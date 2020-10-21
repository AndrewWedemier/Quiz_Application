import sqlite3
import os


def create_table( dataBaseFileLocation , dbCommandString ):
    conn = sqlite3.connect(dataBaseFileLocation)
    cur = conn.cursor( ) 
    table = 'TABLE'
    tablePos = dbCommandString.find(table)
    startPos = tablePos+len(table) + 1
    endPos=dbCommandString.find(" ",startPos )
    print(dbCommandString[startPos:endPos])
    stringToexecute = 'DROP TABLE IF EXISTS ' + dbCommandString[startPos : endPos] 
    cur.execute(stringToexecute)
    cur.execute(  dbCommandString )
    conn.close()


def create_subject_table( dataBaseFileLocation, dbCommandString ):

    return 0 
    ''' deprecate this function
    def create_list_of_subtopic_table_commands( numberOfTopics ):
        tableNames = []
        commandList = []
        for i in range( 1, numberOfTopics + 1 , 1 ):
            tableNames.append('SubTopic'+str(i) )

        for name in tableNames:
            command = create_subtopic_table_command( name )
            commandList.append(command)

        return commandList
    '''

def create_subtopic_table_command( name ):

    command = 'CREATE TABLE IF NOT EXISTS '+ name +''' ( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        topicNumber INTEGER, fk_prev_topic_id INTEGER, fk_next_topic_id  
        INTEGER, toplevel_topic_id INTEGER,  bottomlevel_topic_id  INTEGER, question_solution INTEGER )'''
    return command

def setup_database(dbLocation):
    command = 'CREATE TABLE IF NOT EXISTS Topic ( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, name TEXT UNIQUE )'
    execute_command(command, dbLocation)

def execute_sql_command( my_command , database ):
    conn = sqlite3.connect(database)
    cur = conn.cursor()
    cur.execute( my_command )
    conn.close()

def generate_insert_commands( table, fields, values) :

    command = 'INSERT INTO '+table+ ' (' 
    for field in fields:
        command = command + field + ','
    command = command[0:-1] + ')'
    command += ' VALUES ' + '('
    for value in values:
        #print("values : {}".format(value))
        if isinstance(value, str)  :
            command += ( '"'+ value + '"' + ',')
        else:
            command +=  str(value) + ','

    command =  command[0:-1] + ')' 
    return command

def generate_fetch_topic_id_sql_commands( table, values) :

    command = 'SELECT id, name FROM '+table+' WHERE (' 
    for value in values:
        command = command + 'name = ' +'"'+ value +'"' +' OR '
    command = command[0:-3] +" )"

    return command


def execute_command( myCommand, dbLocation ):
    conn = sqlite3.connect( dbLocation )
    cur = conn.cursor()
    cur.execute(myCommand)
    conn.commit()
    conn.close()

def fetch_command_results(myCommand, dbLocation ):
    table = []
    conn = sqlite3.connect( dbLocation )
    cur = conn.cursor()
    try:
        cur.execute( myCommand )
        for row in cur:
            table.append(row)
    except:
        print("Error while tying to execute {}".format(myCommand))
    
    conn.close()
    return table

def create_table_and_insert_subtopic( tableOneData, dbLocation ):
    ''' @params tableOneData: A list containing  [ ( tableNames ), (tableColumns), (tableColumnsValues)]
        @params dbLocation: a string containing the full path  of the database
    '''
    tableName = tableOneData[0]
    command = create_subtopic_table_command( tableName )
    execute_command( command, dbLocation )
    tableName , tableFields, tableValues = tableOneData
    command = generate_insert_commands( tableName, tableFields, tableValues )
    execute_command(command, dbLocation)

def create_and_insert_into_question_solution_table( dbLocation, values ):
    ''' @params: dbLocation - Location of database
        @params: values ["/full/file/path/to/question/or/solution", display_number_of_row_pixels,
         display_number_of_column pixels, question_or_solution, question_difficulty ]
        - full string path to the question or solution'''

    myCommand = '''CREATE TABLE IF NOT EXISTS questions_and_solutions 
             (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
             file_location TEXT UNIQUE, row_pixels_property INTEGER, column_pixels_property INTEGER,
             question_or_solution INTEGER, question_difficutly TEXT )'''
    execute_command(myCommand, dbLocation)
    
    myCommand = '''INSERT INTO questions_and_solutions ( file_location, row_pixels_property, column_pixels_property, 
        question_or_solution, question_difficutly ) VALUES ''' +  '''( 
        ''' + "'"+ values[0] +"'"+ ", " + str(values[1]) + ", " + str(values[2]) +", " + str(values[3]) + "," + "'"+ values[4] + "'" + " )"

    execute_command(myCommand, dbLocation )


def create_questions_database(dbLocation, questionsToInsert ):
    '''
    @param dbLoction: String
    @param questionsToInsert: dictionary 
    @return: List of questions with primary_keys created
    '''
    connect = sqlite3.connect(dbLocation)
    cursor = connect.cursor()
    myCommand = '''CREATE TABLE IF NOT EXISTS Questions( 
        id INTEGER NOT NULL PRIMARY KEY  AUTOINCREMENT UNIQUE,
        full_path TEXT,
        file_name TEXT,
        number_of_horizontal_pixels INTEGER,
        number_of_vertical_pixels INTEGER,
        question_difficulty TEXT )
        '''
    cursor.execute(myCommand)

    for key in questionsToInsert:       
        cursor.execute( ''' INSERT INTO Questions 
                    (
                    file_name,
                    full_path,
                    number_of_horizontal_pixels,
                    number_of_vertical_pixels,
                    question_difficulty ) 
                    VALUES (?, ?, ?, ?, ?)''',  
                   ( questionsToInsert[key][0],
                    key,
                    questionsToInsert[key][1],
                    questionsToInsert[key][2],
                    questionsToInsert[key][3] ) )

    connect.commit()

    cursor.execute("SELECT id, full_path FROM Questions ")
    questionPrimaryKeydict = {}
    for cur in cursor:
        questionPrimaryKeydict[ cur[1] ] = questionPrimaryKeydict.get( cur[1], cur[0] )
    
    return questionPrimaryKeydict



def crawl_and_update_database(dbLocation, startSearchPath):
    topicsList = set()
    subTopics = []
    commandList = []
    filesDict = {}
    tables = {}
    pathSplit = startSearchPath.split('/')
    subjectsDict = {}
    subTopicsDict = {}
    questionsDict = {}
    solutionsDict = {}
    responsesDict = {}
    matchedQuestionsAndSolutionsDict = {}
    unmatchedQuestionsAndSolutionsDict = {}
    matchedQuestionsAndResponsesDict = {}
    unmatchedQuestionsAndResponsesDict = {}
    depthCount = 0

    for root, folders, files in os.walk(startSearchPath) :
        #print("")
        #print("root: {}".format( root ) )
        #print("folders: {}".format( folders ) )
        #print("files: {}".format( files ) )
        rootSplit = root.split('/')
        filePathWithrootRemoved = [level for level in rootSplit if level not in 
                                            (pathSplit+['Questions', 'Solutions']) ]
        for file in files:
            if "ignore" not in folders:
                for topic in filePathWithrootRemoved: 
                    if len(filePathWithrootRemoved) > 1 and depthCount == 0:
                        subjectsDict[ topic ] = subjectsDict.get( topic ,
                        [] ) + [ [ os.path.join(root, file), filePathWithrootRemoved[depthCount + 1] ] ]
                    else:
                        if  depthCount == len(filePathWithrootRemoved) - 1 :
                            subTopicsDict[ topic ] = subTopicsDict.get(
                                    topic, []  ) + [ [ [ os.path.join(root, file), "N/A"] ] ]

                        else:
                            if len(filePathWithrootRemoved) > 1:
                                subTopicsDict[ topic ] = subTopicsDict.get(
                                        topic , [] ) + [ [ os.path.join(root, file), 
                                            filePathWithrootRemoved[depthCount + 1] ] ]                            
                    depthCount += 1
            
                depthCount = 0
                qkey = os.path.join( root, file )
                #start=root.find("Questions")
                #print(start)
                questionsInstance = root.rfind("Questions")
                skey = os.path.join( qkey[:questionsInstance],"Solutions",file)
                rkey = os.path.join( qkey[:questionsInstance], "Responses", file )
                questionsDict[qkey] = questionsDict.get(qkey, [file, 720 , 480, "Medium" ])
                
                if os.path.isfile(skey):
                    matchedQuestionsAndSolutionsDict[qkey] = matchedQuestionsAndSolutionsDict.get( qkey, skey)
                    solutionsDict[skey] = solutionsDict.get(skey, [file, 720, 480])
                else:
                    unmatchedQuestionsAndSolutionsDict[qkey] = unmatchedQuestionsAndSolutionsDict.get( qkey, skey ) 

                if os.path.isfile(rkey):
                     matchedQuestionsAndResponsesDict[qkey] = matchedQuestionsAndResponsesDict.get( qkey, rkey )
                     responsesDict[rkey] = responsesDict.get(rkey,[file, 720, 480] )
                else:
                    unmatchedQuestionsAndResponsesDict[qkey] = unmatchedQuestionsAndResponsesDict.get( qkey,  rkey ) 


            else:
                pass

    for x in subTopicsDict:
        print( "SUBTOPIC: {}  QUESTION: {}".format(x ,subTopicsDict[x] ), "\n")

    for x in subjectsDict:
        print( "SUBJECT: {}   QUESTION: {}".format(x, subjectsDict[x] ), "\n")

    for x in questionsDict:
        print( "Questions table: {}".format(x), questionsDict[x], "\n" )
    
    for x in matchedQuestionsAndSolutionsDict:
        print( "QUESTION: {} SOLUTION: {}".format(x, matchedQuestionsAndSolutionsDict[x] ), "\n" )

    for x in unmatchedQuestionsAndSolutionsDict:
        print( "QUESTION WITH NO FOUND SOLUTION: {}".format(x), "\n" )    
            #older implemtnations starts here  

    result = create_questions_database(dbLocation, questionsDict ) 
    print( "The results are: {}".format(result) )


if __name__ == '__main__' :
    dbLocation = r'/media/andrew/Hummingbird_AI/Questions_and_Answers/QuestionsAndSolutions'
    crawlPath = '/media/andrew/Hummingbird_AI/Questions_and_Answers'
    linkStart = {}

    #setup_database( dbLocation )
    #print( dir(os) )
    #crawl_and_update_database()
    crawl_and_update_database(dbLocation, crawlPath )
    #command =generate_insert_commands("subTopic1", [ 'fk_prev_topic_id', 'fk_next_subtopic_id'], [1, 4])
    #execute_command(command, dbLocation)


    print(linkStart)