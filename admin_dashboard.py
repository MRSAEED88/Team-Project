import sys
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
                             QLineEdit, QAbstractItemView, QMessageBox, QComboBox, 
                             QSpinBox, QFormLayout, QCheckBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- IMPORT ADMIN LOGIC ---
from Admin import Admin

class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("KAU Admin Portal | Fall 2025")
        self.resize(1300, 800)
        
        # 1. Initialize Admin Logic
        self.admin_logic = Admin(user_id, "Admin", "admin@kau.edu.sa", "pass")

        # 2. Apply Professional Styles
        self.setup_styles()

        # 3. Setup Layouts
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 4. Build UI Components
        self.setup_sidebar()
        
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        # 5. Create Pages
        self.create_dashboard_page()   # Index 0
        self.create_students_page()    # Index 1
        self.create_courses_page()     # Index 2
        self.create_plans_page()       # Index 3

        # 6. Initial Data Load
        self.load_dashboard_stats()
        self.load_students()
        self.load_courses()
        self.load_plans()

        # Default Page
        self.nav_dashboard.setChecked(True)
        self.content_area.setCurrentIndex(0)

    # =======================================================
    # STYLE SHEET
    # =======================================================
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f6f9; }
            QFrame#Sidebar { background-color: #2c3e50; color: white; border: none; }
            QLabel#LogoLabel { font-size: 22px; font-weight: bold; color: #ecf0f1; padding: 20px; }
            QPushButton[class="nav-btn"] {
                background-color: transparent; border: none; color: #bdc3c7;
                text-align: left; padding: 15px 25px; font-size: 14px;
                border-left: 4px solid transparent;
            }
            QPushButton[class="nav-btn"]:hover { background-color: #34495e; color: white; }
            QPushButton[class="nav-btn"]:checked { background-color: #34495e; color: white; border-left: 4px solid #3498db; }
            QLabel[class="page-title"] { font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            QLabel[class="section-title"] { font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 10px; }
            QFrame[class="card"] { background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; }
            QTableWidget { background-color: white; border: 1px solid #dcdcdc; gridline-color: #ecf0f1; font-size: 13px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 8px; border: none; font-weight: bold; color: #2c3e50; }
            QLineEdit, QComboBox, QSpinBox { padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background: white; }
            QPushButton[class="action-btn"] { background-color: #2980b9; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="action-btn"]:hover { background-color: #3498db; }
            QPushButton[class="success-btn"] { background-color: #27ae60; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="success-btn"]:hover { background-color: #2ecc71; }
            QPushButton[class="danger-btn"] { background-color: #c0392b; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="danger-btn"]:hover { background-color: #e74c3c; }
        """)

    # =======================================================
    # SIDEBAR
    # =======================================================
    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        logo = QLabel("Admin Portal")
        logo.setObjectName("LogoLabel")
        layout.addWidget(logo)

        # Nav Buttons
        self.nav_dashboard = self.create_nav_button("Dashboard Overview")
        self.nav_students = self.create_nav_button("Manage Students")
        self.nav_courses = self.create_nav_button("Manage Courses")
        self.nav_plans = self.create_nav_button("Manage Plans")
        
        layout.addWidget(self.nav_dashboard)
        layout.addWidget(self.nav_students)
        layout.addWidget(self.nav_courses)
        layout.addWidget(self.nav_plans)

        layout.addStretch()

        self.btn_logout = self.create_nav_button("Log Out")
        self.btn_logout.clicked.connect(self.close)
        layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(self.sidebar)

        # Connect Navigation
        self.nav_dashboard.clicked.connect(lambda: self.switch_page(0, self.nav_dashboard))
        self.nav_students.clicked.connect(lambda: self.switch_page(1, self.nav_students))
        self.nav_courses.clicked.connect(lambda: self.switch_page(2, self.nav_courses))
        self.nav_plans.clicked.connect(lambda: self.switch_page(3, self.nav_plans))

    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setProperty("class", "nav-btn")
        return btn

    def switch_page(self, index, btn_sender):
        self.content_area.setCurrentIndex(index)
        btn_sender.setChecked(True)

    # =======================================================
    # PAGE 1: OVERVIEW
    # =======================================================
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("System Overview")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        self.card_students = self.create_info_card("Total Students", "Loading...", "#2980b9")
        self.card_courses = self.create_info_card("Active Courses", "Loading...", "#27ae60")
        
        cards_layout.addWidget(self.card_students)
        cards_layout.addWidget(self.card_courses)
        cards_layout.addStretch()
        
        layout.addLayout(cards_layout)
        layout.addStretch()
        self.content_area.addWidget(page)

    def create_info_card(self, title, value, color):
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(f"border-top: 4px solid {color}; background: white; border-radius: 8px;")
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)
        
        t = QLabel(title)
        v = QLabel(value)
        v.setStyleSheet("color: #2c3e50; font-size: 28px; font-weight: bold;")
        
        l.addWidget(t)
        l.addWidget(v)
        return card

    # =======================================================
    # PAGE 2: MANAGE STUDENTS
    # =======================================================
    def create_students_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header = QHBoxLayout()
        title = QLabel("Student Management")
        title.setProperty("class", "page-title")
        header.addWidget(title)
        header.addStretch()

        btn_refresh = QPushButton("Refresh List")
        btn_refresh.setProperty("class", "action-btn")
        btn_refresh.clicked.connect(self.load_students)
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Program", "Level"])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.student_table)

        # Add Student Form
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QFormLayout(form_frame)

        lbl_form = QLabel("Add New Student")
        lbl_form.setProperty("class", "section-title")
        form_layout.addRow(lbl_form)

        self.inp_s_id = QLineEdit()
        self.inp_s_id.setPlaceholderText("e.g. 2241234")

        self.inp_s_name = QLineEdit()
        self.inp_s_name.setPlaceholderText("Full Name")

        self.inp_s_email = QLineEdit()
        self.inp_s_email.setPlaceholderText("student@kau.edu.sa")

        self.inp_s_program = QComboBox()
        self.inp_s_program.addItems(["Computer", "Communications", "Power", "Biomedical"])

        self.inp_s_level = QSpinBox()
        self.inp_s_level.setRange(1, 10)

        # --- ADD PASSWORD FIELD HERE ---
        self.inp_s_password = QLineEdit()
        self.inp_s_password.setEchoMode(QLineEdit.Password)
        self.inp_s_password.setPlaceholderText("Enter password for student")

        form_layout.addRow("Student ID:", self.inp_s_id)
        form_layout.addRow("Name:", self.inp_s_name)
        form_layout.addRow("Email:", self.inp_s_email)
        form_layout.addRow("Program:", self.inp_s_program)
        form_layout.addRow("Level:", self.inp_s_level)
        form_layout.addRow("Password:", self.inp_s_password)

        self.btn_add_student = QPushButton("Add Student")
        self.btn_add_student.setProperty("class", "success-btn")
        self.btn_add_student.clicked.connect(self.handle_add_student)
        form_layout.addRow(self.btn_add_student)

        layout.addWidget(form_frame)
        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 3: MANAGE COURSES
    # =======================================================
    def create_courses_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Course Management")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels(
            ["Code", "Name", "Credits", "Day", "Start", "End", "Room", "Cap"]
        )
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.course_table)

        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        f = QVBoxLayout(form_frame)

        lbl_add = QLabel("Add New Course")
        lbl_add.setProperty("class", "section-title")
        f.addWidget(lbl_add)

        grid = QHBoxLayout()

        # Column 1
        col1 = QVBoxLayout()
        self.inp_code = QLineEdit()
        self.inp_name = QLineEdit()
        self.inp_credits = QSpinBox()
        self.inp_credits.setRange(1, 6)
        col1.addWidget(QLabel("Details"))
        col1.addWidget(self.inp_code)
        col1.addWidget(self.inp_name)
        col1.addWidget(self.inp_credits)

        # Column 2
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Schedule (Select Days)"))

        days_layout = QHBoxLayout()
        self.day_checkboxes = []
        days_list = ["Sun", "Mon", "Tue", "Wed", "Thu"]
        for d in days_list:
            cb = QCheckBox(d)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)
        col2.addLayout(days_layout)

        self.inp_start = QSpinBox()
        self.inp_start.setRange(8, 20)
        self.inp_end = QSpinBox()
        self.inp_end.setRange(9, 21)

        col2.addWidget(self.inp_start)
        col2.addWidget(self.inp_end)

        # Column 3
        col3 = QVBoxLayout()
        self.inp_room = QLineEdit()
        self.inp_cap = QSpinBox()
        self.inp_cap.setRange(10, 100)

        self.btn_add_course = QPushButton("Add Course")
        self.btn_add_course.clicked.connect(self.handle_add_course)

        col3.addWidget(QLabel("Location"))
        col3.addWidget(self.inp_room)
        col3.addWidget(self.inp_cap)
        col3.addWidget(self.btn_add_course)

        grid.addLayout(col1)
        grid.addLayout(col2)
        grid.addLayout(col3)

        f.addLayout(grid)
        layout.addWidget(form_frame)
        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 4: MANAGE PLANS
    # =======================================================
    def create_plans_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Program Plans Management")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        fl = QHBoxLayout(filter_frame)

        self.filter_program = QComboBox()
        self.filter_program.addItems(["Computer", "Comm", "Power", "Biomedical"])
        self.filter_program.currentIndexChanged.connect(self.load_plans)

        fl.addWidget(QLabel("Select Program:"))
        fl.addWidget(self.filter_program)
        fl.addStretch()

        layout.addWidget(filter_frame)

        self.plans_table = QTableWidget()
        self.plans_table.setColumnCount(3)
        self.plans_table.setHorizontalHeaderLabels(["Program", "Level", "Course Code"])
        self.plans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.plans_table)

        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        ff = QHBoxLayout(form_frame)

        self.inp_plan_level = QSpinBox()
        self.inp_plan_level.setRange(1, 10)

        self.combo_plan_course = QComboBox()
        self.load_course_codes_into_combo()

        btn_add_plan = QPushButton("Add to Plan")
        btn_add_plan.clicked.connect(self.handle_add_to_plan)

        btn_del_plan = QPushButton("Remove Selected")
        btn_del_plan.clicked.connect(self.handle_delete_from_plan)

        ff.addWidget(QLabel("Add Course:"))
        ff.addWidget(self.combo_plan_course)
        ff.addWidget(QLabel("Level:"))
        ff.addWidget(self.inp_plan_level)
        ff.addWidget(btn_add_plan)
        ff.addStretch()
        ff.addWidget(btn_del_plan)

        layout.addWidget(form_frame)
        self.content_area.addWidget(page)

    # =======================================================
    # DATA LOADING
    # =======================================================
    def load_dashboard_stats(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("SELECT COUNT(*) FROM students")
            s_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM courses")
            c_count = cur.fetchone()[0]

            con.close()

            self.card_students.layout().itemAt(1).widget().setText(str(s_count))
            self.card_courses.layout().itemAt(1).widget().setText(str(c_count))

        except Exception as e:
            print("Error loading stats:", e)

    def load_students(self):
        self.student_table.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("SELECT id, name, email, program, level FROM students")
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.student_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.student_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

        except Exception as e:
            print("Student Load Error:", e)

    def load_courses(self):
        self.course_table.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("SELECT * FROM courses")
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.course_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.course_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

        except Exception as e:
            print("Course Load Error:", e)

    def load_course_codes_into_combo(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("SELECT course_code FROM courses")
            courses = cur.fetchall()

            self.combo_plan_course.clear()
            for c in courses:
                self.combo_plan_course.addItem(c[0])

            con.close()

        except Exception as e:
            print("Plan Course Load Error:", e)

    def load_plans(self):
        self.plans_table.setRowCount(0)
        prog = self.filter_program.currentText()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute(
                "SELECT program, level, course_code FROM program_plans WHERE program=? ORDER BY level ASC",
                (prog,)
            )
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.plans_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.plans_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

        except Exception as e:
            print("Plan Load Error:", e)

    # =======================================================
    # HANDLERS
    # =======================================================
    def handle_add_student(self):
        student_id = self.inp_s_id.text().strip()
        name = self.inp_s_name.text().strip()
        email = self.inp_s_email.text().strip()
        password = self.inp_s_password.text().strip()
        program = self.inp_s_program.currentText()
        level = self.inp_s_level.value()

        if not student_id or not name or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill ALL fields including password.")
            return

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            # USERS
            cur.execute("""
                INSERT INTO users (id, name, email, password, membership)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, name, email, password, "student"))

            # STUDENTS
            cur.execute("""
                INSERT INTO students (id, name, email, program, level)
                VALUES (?, ?, ?, ?, ?)
            """, (student_id, name, email, program, level))

            con.commit()
            con.close()

            QMessageBox.information(self, "Success", "Student Added Successfully")

            self.load_students()
            self.load_dashboard_stats()

            # Clear inputs
            self.inp_s_id.clear()
            self.inp_s_name.clear()
            self.inp_s_email.clear()
            self.inp_s_password.clear()

        except Exception as e:
            QMessageBox.warning(self, "Database Error", str(e))

    def handle_add_course(self):
        code = self.inp_code.text()
        name = self.inp_name.text()
        credits = self.inp_credits.value()

        days = [cb.text() for cb in self.day_checkboxes if cb.isChecked()]
        if not days:
            QMessageBox.warning(self, "Error", "Please select at least one day.")
            return
        day_str = ", ".join(days)

        start = self.inp_start.value()
        end = self.inp_end.value()
        room = self.inp_room.text()
        cap = self.inp_cap.value()

        success, msg = self.admin_logic.add_course(
            code, name, credits, day_str, start, end, room, cap, []
        )

        if success:
            QMessageBox.information(self, "Success", "Course Added.")
            self.load_courses()
            self.load_course_codes_into_combo()

            self.inp_code.clear()
            self.inp_name.clear()
            self.inp_room.clear()
            for cb in self.day_checkboxes:
                cb.setChecked(False)

        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_delete_course(self):
        row = self.course_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a course first.")
            return

        code = self.course_table.item(row, 0).text()

        confirm = QMessageBox.question(
            self,
            "Confirm",
            f"Delete course {code}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_course(code)

            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses()
                self.load_course_codes_into_combo()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_add_to_plan(self):
        prog = self.filter_program.currentText()
        lvl = self.inp_plan_level.value()
        code = self.combo_plan_course.currentText()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("""
                INSERT INTO program_plans (program, level, course_code)
                VALUES (?, ?, ?)
            """, (prog, lvl, code))

            con.commit()
            con.close()

            QMessageBox.information(self, "Success", f"Added {code} to Level {lvl}")
            self.load_plans()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def handle_delete_from_plan(self):
        row = self.plans_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a row.")
            return

        prog = self.plans_table.item(row, 0).text()
        lvl = self.plans_table.item(row, 1).text()
        code = self.plans_table.item(row, 2).text()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("""
                DELETE FROM program_plans WHERE program=? AND level=? AND course_code=?
            """, (prog, lvl, code))

            con.commit()
            con.close()

            self.load_plans()

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())
