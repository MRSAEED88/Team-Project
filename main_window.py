from PyQt5.QtWidgets import QMainWindow, QStackedWidget
from student_dashboard import StudentDashboard
from admin_dashboard import AdminDashboard

class MainWindow(QMainWindow):
    def __init__(self, user_id, user_role, user_name):
        super().__init__()
        self.setWindowTitle("Course Registration System")
        self.resize(900, 600)

        self.user_id = user_id
        self.user_role = user_role
        self.user_name = user_name

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.student_dashboard = StudentDashboard(self.user_id)
        self.admin_dashboard = AdminDashboard()

        if self.user_role == "student":
            self.stack.addWidget(self.student_dashboard)
            self.stack.setCurrentWidget(self.student_dashboard)
        else:
            self.stack.addWidget(self.admin_dashboard)
            self.stack.setCurrentWidget(self.admin_dashboard)
