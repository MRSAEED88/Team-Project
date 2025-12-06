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
from PyQt5.QtGui import QFont, QPixmap  # Added QPixmap

# --- matplotlib for Reports Tab ---
try:
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# --- IMPORT ADMIN LOGIC ---
from Admin import Admin


class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("ECE Admin Portal | Fall 2025")
        self.resize(1300, 800)

        # Edit Mode State
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
        self.create_dashboard_page()      # Index 0
        self.create_students_page()       # Index 1
        self.create_courses_page()        # Index 2
        self.create_plans_page()          # Index 3
        self.create_transcripts_page()    # Index 4
        self.create_reports_page()        # Index 5

        # 6. Initial Data Load
        self.load_dashboard_stats()
        self.load_students()
        self.load_courses()
        self.load_plans()
        self.load_transcript_student_list()
        self.load_reports_data()

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
            QPushButton[class="nav-btn"]:checked {
                background-color: #34495e; color: white; border-left: 4px solid #3498db;
            }
            QLabel[class="page-title"] {
                font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;
            }
            QLabel[class="section-title"] {
                font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 10px;
            }
            QFrame[class="card"] { background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; }
            QTableWidget {
                background-color: white; border: 1px solid #dcdcdc;
                gridline-color: #ecf0f1; font-size: 13px;
            }
            QHeaderView::section {
                background-color: #ecf0f1; padding: 8px; border: none;
                font-weight: bold; color: #2c3e50;
            }
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background: white;
            }
            QPushButton[class="action-btn"] {
                background-color: #2980b9; color: white; border-radius: 4px;
                padding: 8px 15px; font-weight: bold;
            }
            QPushButton[class="action-btn"]:hover { background-color: #3498db; }
            QPushButton[class="success-btn"] {
                background-color: #27ae60; color: white; border-radius: 4px;
                padding: 8px 15px; font-weight: bold;
            }
            QPushButton[class="success-btn"]:hover { background-color: #2ecc71; }
            QPushButton[class="danger-btn"] {
                background-color: #c0392b; color: white; border-radius: 4px;
                padding: 8px 15px; font-weight: bold;
            }
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
        layout.setSpacing(15) # Increased spacing

        # --- UPDATED LOGO SECTION ---
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        
        # Load the logo image
        pixmap = QPixmap("kau_logo.png") 
        
        if not pixmap.isNull():
            # Scale image to fit sidebar
            scaled = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled)
        else:
            # Fallback text if image missing
            img_label.setText("ADMIN")
            img_label.setStyleSheet("color: #bdc3c7; font-weight: bold; font-size: 20px;")
            
        layout.addWidget(img_label)

        # Text Title
        text_logo = QLabel("ECE Registration\nSystem")
        text_logo.setObjectName("LogoLabel")
        text_logo.setAlignment(Qt.AlignCenter)
        text_logo.setWordWrap(True)
        text_logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecf0f1; padding: 10px;")
        layout.addWidget(text_logo)
        # ----------------------------

        # Nav Buttons
        self.nav_dashboard = self.create_nav_button("Dashboard Overview")
        self.nav_students = self.create_nav_button("Manage Students")
        self.nav_courses = self.create_nav_button("Manage Courses")
        self.nav_plans = self.create_nav_button("Manage Plans")
        self.nav_transcripts = self.create_nav_button("Student Transcripts")
        self.nav_reports = self.create_nav_button("Reports & Analytics") 

        layout.addWidget(self.nav_dashboard)
        layout.addWidget(self.nav_students)
        layout.addWidget(self.nav_courses)
        layout.addWidget(self.nav_plans)
        layout.addWidget(self.nav_transcripts)
        layout.addWidget(self.nav_reports)

        layout.addStretch()

        self.btn_logout = self.create_nav_button("Log Out")
        self.btn_logout.clicked.connect(self.handle_logout) # Updated connect
        layout.addWidget(self.btn_logout)

        self.main_layout.addWidget(self.sidebar)

        # Connect Navigation
        self.nav_dashboard.clicked.connect(lambda: self.switch_page(0, self.nav_dashboard))
        self.nav_students.clicked.connect(lambda: self.switch_page(1, self.nav_students))
        self.nav_courses.clicked.connect(lambda: self.switch_page(2, self.nav_courses))
        self.nav_plans.clicked.connect(lambda: self.switch_page(3, self.nav_plans))
        self.nav_transcripts.clicked.connect(lambda: self.switch_page(4, self.nav_transcripts))
        self.nav_reports.clicked.connect(lambda: self.switch_page(5, self.nav_reports))

    def create_nav_button(self, text):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setProperty("class", "nav-btn")
        return btn

    def switch_page(self, index, btn_sender):
        self.content_area.setCurrentIndex(index)
        btn_sender.setChecked(True)

    def handle_logout(self):
        """Returns to the Login Window."""
        from Login_Window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.showMaximized()
        self.close()

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
        card.setStyleSheet(
            f"border-top: 4px solid {color}; background: white; border-radius: 8px;"
        )
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
        self.student_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Email", "Program", "Level"]
        )
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.student_table.setAlternatingRowColors(True)
        self.student_table.verticalHeader().setVisible(False)
        layout.addWidget(self.student_table)

        self.student_table.itemDoubleClicked.connect(
            self.open_transcript_from_students_page
        )

        action_layout = QHBoxLayout()
        action_layout.addStretch()

        self.btn_show_password = QPushButton("Show Password")
        self.btn_show_password.setProperty("class", "action-btn")
        self.btn_show_password.clicked.connect(self.handle_show_password)
        action_layout.addWidget(self.btn_show_password)

        layout.addLayout(action_layout)

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

        form_frame = QFrame()
        form_frame.setProperty("class", "card")
        f = QVBoxLayout(form_frame)

        lbl_add = QLabel("Add / Edit Course")
        lbl_add.setProperty("class", "section-title")
        f.addWidget(lbl_add)

        grid = QHBoxLayout()

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

        time_row_start = QHBoxLayout()
        self.inp_start_hour = QSpinBox()
        self.inp_start_hour.setRange(8, 20)
        self.inp_start_hour.setPrefix("Start H: ")
        self.inp_start_min = QComboBox()
        self.inp_start_min.addItems(["00", "15", "30", "45"])
        time_row_start.addWidget(self.inp_start_hour)
        time_row_start.addWidget(self.inp_start_min)
        col2.addLayout(time_row_start)

        time_row_end = QHBoxLayout()
        self.inp_end_hour = QSpinBox()
        self.inp_end_hour.setRange(9, 21)
        self.inp_end_hour.setPrefix("End H: ")
        self.inp_end_min = QComboBox()
        self.inp_end_min.addItems(["00", "15", "30", "45"])
        time_row_end.addWidget(self.inp_end_hour)
        time_row_end.addWidget(self.inp_end_min)
        col2.addLayout(time_row_end)

        col3 = QVBoxLayout()
        col3.addWidget(QLabel("Location"))
        self.inp_room = QLineEdit()
        self.inp_room.setPlaceholderText("Room (e.g. 25-101)")
        self.inp_cap = QSpinBox()
        self.inp_cap.setRange(1, 100)
        self.inp_cap.setPrefix("Cap: ")

        col3.addWidget(self.inp_room)
        col3.addWidget(self.inp_cap)

        col3.addWidget(QLabel("Prerequisites"))
        self.prereq_combo = QComboBox()
        self.refresh_prereq_combo()
        col3.addWidget(self.prereq_combo)

        self.btn_add_prereq = QPushButton("Add Prerequisite")
        self.btn_add_prereq.setProperty("class", "action-btn")
        self.btn_add_prereq.clicked.connect(self.handle_add_prereq)
        col3.addWidget(self.btn_add_prereq)

        self.prereq_list = QListWidget()
        self.prereq_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.prereq_list.itemDoubleClicked.connect(self.handle_remove_prereq_item)
        col3.addWidget(self.prereq_list)

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
    # PAGE 5: STUDENT TRANSCRIPTS
    # =======================================================
    def create_transcripts_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Student Transcripts")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        top_frame = QFrame()
        top_frame.setProperty("class", "card")
        top_layout = QHBoxLayout(top_frame)

        lbl_select = QLabel("Select Student:")
        self.transcript_student_combo = QComboBox()

        btn_refresh_students = QPushButton("Refresh")
        btn_refresh_students.setProperty("class", "action-btn")
        btn_refresh_students.clicked.connect(self.load_transcript_student_list)

        btn_load_transcript = QPushButton("Load Transcript")
        btn_load_transcript.setProperty("class", "success-btn")
        btn_load_transcript.clicked.connect(self.handle_load_transcript_clicked)

        top_layout.addWidget(lbl_select)
        top_layout.addWidget(self.transcript_student_combo)
        top_layout.addWidget(btn_refresh_students)
        top_layout.addStretch()
        top_layout.addWidget(btn_load_transcript)

        layout.addWidget(top_frame)

        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(4)
        self.transcript_table.setHorizontalHeaderLabels(
            ["Course Code", "Course Name", "Credits", "Grade"]
        )
        self.transcript_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transcript_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transcript_table.setAlternatingRowColors(True)
        self.transcript_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transcript_table)

        summary_layout = QHBoxLayout()
        self.lbl_transcript_summary = QLabel("No student selected.")
        summary_layout.addWidget(self.lbl_transcript_summary)
        summary_layout.addStretch()

        self.btn_save_grades = QPushButton("Save Grades")
        self.btn_save_grades.setProperty("class", "success-btn")
        self.btn_save_grades.clicked.connect(self.handle_save_grades)
        summary_layout.addWidget(self.btn_save_grades)

        layout.addLayout(summary_layout)

        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 6: REPORTS & ANALYTICS
    # =======================================================
    def create_reports_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Reports & Analytics")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        top_frame = QFrame()
        top_frame.setProperty("class", "card")
        top_layout = QHBoxLayout(top_frame)

        self.lbl_reports_info = QLabel("Course enrollment summary.")
        top_layout.addWidget(self.lbl_reports_info)

        top_layout.addStretch()

        btn_refresh_reports = QPushButton("Refresh Report")
        btn_refresh_reports.setProperty("class", "action-btn")
        btn_refresh_reports.clicked.connect(self.load_reports_data)
        top_layout.addWidget(btn_refresh_reports)

        layout.addWidget(top_frame)

        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(4)
        self.reports_table.setHorizontalHeaderLabels(
            ["Course Code", "Capacity", "Enrolled", "Remaining"]
        )
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.reports_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.reports_table.setAlternatingRowColors(True)
        self.reports_table.verticalHeader().setVisible(False)
        layout.addWidget(self.reports_table)

        if MATPLOTLIB_AVAILABLE:
            chart_frame = QFrame()
            chart_frame.setProperty("class", "card")
            chart_layout = QVBoxLayout(chart_frame)

            self.figure = Figure(figsize=(6, 4))
            self.canvas = FigureCanvas(self.figure)
            chart_layout.addWidget(self.canvas)

            layout.addWidget(chart_frame)
        else:
            layout.addWidget(QLabel("Matplotlib not installed. Please run: pip install matplotlib"))

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

            cur.execute("""
                SELECT course_code, course_name, credits, day,
                       start_time, end_time, room, max_capacity
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
                "SELECT program, level, course_code FROM program_plans "
                "WHERE program=? ORDER BY level ASC, course_code",
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

    def load_transcript_student_list(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT id, name FROM students ORDER BY id")
            rows = cur.fetchall()
            con.close()

            self.transcript_student_combo.clear()
            for sid, sname in rows:
                display = f"{sid} - {sname}"
                self.transcript_student_combo.addItem(display, str(sid))

        except Exception as e:
            print("Transcript Student List Error:", e)

    def load_reports_data(self):
        self.reports_table.setRowCount(0)
        course_codes = []
        enrolled_counts = []
        capacities = []

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()

            cur.execute("""
                SELECT course_code, max_capacity
                FROM courses
                ORDER BY course_code
            """)
            courses = cur.fetchall()

            for idx, (code, cap) in enumerate(courses):
                cur.execute(
                    "SELECT COUNT(*) FROM registration WHERE course_code = ?",
                    (code,)
                )
                enrolled = cur.fetchone()[0]
                remaining = max(cap - enrolled, 0)

                self.reports_table.insertRow(idx)
                self.reports_table.setItem(idx, 0, QTableWidgetItem(str(code)))
                self.reports_table.setItem(idx, 1, QTableWidgetItem(str(cap)))
                self.reports_table.setItem(idx, 2, QTableWidgetItem(str(enrolled)))
                self.reports_table.setItem(idx, 3, QTableWidgetItem(str(remaining)))

                course_codes.append(code)
                enrolled_counts.append(enrolled)
                capacities.append(cap)

            con.close()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load reports: {e}")
            return

        total_courses = len(course_codes)
        self.lbl_reports_info.setText(
            f"Total Courses: {total_courses} | Chart based on enrollment count per course."
        )

        if MATPLOTLIB_AVAILABLE:
            self.draw_enrollment_chart(course_codes, enrolled_counts, capacities)

    def draw_enrollment_chart(self, course_codes, enrolled_counts, capacities):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x_positions = range(len(course_codes))
        ax.bar(x_positions, enrolled_counts, color="#3498db")

        ax.set_xticks(x_positions)
        ax.set_xticklabels(course_codes, rotation=45, ha='right')
        ax.set_ylabel("Enrolled Students")
        ax.set_xlabel("Course Code")
        ax.set_title("Course Enrollment Count")

        self.figure.tight_layout()
        self.canvas.draw()

    # =======================================================
    # HELPERS
    # =======================================================
    def get_current_prereq_codes(self):
        codes = []
        for i in range(self.prereq_list.count()):
            codes.append(self.prereq_list.item(i).text())
        return codes

    def parse_time_str(self, s):
        try:
            s = str(s).strip()
            if ":" in s:
                parts = s.split(":")
                return int(parts[0]), int(parts[1])
            else:
                return int(s), 0
        except Exception:
            return 8, 0

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

        success, msg = self.admin_logic.add_student(
            student_id, name, email, program, level, password
        )

        if success:
            QMessageBox.information(self, "Success", msg)
            self.load_students()
            self.load_dashboard_stats()
            self.load_transcript_student_list()
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

    def open_transcript_from_students_page(self, item):
        row = item.row()
        sid_item = self.student_table.item(row, 0)
        if not sid_item:
            return
        student_id = sid_item.text().strip()
        idx = self.transcript_student_combo.findData(student_id)
        if idx != -1:
            self.transcript_student_combo.setCurrentIndex(idx)
        self.switch_page(4, self.nav_transcripts)
        self.load_transcript_for_student(student_id)

    # =======================================================
    # HANDLERS - COURSES
    # =======================================================
    def handle_add_prereq(self):
        code = self.prereq_combo.currentText().strip()
        if not code: return
        if code in self.get_current_prereq_codes(): return
        self.prereq_list.addItem(code)

    def handle_remove_prereq_item(self, item):
        self.prereq_list.takeItem(self.prereq_list.row(item))

    def handle_add_course(self):
        code = self.inp_code.text().strip()
        name = self.inp_name.text().strip()
        credits = self.inp_credits.value()
        days = [cb.text() for cb in self.day_checkboxes if cb.isChecked()]
        if not days:
            QMessageBox.warning(self, "Error", "Please select at least one day.")
            return
        day_str = ", ".join(days)
        start_time = f"{self.inp_start_hour.value():02d}:{self.inp_start_min.currentText()}"
        end_time = f"{self.inp_end_hour.value():02d}:{self.inp_end_min.currentText()}"
        room = self.inp_room.text().strip()
        cap = self.inp_cap.value()
        prereqs = self.get_current_prereq_codes()

        success, msg = self.admin_logic.add_course(
            code, name, credits, day_str, start_time, end_time, room, cap, prereqs
        )

        if success:
            QMessageBox.information(self, "Success", "Course Added.")
            self.load_courses()
            self.refresh_prereq_combo()
            self.load_course_codes_into_combo()
            self.load_reports_data()
            self.inp_code.clear()
            self.inp_name.clear()
            self.inp_room.clear()
            self.inp_credits.setValue(1)
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

        self.edit_mode = True
        self.current_edit_code = code
        self.btn_update_course.setEnabled(True)

        self.inp_code.setText(code)
        self.inp_code.setReadOnly(True)
        self.inp_name.setText(name)
        try: self.inp_credits.setValue(int(credits))
        except: self.inp_credits.setValue(1)

        days_list = [d.strip() for d in days_str.split(",")] if days_str else []
        for cb in self.day_checkboxes: cb.setChecked(cb.text() in days_list)

        sh, sm = self.parse_time_str(start_str)
        eh, em = self.parse_time_str(end_str)
        self.inp_start_hour.setValue(sh)
        self.inp_end_hour.setValue(eh)
        
        self.inp_room.setText(room)
        try: self.inp_cap.setValue(int(cap_str))
        except: self.inp_cap.setValue(10)

        self.prereq_list.clear()
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT prereq_code FROM prerequisites WHERE course_code=?", (code,))
            for r in cur.fetchall(): self.prereq_list.addItem(r[0])
            con.close()
        except: pass
        QMessageBox.information(self, "Edit Mode", f"Now editing course: {code}")

    def handle_update_course(self):
        if not self.edit_mode: return
        code = self.current_edit_code
        name = self.inp_name.text().strip()
        credits = self.inp_credits.value()
        days = [cb.text() for cb in self.day_checkboxes if cb.isChecked()]
        if not days: return QMessageBox.warning(self, "Error", "Select day")
        day_str = ", ".join(days)
        start_time = f"{self.inp_start_hour.value():02d}:{self.inp_start_min.currentText()}"
        end_time = f"{self.inp_end_hour.value():02d}:{self.inp_end_min.currentText()}"
        room = self.inp_room.text().strip()
        cap = self.inp_cap.value()
        prereqs = self.get_current_prereq_codes()

        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("""
                UPDATE courses
                SET course_name=?, credits=?, day=?, start_time=?, end_time=?, room=?, max_capacity=?
                WHERE course_code=?
            """, (name, credits, day_str, start_time, end_time, room, cap, code))
            
            cur.execute("DELETE FROM prerequisites WHERE course_code=?", (code,))
            for p in prereqs:
                cur.execute("INSERT INTO prerequisites (course_code, prereq_code) VALUES (?, ?)", (code, p))
            
            con.commit()
            con.close()
            QMessageBox.information(self, "Success", "Course updated.")
            self.load_courses()
            self.edit_mode = False
            self.btn_update_course.setEnabled(False)
            self.inp_code.setReadOnly(False)
            self.inp_code.clear()
            self.inp_name.clear()
        except Exception as e: QMessageBox.warning(self, "Error", str(e))

    def handle_delete_course(self):
        row = self.course_table.currentRow()
        if row < 0: return
        code = self.course_table.item(row, 0).text()
        if QMessageBox.question(self, "Confirm", f"Delete {code}?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            success, msg = self.admin_logic.delete_course(code)
            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses()
                self.refresh_prereq_combo()
                self.load_course_codes_into_combo()
                self.load_reports_data()

    def handle_import_csv(self):
        fp, _ = QFileDialog.getOpenFileName(self, "CSV", "", "CSV (*.csv)")
        if fp:
            s, sum_txt, errs = self.admin_logic.import_courses_from_csv(fp)
            msg = sum_txt + ("\nErrors:\n"+"\n".join(errs[:5]) if errs else "")
            QMessageBox.information(self,"Result",msg)
            self.load_courses(); self.load_reports_data()

    # =======================================================
    # HANDLERS - PLANS
    # =======================================================
    def handle_add_to_plan(self):
        p = self.filter_program.currentText(); l = self.inp_plan_level.value(); c = self.combo_plan_course.currentText()
        try:
            con = sqlite3.connect("User.db")
            if con.execute("SELECT 1 FROM program_plans WHERE program=? AND level=? AND course_code=?",(p,l,c)).fetchone():
                return QMessageBox.warning(self,"Error","Already exists in plan")
            con.execute("INSERT INTO program_plans VALUES (?,?,?)",(p,l,c)); con.commit(); con.close()
            self.load_plans()
        except Exception as e: QMessageBox.warning(self,"Error",str(e))

    def handle_delete_from_plan(self):
        r = self.plans_table.currentRow()
        if r < 0: return
        p = self.plans_table.item(r,0).text(); l = self.plans_table.item(r,1).text(); c = self.plans_table.item(r,2).text()
        try:
            con=sqlite3.connect("User.db"); con.execute("DELETE FROM program_plans WHERE program=? AND level=? AND course_code=?",(p,l,c)); con.commit(); con.close()
            self.load_plans()
        except: pass

    # =======================================================
    # HANDLERS - TRANSCRIPTS
    # =======================================================
    def handle_load_transcript_clicked(self):
        idx = self.transcript_student_combo.currentIndex()
        if idx<0: return QMessageBox.warning(self,"Error","No student selected")
        sid = self.transcript_student_combo.currentData()
        self.load_transcript_for_student(sid)

    def load_transcript_for_student(self, sid):
        self.transcript_table.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            nm = con.execute("SELECT name FROM students WHERE id=?",(sid,)).fetchone()
            nm = nm[0] if nm else "Unknown"
            
            rows = con.execute("""
                SELECT course_code, course_name, credits, grade FROM (
                    SELECT r.course_code, c.course_name, c.credits, t.grade 
                    FROM registration r 
                    LEFT JOIN courses c ON r.course_code=c.course_code 
                    LEFT JOIN transcripts t ON t.student_id=r.student_id AND t.course_code=r.course_code
                    WHERE r.student_id=?
                    UNION
                    SELECT t.course_code, c.course_name, c.credits, t.grade 
                    FROM transcripts t 
                    LEFT JOIN courses c ON t.course_code=c.course_code
                    WHERE t.student_id=? AND t.course_code NOT IN (SELECT course_code FROM registration WHERE student_id=?)
                ) ORDER BY course_code
            """, (sid, sid, sid)).fetchall()
            con.close()

            for r, rd in enumerate(rows):
                self.transcript_table.insertRow(r)
                for c, d in enumerate(rd):
                    it = QTableWidgetItem(str(d) if d else "")
                    if c in (0,1,2): it.setFlags(Qt.ItemIsSelectable|Qt.ItemIsEnabled)
                    self.transcript_table.setItem(r, c, it)
            self.lbl_transcript_summary.setText(f"Transcript for {sid} - {nm}")
        except Exception as e: QMessageBox.warning(self,"Error",str(e))

    def handle_save_grades(self):
        idx = self.transcript_student_combo.currentIndex()
        if idx<0: return
        sid = self.transcript_student_combo.currentData()
        try:
            con = sqlite3.connect("User.db")
            for r in range(self.transcript_table.rowCount()):
                cc = self.transcript_table.item(r,0).text()
                gr = self.transcript_table.item(r,3).text().strip()
                if not gr: con.execute("DELETE FROM transcripts WHERE student_id=? AND course_code=?",(sid,cc))
                else:
                    if con.execute("SELECT 1 FROM transcripts WHERE student_id=? AND course_code=?",(sid,cc)).fetchone():
                        con.execute("UPDATE transcripts SET grade=? WHERE student_id=? AND course_code=?",(gr,sid,cc))
                    else: con.execute("INSERT INTO transcripts VALUES (?,?,?)",(sid,cc,gr))
            con.commit(); con.close()
            QMessageBox.information(self,"Success","Grades saved.")
            self.load_transcript_for_student(sid)
        except Exception as e: QMessageBox.warning(self,"Error",str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = AdminDashboard()
    window.showMaximized()
    sys.exit(app.exec_())
