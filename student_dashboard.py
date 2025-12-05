import sqlite3
from PyQt5.QtWidgets import QMainWindow
# Import the UI class from your generated file
from studentdashboardUi_ import Ui_StudentDashboard 

class StudentDashboard(QMainWindow, Ui_StudentDashboard):
    def __init__(self, user_id):
        super().__init__()
        # This sets up the UI defined in studentdashboardUi_.py
        self.setupUi(self) 
        
        self.user_id = user_id
        self.load_student_data()
        
        # Connect buttons (Example)
        # self.registerButton.clicked.connect(self.register_course)

    def load_student_data(self):
        # Ensure User.db exists and has the correct schema
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            # Assuming your table has these columns. Adjust if necessary.
            cur.execute("SELECT name, email, program, level FROM users WHERE id=?", (self.user_id,))
            student = cur.fetchone()
            con.close()

            if student is None:
                self.studentName.setText("Student Name: Unknown")
                return

            name, email, program, level = student

            # Update the labels defined in studentdashboardUi_.py
            self.studentName.setText(f"Student Name: {name}")
            # You need to add an ID label to your DB logic if you want to show it
            self.studentID.setText(f"Student ID: {self.user_id}") 
            self.studentMajor.setText(f"Major: {program}")
            
            # Note: You have email and level in DB, but not in the UI file provided.
            # You can add them to the UI or ignore them.

        except Exception as e:
            print(f"Database Error: {e}")
            self.studentName.setText("Database Error")
