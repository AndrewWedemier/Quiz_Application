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



def crawl_and_update_database(dbLocation, startSearchPath):
    topicsList = set()
    subTopics = []
    commandList = []
    filesDict = {}
    tables = {}
    pathSplit = startSearchPath.split('/')

    for root, folders, files in os.walk(startSearchPath) :
        if  files: 
            filesDict[root] = filesDict.get( root, files )
            rootSplit = root.split('/')
            for topic in rootSplit:
                if topic not in pathSplit:
                    topicsList.add(topic)


    for topic in topicsList:
        if topic not in set( ('Solutions', 'Questions')) :
            command = generate_insert_commands('Topic',['name'],[topic] )
            commandList.append(command)
    
    setup_database(dbLocation)
    for myCommand in commandList:
        execute_command( myCommand, dbLocation )

    myCommand= generate_fetch_topic_id_sql_commands('Topic', topicsList )
    results = fetch_command_results(myCommand, dbLocation)
    myLookup = { key:value for (value, key) in results }
    
    for key in filesDict:
        directoryLength = len( pathSplit )
        filePathLength = len( key.split( '/' ) )
        
        startPos = filePathLength - directoryLength -1
        endPos = filePathLength
        tableValues = []
        if startPos > 0:
            #= key[startPos]
            tableColumns = ['topicNumber', 'fk_prev_topic_id', 'fk_next_topic_id',
                'toplevel_topic_id',  'bottomlevel_topic_id', 'question_solution' ]
            heading = key.split('/')
            topLevelTopic = heading[startPos]
            bottomLevelTopic = heading[-2]
            questionOrSolution = heading[-1]
            if questionOrSolution =='Questions':
                questionOrSolutionFolder = 1
            else:
                questionOrSolutionFolder = 2

            for idx, value in enumerate( heading[startPos:-1] ):
                if idx > 0 and idx < len( heading[startPos:] ) -2 :
                    create_table_and_insert_subtopic( 
                        [ 'subTopic'+str( idx+1 ) , tableColumns,
                            [ myLookup[value], myLookup[ heading[ startPos + idx -1 ] ], 
                            myLookup[ heading[ startPos+ idx + 1] ], myLookup[ topLevelTopic ],
                            myLookup[bottomLevelTopic], questionOrSolutionFolder ]  ] , dbLocation  )                    
                else:
                    if idx == 0:
                        create_table_and_insert_subtopic( 
                            [ 'subTopic'+str( idx+1 ) , tableColumns,
                             [ myLookup[value], myLookup[value], 
                             myLookup[ heading[ startPos+ idx + 1] ], myLookup[ topLevelTopic ],
                              myLookup[bottomLevelTopic], questionOrSolutionFolder ]  ] , dbLocation  )
                    else:
                        create_table_and_insert_subtopic( 
                            [ 'subTopic'+str( idx+1 ) , tableColumns,
                             [ myLookup[value],  myLookup[ heading[ startPos + idx -1 ] ], 
                             myLookup[  bottomLevelTopic ], myLookup[ topLevelTopic ],
                              myLookup[bottomLevelTopic], questionOrSolutionFolder ]  ] , dbLocation  )                        
                        

                    


            #create_table_and_insert_subtopic( )

    #print(pathSplit)
    
    #print(filesDict)

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