from User import User

class Student(User):
    def __init__(self, user_id :int , name : str, email :str , program : str, level : int, password :str,):
        super().__init__(user_id, name, email, password, membership="student")

        self.program = program
        self.level = level
        self.transcript = []
#______________________________________________________________________________________________________________________________________
    # Connect with data base:
   def store_data(self):
        student_info = users_db.student_db(self.user_id, self.name, self.email,
                                             self.program, self.level, str(self.transcript))
        student_info.insertData()
#_______________________________________________________________________________________________________________________________________
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
