from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import sqlite3



class GUI(Tk):
    """ Creation of a tool to help me remember all the info from my various
        courses"""
    
    def __init__(self, myTitle):
        """ creating basic layout of quiz app"""
        Tk.__init__(self)
        #Without it, each of your menus (on Windows and X11) will start with what looks like a dashed line and allows you to "tear off" the menu
        self.option_add('*tearOff', FALSE) 
        main_menu = Menu(self)
        self['menu'] = main_menu #self.config(menu=main_menu)
        self.title(myTitle)
        
        
        file_menu = Menu(main_menu)
        main_menu.add_cascade(label ="File", menu=file_menu, command=doNothing)
        file_menu.add_command(label="New Quiz", command=self.new_quiz )
        edit_menu = Menu(main_menu)
        main_menu.add_cascade(label='Edit',  menu=edit_menu, command=doNothing)
        quiz_options = Menu(main_menu)
        
        main_menu.add_cascade(label='Quiz Options', menu=quiz_options)
        subjects = Menu(quiz_options)
        quiz_options.add_cascade(label ='Subjects', menu=subjects)
        quiz_options.add_command(label='Number of Questions')
        #self.createCanvas()

        self.mainloop()
        self.img = ""
        self.img2 = ""

    def createCanvas(self):

        h = ttk.Scrollbar(self, orient=HORIZONTAL)
        v = ttk.Scrollbar(self, orient=VERTICAL)
        canvas = Canvas(self, scrollregion=(0, 0, 2000, 2000), yscrollcommand=v.set, xscrollcommand=h.set)
        #canvas.create_oval(10,10,100,100, fill='gray90')
        h['command'] =canvas.xview
        v['command'] =canvas.yview
        ttk.Sizegrip(self).grid(column=1, row=1, sticky=(S,E))
        img = '/home/andrew/Pictures/complex_number.png'
        self.img = Image.open(img)
        
        self.img2=ImageTk.PhotoImage(self.img)

        canvas.create_image(800, 650, image=self.img2, anchor=CENTER)
        frm = Frame(canvas, relief=GROOVE, borderwidth=2)
        canvas.create_window(3000, 5000, window=frm, anchor=CENTER)
        canvas.grid(column=0, row=0, sticky=(N,W,E,S))
        h.grid(column=0, row=1, sticky=(W,E))
        v.grid(column=1, row=0, sticky=(N,S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        response1 = Button(canvas, text="A").pack(side=LEFT, fill=X, expand=YES, anchor=SW)
        response2 = Button(canvas, text="B").pack(side=LEFT, fill=X, expand=YES, anchor=SW)
        response3 = Button(canvas, text="C").pack(side=LEFT, fill=X, expand=YES, anchor=SW)

    def new_quiz(self):
        
        quiz_options = Toplevel(self, width= 500, height = 500)
        quiz_options.transient(self)
        frameForLabels = Frame(quiz_options)
        frameForEntry = Frame(quiz_options)
        frameForLabels.pack(side=LEFT, fill=Y, expand=YES)
        frameForEntry.pack(side=LEFT, fill=Y, expand=YES)
        Label(frameForLabels, text="How many questions do you want?").pack(side=TOP, expand=YES, fill=X)
        responseNumQues = IntVar()
        responseNumQues.set("1 to 60.")
        Entry(frameForEntry, textvariable=responseNumQues, width=40).pack(side=TOP, expand=YES, fill=X)      
        #quiz_frame.pack(side=LEFT)


class QuestionDataBase:
    
    def __init__(self):

        self.numberOfCorrectAns = 0
        self.numberOfIncorrectAns = 0
        self.numberOfQuestions = 0
        self.Subjects = list()
        self.Topics = list()
        self.dataBase = dict()

    def add_topic(self, number, topic_name ):
        return 0
    
    def add_subtopic(self, number, topic_name, count ):
        return 0
        
    def add_subject(self, number, subject_name ):
        return 0
    
    def addn_location(self, number, ques_location ):
        return 0
    def add_solution_location(self, number, sol_location ):
        return 0
    def create_data_connection( self ):
        return 0
    def add_question(self, questionNumber ):
        return 0
        self.dataBase[questionNumber] = self.dataBase.get( questionNumber, [ None, None , None , None , None ] )
        add_question_subject( questionNumber, dataBase )
        add_question_topic( questionNumber, dataBase )
        add_question_location( questionNumber, dataBase )



#class Solution(Frame):
#    def __init__(self):

#class Responses(Frame):
#    def __init__(self)


if __name__ == '__main__':
    #Quiz1 = GUI("Hummingmind Quiz Program")\