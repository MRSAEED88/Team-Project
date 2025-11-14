import users_db

testcase_admin = users_db.add_db((1234,"Admin","admin@kau.edu.sa","12345678","Admin"))
testcase_admin.insertData()
class User :
    def __init__(self,user_id,name,email,membership):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.membership = membership
    def store_data(self):
        user_info=users_db.add_db((self.user_id,self.name,self.email,self.membership))
        user_info.insertData()


    def is_admin(self):
        return self.membership == "Admin"
    def is_student(self):
        return self.membership == "student"
        pass

#-----------------------------------------------------------------------------------------------------------------

class Student:
    def __init__(self, student_id, name, email, program, level):
        self.student_id = student_id
        self.name = name
        self.email = email
        self.program = program
        self.level = level
        self.transcript = []    #the cources student have finshed
        #class Student(User):
        # def __init__(self, user_id, name, email, program, level):
           # super().__init__(user_id, name, email, "student")
           #self.program = program
           #self.level = level
           #self.transcript = []
#______________________________________________________________________________________________________________________________________
    # Connect with data base:
    def connect_db(self):
        super().__init__(user_id, name, email, "student")
        student_info = student_db.add_student(self.program,self.level,self.transcript)
        student_info.insertdata

    def validate_student(self):
        if not self.student_id or not self.name or not self.email:          # checking the inputs ID,NAME,EMAIL
            return False, "All fields are required."
        if self.program not in ["Computer", "Comm", "Power", "Biomedical"]: #Checking the program of student is from this choices
            return False, "Invalid program name."
        if self.level <= 0:
            return False, "Level must be greater than zero."  
        return True, "Student data is valid."
    
     # show academic history
    def view_transcript(self):
        if not self.transcript:                       #if the list of transcript is empty will print (no courses completed yet)
            print("no courses completed yet.")
        else:
            print(f"Transcript for {self.name}:")
            for record in self.transcript:
                print(f"- {record['course_code']}: {record['grade']}")

# When we have finished Courses Class  inshAllah ,we will add 3 methods more wich are (Add,remove,show) courses
