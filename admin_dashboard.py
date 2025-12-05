import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QStackedWidget, 
                             QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFormLayout, QLineEdit, QMessageBox, QComboBox, QSpinBox, QCheckBox)
from PyQt5.QtCore import Qt

from Admin import Admin

class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("KAU Admin Dashboard")
        self.resize(1100, 700)
        self.user_id = user_id

        # Admin logic class
        self.admin_logic = Admin(user_id, "Admin", "admin@kau.edu.sa", "pass")

        # Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()

        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        self.setup_student_page()
        self.setup_course_page()

        self.load_students()
        self.load_courses()

    # ---------------- Sidebar ----------------
    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(220)
        self.sidebar.setStyleSheet("background-color: #2c3e50; color: white;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)

        self.lbl_title = QLabel("Admin Panel")
        self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px; color: #ecf0f1;")
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.lbl_title)

        self.btn_students = self.create_nav_button("Manage Students")
        self.btn_courses = self.create_nav_button("Manage Courses")
        self.btn_logout = self.create_nav_button("Log Out")

        self.sidebar_layout.addStretch()

        self.btn_students.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_students))
        self.btn_courses.clicked.connect(lambda: self.content_area.setCurrentWidget(self.page_courses))
        self.btn_logout.clicked.connect(self.close)

        self.main_layout.addWidget(self.sidebar)

    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton { 
                text-align: left; padding: 12px; border: none; 
                background: none; color: #bdc3c7; font-size: 15px; 
            }
            QPushButton:hover { background-color: #34495e; color: white; }
        """)
        self.sidebar_layout.addWidget(btn)
        return btn

    # ---------------- STUDENTS PAGE ----------------
    def setup_student_page(self):
        self.page_students = QWidget()
        layout = QVBoxLayout(self.page_students)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QLabel("Student Management")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Program", "Level"])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.student_table)

        btn_layout = QHBoxLayout()
        self.btn_refresh_students = QPushButton("Refresh List")
        self.btn_delete_student = QPushButton("Delete Selected Student")
        self.btn_delete_student.setStyleSheet("background-color: #c0392b; color: white; padding: 8px;")
        
        btn_layout.addWidget(self.btn_refresh_students)
        btn_layout.addWidget(self.btn_delete_student)
        layout.addLayout(btn_layout)

        self.btn_refresh_students.clicked.connect(self.load_students)
        self.btn_delete_student.clicked.connect(self.delete_selected_student)
        
        self.content_area.addWidget(self.page_students)

    def load_students(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT id, name, email, program, level FROM users WHERE membership='student'")
            rows = cur.fetchall()
            con.close()

            self.student_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.student_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        except Exception as e:
            print(f"Error loading students: {e}")

    def delete_selected_student(self):
        row = self.student_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a student to delete.")
            return

        student_id = self.student_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm", f"Delete student {student_id}?", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_student(student_id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_students()
            else:
                QMessageBox.warning(self, "Error", msg)

    # ---------------- COURSES PAGE ----------------
    def setup_course_page(self):
        self.page_courses = QWidget()
        layout = QVBoxLayout(self.page_courses)
        layout.setContentsMargins(20, 20, 20, 20)

        layout.addWidget(QLabel("Existing Courses", styleSheet="font-size: 18px; font-weight: bold;"))
        
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels(["Code", "Name", "Credits", "Day", "Start", "End", "Room", "Cap"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_table.setFixedHeight(250)
        layout.addWidget(self.course_table)

        # -------- FORM --------
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #f0f2f5; border-radius: 10px; padding: 10px;")
        form_layout = QVBoxLayout(form_frame)

        form_layout.addWidget(QLabel("Add New Course", styleSheet="font-size: 16px; font-weight: bold; color: #27ae60;"))

        grid = QHBoxLayout()

        self.inp_code = QLineEdit(); self.inp_code.setPlaceholderText("Code (e.g. EE201)")
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("Course Name")
        self.inp_credits = QSpinBox(); self.inp_credits.setRange(1, 6)

        # Day checkboxes
        self.day_container = QWidget()
        self.day_layout = QHBoxLayout(self.day_container)
        self.day_layout.setContentsMargins(0,0,0,0)
        self.day_checkboxes = []
        for d in ["Sun", "Mon", "Tue", "Wed", "Thu"]:
            chk = QCheckBox(d)
            self.day_checkboxes.append(chk)
            self.day_layout.addWidget(chk)

        self.inp_start = QSpinBox(); self.inp_start.setRange(8, 20); self.inp_start.setSuffix(":00")
        self.inp_end = QSpinBox(); self.inp_end.setRange(9, 21); self.inp_end.setSuffix(":00")

        self.inp_room = QLineEdit(); self.inp_room.setPlaceholderText("Room")
        self.inp_cap = QSpinBox(); self.inp_cap.setRange(10, 100); self.inp_cap.setValue(30)

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Code:")); col1.addWidget(self.inp_code)
        col1.addWidget(QLabel("Name:")); col1.addWidget(self.inp_name)
        col1.addWidget(QLabel("Credits:")); col1.addWidget(self.inp_credits)

        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Day:")); col2.addWidget(self.day_container)
        col2.addWidget(QLabel("Start:")); col2.addWidget(self.inp_start)
        col2.addWidget(QLabel("End:")); col2.addWidget(self.inp_end)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Room:")); col3.addWidget(self.inp_room)
        col3.addWidget(QLabel("Capacity:")); col3.addWidget(self.inp_cap)

        grid.addLayout(col1)
        grid.addLayout(col2)
        grid.addLayout(col3)
        form_layout.addLayout(grid)

        self.btn_add_course = QPushButton("Add Course")
        self.btn_add_course.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        self.btn_add_course.clicked.connect(self.add_course)
        form_layout.addWidget(self.btn_add_course)

        # ========== NEW BUTTON: DELETE COURSE ==========
        self.btn_delete_course = QPushButton("Delete Selected Course")
        self.btn_delete_course.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; padding: 10px;")
        self.btn_delete_course.clicked.connect(self.delete_selected_course)
        form_layout.addWidget(self.btn_delete_course)
        # =================================================

        layout.addWidget(form_frame)
        self.content_area.addWidget(self.page_courses)

    # -------- LOAD COURSES --------
    def load_courses(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT course_code, course_name, credits, day, start_time, end_time, room, max_capacity FROM courses")
            rows = cur.fetchall()
            con.close()

            self.course_table.setRowCount(0)
            for row_idx, row_data in enumerate(rows):
                self.course_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.course_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        except Exception as e:
            print(f"Error loading courses: {e}")

    # -------- ADD COURSE --------
    def add_course(self):
        code = self.inp_code.text()
        name = self.inp_name.text()
        credits = self.inp_credits.value()

        selected_days = [chk.text() for chk in self.day_checkboxes if chk.isChecked()]
        if not selected_days:
            QMessageBox.warning(self, "Error", "Select at least one day.")
            return

        day = ",".join(selected_days)

        start = str(self.inp_start.value()) + ":00"
        end = str(self.inp_end.value()) + ":00"
        room = self.inp_room.text()
        cap = self.inp_cap.value()

        success, msg = self.admin_logic.add_course(code, name, credits, day, start, end, room, cap, [])
        
        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_courses()
            self.inp_code.clear()
            self.inp_name.clear()
            for chk in self.day_checkboxes:
                chk.setChecked(False)
        else:
            QMessageBox.warning(self, "Error", msg)

    # -------- DELETE COURSE --------
    def delete_selected_course(self):
        row = self.course_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Select a course to delete.")
            return

        course_code = self.course_table.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete course '{course_code}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_course(course_code)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses()
            else:
                QMessageBox.warning(self, "Error", msg)


    def add_student(self):
        student_id = self.inp_s_id.text()
        name = self.inp_s_name.text()
        email = self.inp_s_email.text()
        program = self.inp_s_program.currentText()
        level = self.inp_s_level.value()
        password = self.inp_s_password.text()

        if not (student_id and name and email and password):
            QMessageBox.warning(self, "Error", "Please fill all fields.")
            return

        success, msg = self.admin_logic.add_student(student_id, name, email, program, level, password)

        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_students()

            # Clear inputs
            self.inp_s_id.clear()
            self.inp_s_name.clear()
            self.inp_s_email.clear()
            self.inp_s_password.clear()
        else:
            QMessageBox.warning(self, "Error", msg)
