import sys
import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
    QLineEdit, QAbstractItemView, QMessageBox, QComboBox,
    QSpinBox, QFormLayout, QCheckBox, QFileDialog, QListWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- IMPORT ADMIN LOGIC ---
from Admin import Admin


class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("KAU Admin Portal | Fall 2025")
        self.resize(1300, 800)

        # حالة تعديل الكورس
        self.edit_mode = False
        self.current_edit_code = None

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
        self.student_table.setAlternatingRowColors(True)
        self.student_table.verticalHeader().setVisible(False)
        layout.addWidget(self.student_table)

        # Action Bar (Show Password)
        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_show_password = QPushButton("Show Password")
        self.btn_show_password.setProperty("class", "action-btn")
        self.btn_show_password.clicked.connect(self.handle_show_password)
        action_layout.addWidget(self.btn_show_password)

        layout.addLayout(action_layout)

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

        # TABLE
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels(
            ["Code", "Name", "Credits", "Day(s)", "Start", "End", "Room", "Cap"]
        )
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.course_table.setAlternatingRowColors(True)
        self.course_table.verticalHeader().setVisible(False)
        layout.addWidget(self.course_table)

        # ACTION BAR (IMPORT / LOAD / DELETE)
        action_layout = QHBoxLayout()

        self.btn_import = QPushButton("Import CSV")
        self.btn_import.setProperty("class", "action-btn")
        self.btn_import.clicked.connect(self.handle_import_csv)
        action_layout.addWidget(self.btn_import)

        self.btn_load_course = QPushButton("Load Selected for Edit")
        self.btn_load_course.setProperty("class", "action-btn")
        self.btn_load_course.clicked.connect(self.handle_load_course_for_edit)
        action_layout.addWidget(self.btn_load_course)

        action_layout.addStretch()

        self.btn_del_course = QPushButton("Delete Selected Course")
        self.btn_del_course.setProperty("class", "danger-btn")
        self.btn_del_course.clicked.connect(self.handle_delete_course)
        action_layout.addWidget(self.btn_del_course)

        layout.addLayout(action_layout)

        # ADD / EDIT COURSE FORM
        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        f = QVBoxLayout(form_frame)

        lbl_add = QLabel("Add / Edit Course")
        lbl_add.setProperty("class", "section-title")
        f.addWidget(lbl_add)

        grid = QHBoxLayout()

        # Column 1: Details
        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Details"))
        self.inp_code = QLineEdit()
        self.inp_code.setPlaceholderText("Code (e.g. EE201)")
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText("Course Name")
        self.inp_credits = QSpinBox()
        self.inp_credits.setRange(1, 6)
        self.inp_credits.setPrefix("Credits: ")

        col1.addWidget(self.inp_code)
        col1.addWidget(self.inp_name)
        col1.addWidget(self.inp_credits)

        # Column 2: Schedule
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
        self.inp_start.setPrefix("Start: ")
        self.inp_start.setSuffix(":00")

        self.inp_end = QSpinBox()
        self.inp_end.setRange(9, 21)
        self.inp_end.setPrefix("End: ")
        self.inp_end.setSuffix(":00")

        col2.addWidget(self.inp_start)
        col2.addWidget(self.inp_end)

        # Column 3: Location + Prereqs + Buttons
        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Location"))
        self.inp_room = QLineEdit()
        self.inp_room.setPlaceholderText("Room (e.g. 25-101)")
        self.inp_cap = QSpinBox()
        self.inp_cap.setRange(10, 100)
        self.inp_cap.setPrefix("Cap: ")

        col3.addWidget(self.inp_room)
        col3.addWidget(self.inp_cap)

        # Prerequisites UI
        col3.addWidget(QLabel("Prerequisites"))
        self.prereq_combo = QComboBox()
        self.refresh_prereq_combo()   # load course codes into combo
        col3.addWidget(self.prereq_combo)

        self.btn_add_prereq = QPushButton("Add Prerequisite")
        self.btn_add_prereq.setProperty("class", "action-btn")
        self.btn_add_prereq.clicked.connect(self.handle_add_prereq)
        col3.addWidget(self.btn_add_prereq)

        self.prereq_list = QListWidget()
        self.prereq_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.prereq_list.itemDoubleClicked.connect(self.handle_remove_prereq_item)
        col3.addWidget(self.prereq_list)

        # Buttons
        self.btn_add_course = QPushButton("Add New Course")
        self.btn_add_course.setProperty("class", "success-btn")
        self.btn_add_course.clicked.connect(self.handle_add_course)
        col3.addWidget(self.btn_add_course)

        self.btn_update_course = QPushButton("Save Changes")
        self.btn_update_course.setProperty("class", "action-btn")
        self.btn_update_course.setEnabled(False)
        self.btn_update_course.clicked.connect(self.handle_update_course)
        col3.addWidget(self.btn_update_course)

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
        self.plans_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plans_table.setAlternatingRowColors(True)
        self.plans_table.verticalHeader().setVisible(False)
        layout.addWidget(self.plans_table)

        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        ff = QHBoxLayout(form_frame)

        self.inp_plan_level = QSpinBox()
        self.inp_plan_level.setRange(1, 10)
        self.inp_plan_level.setPrefix("Level: ")

        self.combo_plan_course = QComboBox()
        self.load_course_codes_into_combo()

        btn_add_plan = QPushButton("Add to Plan")
        btn_add_plan.setProperty("class", "success-btn")
        btn_add_plan.clicked.connect(self.handle_add_to_plan)

        btn_del_plan = QPushButton("Remove Selected")
        btn_del_plan.setProperty("class", "danger-btn")
        btn_del_plan.clicked.connect(self.handle_delete_from_plan)

        ff.addWidget(QLabel("Add Course:"))
        ff.addWidget(self.combo_plan_course)
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

            # نختار الأعمدة المطلوبة فقط عشان الكود يكون أول عمود
            cur.execute("""
                SELECT course_code, course_name, credits, day, start_time, end_time, room, max_capacity
                FROM courses
                ORDER BY course_code
            """)
            rows = cur.fetchall()
            con.close()

            for row_idx, row_data in enumerate(rows):
                self.course_table.insertRow(row_idx)
                for col_idx, data in enumerate(row_data):
                    self.course_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))

        except Exception as e:
            print("Course Load Error:", e)

    def refresh_prereq_combo(self):
        """تحديث قائمة الكورسات المستخدمة لاختيار المتطلبات."""
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT course_code FROM courses ORDER BY course_code")
            courses = cur.fetchall()
            con.close()

            self.prereq_combo.clear()
            for c in courses:
                self.prereq_combo.addItem(c[0])

        except Exception as e:
            print("Prereq Combo Load Error:", e)

    def load_course_codes_into_combo(self):
        """تستخدم في صفحة الخطط لعرض الكورسات في الكومبوبوكس."""
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("SELECT course_code FROM courses ORDER BY course_code")
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
                "SELECT program, level, course_code FROM program_plans WHERE program=? ORDER BY level ASC, course_code",
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
    # HELPERS (PREREQS)
    # =======================================================
    def get_current_prereq_codes(self):
        codes = []
        for i in range(self.prereq_list.count()):
            codes.append(self.prereq_list.item(i).text())
        return codes

    # =======================================================
    # HANDLERS - STUDENTS
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

        # --- UPDATED: Use Admin Logic Class (Enforces Encryption) ---
        success, msg = self.admin_logic.add_student(
            student_id, name, email, program, level, password
        )

        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_students()
            self.load_dashboard_stats()

            # Clear inputs
            self.inp_s_id.clear()
            self.inp_s_name.clear()
            self.inp_s_email.clear()
            self.inp_s_password.clear()
        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_show_password(self):
        row = self.student_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a student first.")
            return

        student_id = self.student_table.item(row, 0).text()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT password FROM users WHERE id=?", (student_id,))
            res = cur.fetchone()
            con.close()

            if not res:
                QMessageBox.information(self, "Password", "No user record found in users table.")
            else:
                pwd = res[0]
                QMessageBox.information(self, "Password", f"Password for ID {student_id}:\n{pwd}")

        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    # =======================================================
    # HANDLERS - COURSES
    # =======================================================
    def handle_add_prereq(self):
        code = self.prereq_combo.currentText().strip()
        if not code:
            return

        # ما نكرر الكود في القائمة
        existing = self.get_current_prereq_codes()
        if code in existing:
            return

        self.prereq_list.addItem(code)

    def handle_remove_prereq_item(self, item):
        row = self.prereq_list.row(item)
        self.prereq_list.takeItem(row)

    def handle_add_course(self):
        # إضافة كورس جديد (NOT edit)
        code = self.inp_code.text().strip()
        name = self.inp_name.text().strip()
        credits = self.inp_credits.value()

        days = [cb.text() for cb in self.day_checkboxes if cb.isChecked()]
        if not days:
            QMessageBox.warning(self, "Error", "Please select at least one day.")
            return
        day_str = ", ".join(days)

        start = self.inp_start.value()
        end = self.inp_end.value()
        room = self.inp_room.text().strip()
        cap = self.inp_cap.value()

        prereqs = self.get_current_prereq_codes()

        success, msg = self.admin_logic.add_course(
            code, name, credits, day_str, start, end, room, cap, prereqs
        )

        if success:
            QMessageBox.information(self, "Success", "Course Added.")
            self.load_courses()
            self.refresh_prereq_combo()
            self.load_course_codes_into_combo()

            # Clear form
            self.inp_code.clear()
            self.inp_name.clear()
            self.inp_room.clear()
            self.inp_credits.setValue(1)
            self.inp_start.setValue(8)
            self.inp_end.setValue(9)
            self.inp_cap.setValue(10)
            for cb in self.day_checkboxes:
                cb.setChecked(False)
            self.prereq_list.clear()

        else:
            QMessageBox.warning(self, "Error", msg)

    def handle_load_course_for_edit(self):
        row = self.course_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Select a course first.")
            return

        code = self.course_table.item(row, 0).text()
        name = self.course_table.item(row, 1).text()
        credits = self.course_table.item(row, 2).text()
        days_str = self.course_table.item(row, 3).text()
        start_str = self.course_table.item(row, 4).text()
        end_str = self.course_table.item(row, 5).text()
        room = self.course_table.item(row, 6).text()
        cap_str = self.course_table.item(row, 7).text()

        # وضع وضعية التعديل
        self.edit_mode = True
        self.current_edit_code = code
        self.btn_update_course.setEnabled(True)

        # الكود مايتغير في التعديل (عشان ما نخرب الجداول الثانية)
        self.inp_code.setText(code)
        self.inp_code.setReadOnly(True)

        self.inp_name.setText(name)
        try:
            self.inp_credits.setValue(int(credits))
        except ValueError:
            self.inp_credits.setValue(1)

        # الأيام
        days_list = [d.strip() for d in days_str.split(",")] if days_str else []
        for cb in self.day_checkboxes:
            cb.setChecked(cb.text() in days_list)

        # الأوقات (نحاول نقرأ أول ساعتين من النص)
        def parse_hour(s):
            s = str(s)
            if ":" in s:
                try:
                    return int(s.split(":")[0])
                except:
                    return 8
            try:
                return int(s)
            except:
                return 8

        self.inp_start.setValue(parse_hour(start_str))
        self.inp_end.setValue(parse_hour(end_str))

        self.inp_room.setText(room)
        try:
            self.inp_cap.setValue(int(cap_str))
        except ValueError:
            self.inp_cap.setValue(10)

        # تحميل المتطلبات من جدول prerequisites
        self.prereq_list.clear()
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT prereq_code FROM prerequisites WHERE course_code=?", (code,))
            rows = cur.fetchall()
            con.close()
            for r in rows:
                self.prereq_list.addItem(r[0])
        except Exception as e:
            print("Load Prereqs Error:", e)

        QMessageBox.information(self, "Edit Mode", f"Now editing course: {code}")

    def handle_update_course(self):
        if not self.edit_mode or not self.current_edit_code:
            QMessageBox.warning(self, "Error", "No course loaded for editing.")
            return

        code = self.current_edit_code  # ثابت عشان ما نخرب الربط
        name = self.inp_name.text().strip()
        credits = self.inp_credits.value()

        days = [cb.text() for cb in self.day_checkboxes if cb.isChecked()]
        if not days:
            QMessageBox.warning(self, "Error", "Please select at least one day.")
            return
        day_str = ", ".join(days)

        start = self.inp_start.value()
        end = self.inp_end.value()
        room = self.inp_room.text().strip()
        cap = self.inp_cap.value()

        prereqs = self.get_current_prereq_codes()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            # تحديث جدول الكورسات
            cur.execute("""
                UPDATE courses
                SET course_name=?, credits=?, day=?, start_time=?, end_time=?, room=?, max_capacity=?
                WHERE course_code=?
            """, (name, credits, day_str, f"{start}:00", f"{end}:00", room, cap, code))

            # حذف المتطلبات القديمة ثم إضافة الجديدة
            cur.execute("DELETE FROM prerequisites WHERE course_code=?", (code,))
            for p in prereqs:
                cur.execute(
                    "INSERT INTO prerequisites (course_code, prereq_code) VALUES (?, ?)",
                    (code, p)
                )

            con.commit()
            con.close()

            QMessageBox.information(self, "Success", f"Course {code} updated successfully.")

            self.load_courses()
            self.refresh_prereq_combo()
            self.load_course_codes_into_combo()

            # الخروج من وضع التعديل
            self.edit_mode = False
            self.current_edit_code = None
            self.btn_update_course.setEnabled(False)
            self.inp_code.setReadOnly(False)

            # نفرغ النموذج
            self.inp_code.clear()
            self.inp_name.clear()
            self.inp_room.clear()
            self.inp_credits.setValue(1)
            self.inp_start.setValue(8)
            self.inp_end.setValue(9)
            self.inp_cap.setValue(10)
            for cb in self.day_checkboxes:
                cb.setChecked(False)
            self.prereq_list.clear()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Update failed: {e}")

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
                self.refresh_prereq_combo()
                self.load_course_codes_into_combo()
            else:
                QMessageBox.warning(self, "Error", msg)

    def handle_import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Course CSV", "", "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                success, summary, error_list = self.admin_logic.import_courses_from_csv(file_path)

                if success:
                    msg = summary
                    if error_list:
                        msg += "\n\nSample Errors:\n" + "\n".join(error_list[:5])

                    QMessageBox.information(self, "Import Result", msg)
                    self.load_courses()
                    self.load_dashboard_stats()
                    self.refresh_prereq_combo()
                    self.load_course_codes_into_combo()
                else:
                    QMessageBox.critical(self, "Import Failed", summary)
            except AttributeError:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Your Admin.py file is missing the 'import_courses_from_csv' method.\nPlease update Admin.py first."
                )

    # =======================================================
    # HANDLERS - PLANS
    # =======================================================
    def handle_add_to_plan(self):
        prog = self.filter_program.currentText()
        lvl = self.inp_plan_level.value()
        code = self.combo_plan_course.currentText()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            # نتجنب التكرار
            cur.execute("""
                SELECT 1 FROM program_plans WHERE program=? AND level=? AND course_code=?
            """, (prog, lvl, code))
            if cur.fetchone():
                con.close()
                QMessageBox.warning(self, "Error", f"{code} already in {prog} Level {lvl}.")
                return

            cur.execute("""
                INSERT INTO program_plans (program, level, course_code)
                VALUES (?, ?, ?)
            """, (prog, lvl, code))

            con.commit()
            con.close()

            QMessageBox.information(self, "Success", f"Added {code} to {prog} Level {lvl}")
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
    # عشان يفتح مثل صفحة اللوق إن على طول الشاشة
    window.showMaximized()
    sys.exit(app.exec_())
