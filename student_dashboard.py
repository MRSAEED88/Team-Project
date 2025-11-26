from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton

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
