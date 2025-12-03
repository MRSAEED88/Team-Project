from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton


# import sqlite3
# from PyQt5.QtWidgets import QMainWindow

# class StudentDashboard(QMainWindow):
#     def __init__(self, user_id):
#         super().__init__()
#         self.setupUi(self)

#         # Save user id
#         self.user_id = user_id

#         # Load student data from database
#         self.load_student_data()

#     def load_student_data(self):
#         # 1) Connect to database
#         con = sqlite3.connect("User.db")
#         cur = con.cursor()

#         # 2) Get student info by ID
#         cur.execute("SELECT * FROM students WHERE ID=?", (self.user_id,))
#         student = cur.fetchone()

#         # 3) Close database
#         con.close()

#         if student is None:
#             # If student is not found (should not happen)
#             self.student_name_label.setText("Unknown Student")
#             return

#         # 4) Extract student data
#         student_id = student[0]
#         name = student[1]
#         email = student[2]
#         program = student[3]
#         level = student[4]

#         # 5) Display on UI labels
#         self.student_name_label.setText(f"Name: {name}")
#         self.student_email_label.setText(f"Email: {email}")
#         self.student_program_label.setText(f"Program: {program}")
#         self.student_level_label.setText(f"Level: {level}")
 # ---- DATABASE CONNECTION ----
        # self.load_student_info()
        # self.load_registered_courses()
        # self.load_available_courses()

        # # Button: Register into selected course
        # self.register_button.clicked.connect(self.register_selected_course)

class StudentDashboard(QWidget):
    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id

        layout = QVBoxLayout()

        self.welcome_label = QLabel("Welcome Student")
        layout.addWidget(self.welcome_label)

        self.registered_label = QLabel("Registered Courses")
        layout.addWidget(self.registered_label)

        self.registered_list = QListWidget()
        self.registered_list.addItem("No registered courses yet")
        layout.addWidget(self.registered_list)

        self.available_label = QLabel("Available Courses")
        layout.addWidget(self.available_label)

        self.available_list = QListWidget()
        self.available_list.addItem("Course 1")
        self.available_list.addItem("Course 2")
        self.available_list.addItem("Course 3")
        layout.addWidget(self.available_list)

        self.register_button = QPushButton("Register")
        layout.addWidget(self.register_button)

        self.setLayout(layout)
