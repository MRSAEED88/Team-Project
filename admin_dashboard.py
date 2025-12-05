from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QStackedWidget, QFrame)
from PyQt5.QtCore import Qt

class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.resize(900, 600)
        self.user_id = user_id

        # --- Main Layout Setup ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- Sidebar (Left) ---
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        
        self.lbl_title = QLabel("Admin Panel")
        self.lbl_title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.sidebar_layout.addWidget(self.lbl_title)

        # Menu Buttons
        self.btn_students = QPushButton("Manage Students")
        self.btn_courses = QPushButton("Manage Courses")
        self.btn_logout = QPushButton("Log Out")
        
        # Style sidebar buttons
        for btn in [self.btn_students, self.btn_courses, self.btn_logout]:
            btn.setStyleSheet("""
                QPushButton { text-align: left; padding: 10px; border: none; background: none; color: white; font-size: 14px; }
                QPushButton:hover { background-color: #34495e; }
            """)
            self.sidebar_layout.addWidget(btn)

        self.sidebar_layout.addStretch()
        self.main_layout.addWidget(self.sidebar)

        # --- Content Area (Right) ---
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        # Page 1: Students
        self.page_students = QWidget()
        student_layout = QVBoxLayout(self.page_students)
        student_layout.addWidget(QLabel("Student Management Area", styleSheet="font-size: 20px; color: #333;"))
        student_layout.addStretch()
        self.content_area.addWidget(self.page_students)

        # Page 2: Courses
        self.page_courses = QWidget()
        course_layout = QVBoxLayout(self.page_courses)
        course_layout.addWidget(QLabel("Course Management Area", styleSheet="font-size: 20px; color: #333;"))
        course_layout.addStretch()
        self.content_area.addWidget(self.page_courses)

        # --- Connect Buttons ---
        self.btn_students.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_students))
        self.btn_courses.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_courses))
        self.btn_logout.clicked.connect(self.close)
