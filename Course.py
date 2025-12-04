from User import User
import users_db

class Student(User):
    def __init__(self, user_id :int , name : str, email :str , program : str, level : int, password :str,):
        super().__init__(user_id, name, email, password, membership="student")

        self.program = program
        self.level = level
        self.transcript = self.load_transcript()
#______________________________________________________________________________________________________________________________________
    # Connect with data base:
    def store_data(self):
        student_info = users_db.student_db(self.user_id, self.name, self.email,
                                             self.program, self.level)
        student_info.insertData()
#_______________________________________________________________________________________________________________________________________
    def validate_student(self):
        if not self.user_id or not self.name or not self.email:          # checking the inputs ID,NAME,EMAIL
            return False, "All fields are required."
        if self.program not in ["Computer", "Comm", "Power", "Biomedical"]: #Checking the program of student is from this choices
            return False, "Invalid program name."
        if self.level <= 0:
            return False, "Level must be greater than zero."  
        return True, "Student data is valid."
    
    def load_transcript(self):
        """Loads the student's completed courses from the database."""
        # calls the function you already wrote in users_db.py
        return users_db.get_completed_courses(self.user_id)

    def get_completed_credits(self):
        """Calculates the total credits for completed courses from the transcript."""
        total_credits = 0
        # This requires a database call to join transcript, courses tables
        # and sum the credits.
        # for course_record in self.transcript:
        #     total_credits += users_db.get_course_credits(course_record['course_code'])
        return total_credits

     # show academic history
    def view_transcript(self):
        if not self.transcript:                       #if the list of transcript is empty will print (no courses completed yet)
            print("no courses completed yet.")
        else:
            print(f"Transcript for {self.name}:")
            for record in self.transcript:
                print(f"- {record['course_code']}: {record['grade']}")
