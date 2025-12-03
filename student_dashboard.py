import sqlite3
from PyQt5.QtWidgets import QMainWindow

class StudentDashboard(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)

        self.user_id = user_id
        self.load_student_data()

    def load_student_data(self):
        con = sqlite3.connect("User.db")
        cur = con.cursor()

        cur.execute("SELECT id, name, email, program, level FROM users WHERE id=?", (self.user_id,))
        student = cur.fetchone()

        con.close()

        if student is None:
            self.student_name_label.setText("Unknown")
            return

        _, name, email, program, level = student

        self.student_name_label.setText(f"Name: {name}")
        self.student_email_label.setText(f"Email: {email}")
        self.student_program_label.setText(f"Program: {program}")
        self.student_level_label.setText(f"Level: {level}")


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
