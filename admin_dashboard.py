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
        self.create_plans_page()       # Index 3 (Updated)

        # 6. Initial Data Load
        self.load_dashboard_stats()
        self.load_students()
        self.load_courses()
        self.load_plans()              # Updated Logic

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

        # Logo
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
        
        # Logout Button
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

        # Stats Cards
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
        t.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
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

        # Header
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

        # Table
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Program", "Level"])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.student_table.setAlternatingRowColors(True)
        self.student_table.verticalHeader().setVisible(False)
        layout.addWidget(self.student_table)

        # Action Bar
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.btn_del_student = QPushButton("Delete Selected Student")
        self.btn_del_student.setProperty("class", "danger-btn")
        self.btn_del_student.clicked.connect(self.handle_delete_student)
        
        action_layout.addWidget(self.btn_del_student)
        layout.addLayout(action_layout)

        # Add Student Form
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QFormLayout(form_frame)
        form_layout.setLabelAlignment(Qt.AlignRight)

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

        form_layout.addRow("Student ID:", self.inp_s_id)
        form_layout.addRow("Name:", self.inp_s_name)
        form_layout.addRow("Email:", self.inp_s_email)
        form_layout.addRow("Program:", self.inp_s_program)
        form_layout.addRow("Level:", self.inp_s_level)

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

        # Header
        title = QLabel("Course Management")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # --- Top: Table ---
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels(["Code", "Name", "Credits", "Day", "Start", "End", "Room", "Cap"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.course_table.setAlternatingRowColors(True)
        self.course_table.setFixedHeight(300)
        self.course_table.verticalHeader().setVisible(False)
        layout.addWidget(self.course_table)

        # Delete Button
        btn_del_layout = QHBoxLayout()
        btn_del_layout.addStretch()
        self.btn_del_course = QPushButton("Delete Selected Course")
        self.btn_del_course.setProperty("class", "danger-btn")
        self.btn_del_course.clicked.connect(self.handle_delete_course)
        btn_del_layout.addWidget(self.btn_del_course)
        layout.addLayout(btn_del_layout)

        # --- Bottom: Add Course Form ---
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QVBoxLayout(form_frame)
        
        lbl_add = QLabel("Add New Course")
        lbl_add.setProperty("class", "section-title")
        form_layout.addWidget(lbl_add)

        # Grid of Inputs
        grid = QHBoxLayout()
        
        # Col 1
        col1 = QVBoxLayout()
        self.inp_code = QLineEdit(); self.inp_code.setPlaceholderText("Code (e.g. EE201)")
        self.inp_name = QLineEdit(); self.inp_name.setPlaceholderText("Course Name")
        self.inp_credits = QSpinBox(); self.inp_credits.setRange(1, 6); self.inp_credits.setPrefix("Credits: ")
        col1.addWidget(QLabel("Details"))
        col1.addWidget(self.inp_code)
        col1.addWidget(self.inp_name)
        col1.addWidget(self.inp_credits)
        
        # Col 2
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Schedule (Select Days)"))
        
        days_layout = QHBoxLayout()
        self.day_checkboxes = [] 
        days_list = ["Sun", "Mon", "Tue", "Wed", "Thu"]
        
        for day in days_list:
            cb = QCheckBox(day)
            self.day_checkboxes.append(cb)
            days_layout.addWidget(cb)
            
        col2.addLayout(days_layout)

        self.inp_start = QSpinBox(); self.inp_start.setRange(8, 20); self.inp_start.setSuffix(":00"); self.inp_start.setPrefix("Start: ")
        self.inp_end = QSpinBox(); self.inp_end.setRange(9, 21); self.inp_end.setSuffix(":00"); self.inp_end.setPrefix("End: ")
        
        col2.addWidget(self.inp_start)
        col2.addWidget(self.inp_end)

        # Col 3
        col3 = QVBoxLayout()
        self.inp_room = QLineEdit(); self.inp_room.setPlaceholderText("Room (e.g. 25-101)")
        self.inp_cap = QSpinBox(); self.inp_cap.setRange(10, 100); self.inp_cap.setValue(30); self.inp_cap.setPrefix("Cap: ")
        
        self.btn_add_course = QPushButton("Add Course")
        self.btn_add_course.setProperty("class", "success-btn")
        self.btn_add_course.clicked.connect(self.handle_add_course)
        
        col3.addWidget(QLabel("Location"))
        col3.addWidget(self.inp_room)
        col3.addWidget(self.inp_cap)
        col3.addWidget(self.btn_add_course)

        grid.addLayout(col1)
        grid.addLayout(col2)
        grid.addLayout(col3)
        form_layout.addLayout(grid)

        layout.addWidget(form_frame)
        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 4: MANAGE PLANS (UPDATED: SHOW ALL LEVELS)
    # =======================================================
    def create_plans_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        title = QLabel("Program Plans Management")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # --- Filter Section (Program ONLY) ---
        filter_frame = QFrame()
        filter_frame.setProperty("class", "card")
        filter_layout = QHBoxLayout(filter_frame)
        
        self.filter_program = QComboBox()
        self.filter_program.addItems(["Computer", "Comm", "Power", "Biomedical"])
        self.filter_program.currentIndexChanged.connect(self.load_plans)
        
        # Note: Level filter removed for display, moved to Add section
        
        filter_layout.addWidget(QLabel("Select Program:"))
        filter_layout.addWidget(self.filter_program)
        filter_layout.addStretch()
        
        layout.addWidget(filter_frame)

        # --- Table Section ---
        self.plans_table = QTableWidget()
        self.plans_table.setColumnCount(3)
        self.plans_table.setHorizontalHeaderLabels(["Program", "Level", "Course Code"])
        self.plans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plans_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plans_table.setAlternatingRowColors(True)
        layout.addWidget(self.plans_table)

        # --- Add Course to Plan Section ---
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        form_layout = QHBoxLayout(form_frame)
        
        # New: Target Level Input for Adding
        self.inp_plan_level = QSpinBox()
        self.inp_plan_level.setRange(1, 10)
        self.inp_plan_level.setPrefix("Level: ")

        self.combo_plan_course = QComboBox()
        self.load_course_codes_into_combo()
        
        btn_add_plan = QPushButton("Add Course to Plan")
        btn_add_plan.setProperty("class", "success-btn")
        btn_add_plan.clicked.connect(self.handle_add_to_plan)
        
        btn_del_plan = QPushButton("Remove Selected")
        btn_del_plan.setProperty("class", "danger-btn")
        btn_del_plan.clicked.connect(self.handle_delete_from_plan)

        form_layout.addWidget(QLabel("Add Course:"))
        form_layout.addWidget(self.combo_plan_course)
        form_layout.addWidget(QLabel("To:"))
        form_layout.addWidget(self.inp_plan_level) # Add the level selector here
        form_layout.addWidget(btn_add_plan)
        form_layout.addStretch()
        form_layout.addWidget(btn_del_plan)
        
        layout.addWidget(form_frame)
        
        self.content_area.addWidget(page)

    # =======================================================
    # DATA LOADING & LOGIC
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
            print(f"Stats Error: {e}")

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
            print(f"Student Load Error: {e}")

    def load_courses(self):
        self.course_table.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT course_code, course_name, credits, day, start_time, end_time, room, max_capacity FROM courses")
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.course_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.course_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        except Exception as e:
            print(f"Course Load Error: {e}")

    # --- PLANS LOGIC (UPDATED) ---
    def load_course_codes_into_combo(self):
        self.combo_plan_course.clear()
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT course_code FROM courses")
            courses = cur.fetchall()
            con.close()
            for c in courses:
                self.combo_plan_course.addItem(c[0])
        except Exception as e:
            print(f"Error loading courses: {e}")

    def load_plans(self):
        """Loads ALL plans for the selected program, ordered by Level."""
        self.plans_table.setRowCount(0)
        prog = self.filter_program.currentText()
        
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            # Changed Query: No longer filters by level, only Program. Order by Level.
            cur.execute("SELECT program, level, course_code FROM program_plans WHERE program=? ORDER BY level ASC", (prog,))
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.plans_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.plans_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        except Exception as e:
            print(f"Plan Load Error: {e}")

    # =======================================================
    # HANDLERS
    # =======================================================
    def handle_delete_student(self):
        row = self.student_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a student to delete.")
            return

        student_id = self.student_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm", f"Delete student ID {student_id}?\nThis will remove all their records.", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_student(student_id)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_students()
                self.load_dashboard_stats()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_add_student(self):
        student_id = self.inp_s_id.text().strip()
        name = self.inp_s_name.text().strip()
        email = self.inp_s_email.text().strip()
        program = self.inp_s_program.currentText()
        level = self.inp_s_level.value()

        if not student_id or not name or not email:
            QMessageBox.warning(self, "Error", "Please fill Student ID, Name, and Email.")
            return

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("INSERT INTO students (id, name, email, program, level) VALUES (?, ?, ?, ?, ?)", (student_id, name, email, program, level))
            con.commit()
            con.close()

            QMessageBox.information(self, "Success", "Student added successfully.")
            self.load_students()
            self.load_dashboard_stats()
            self.inp_s_id.clear()
            self.inp_s_name.clear()
            self.inp_s_email.clear()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Database Error: {e}")

    def handle_add_course(self):
        code = self.inp_code.text()
        name = self.inp_name.text()
        credits = self.inp_credits.value()
        
        # Gather Days
        selected_days = []
        for cb in self.day_checkboxes:
            if cb.isChecked():
                selected_days.append(cb.text())
        
        if not selected_days:
            QMessageBox.warning(self, "Error", "Please select at least one day.")
            return
        day_str = ", ".join(selected_days) 

        start = self.inp_start.value()
        end = self.inp_end.value()
        room = self.inp_room.text()
        cap = self.inp_cap.value()

        success, msg = self.admin_logic.add_course(code, name, credits, day_str, start, end, room, cap, [])
        
        if success:
            QMessageBox.information(self, "Success", "Course Added Successfully")
            self.load_courses()
            self.load_dashboard_stats()
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
            QMessageBox.warning(self, "Warning", "Please select a course to delete.")
            return
            
        code = self.course_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm", f"Delete course {code}?", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_course(code)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses()
                self.load_dashboard_stats()
                self.load_course_codes_into_combo()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_add_to_plan(self):
        prog = self.filter_program.currentText()
        lvl = self.inp_plan_level.value() # Get level from the specific input, not the filter
        code = self.combo_plan_course.currentText()
        
        if not code:
            QMessageBox.warning(self, "Error", "No course selected.")
            return

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT * FROM program_plans WHERE program=? AND level=? AND course_code=?", (prog, lvl, code))
            if cur.fetchone():
                QMessageBox.warning(self, "Error", f"Course {code} is already in the plan for {prog} Level {lvl}.")
                con.close()
                return

            cur.execute("INSERT INTO program_plans (program, level, course_code) VALUES (?, ?, ?)", (prog, lvl, code))
            con.commit()
            con.close()
            
            QMessageBox.information(self, "Success", f"Added {code} to {prog} Level {lvl}.")
            self.load_plans() # Reload the table to show the new entry
        except Exception as e:
            QMessageBox.critical(self, "Database Error", str(e))

    def handle_delete_from_plan(self):
        row = self.plans_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Warning", "Please select a row to remove.")
            return
            
        prog = self.plans_table.item(row, 0).text()
        lvl = self.plans_table.item(row, 1).text()
        code = self.plans_table.item(row, 2).text()
        
        confirm = QMessageBox.question(self, "Confirm", f"Remove {code} from {prog} Level {lvl}?", QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                con = sqlite3.connect("User.db")
                cur = con.cursor()
                cur.execute("DELETE FROM program_plans WHERE program=? AND level=? AND course_code=?", (prog, lvl, code))
                con.commit()
                con.close()
                self.load_plans()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())
