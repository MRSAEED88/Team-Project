import sys
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
                             QLineEdit, QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

# --- IMPORTS FROM YOUR LOGIC FILES ---
from RegistrationSystem import RegistrationSystem
from Student import Student
import users_db  # Helper functions

class StudentDashboard(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.student_obj = None  
        
        self.setWindowTitle("KAU Student Portal | Fall 2025")
        self.resize(1200, 750)

        # 1. Initialize the Logic Controller
        self.logic_system = RegistrationSystem()

        # 2. Apply Professional Styles
        self.setup_styles()

        # 3. Setup Main Layout & Sidebar
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.setup_sidebar()

        # 4. Setup Content Area (Stacked Widget)
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        # Create Pages
        self.create_dashboard_page()   # Index 0
        self.create_registration_page() # Index 1
        self.create_schedule_page()     # Index 2
        self.create_transcript_page()   # Index 3
        self.create_plan_page()         # Index 4

        # 5. Load Data
        self.load_student_data()
        self.refresh_ui()

        # Default Page
        self.nav_dashboard.setChecked(True)
        self.content_area.setCurrentIndex(0)

    # =======================================================
    # STYLE SHEET
    # =======================================================
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f6f9; }
            
            /* Sidebar */
            QFrame#Sidebar { background-color: #2c3e50; color: white; border: none; }
            QLabel#LogoLabel { font-size: 22px; font-weight: bold; color: #ecf0f1; padding: 20px; }
            
            /* Nav Buttons */
            QPushButton[class="nav-btn"] {
                background-color: transparent; border: none; color: #bdc3c7;
                text-align: left; padding: 15px 25px; font-size: 14px;
                border-left: 4px solid transparent;
            }
            QPushButton[class="nav-btn"]:hover { background-color: #34495e; color: white; }
            QPushButton[class="nav-btn"]:checked { background-color: #34495e; color: white; border-left: 4px solid #3498db; }
            
            /* Page Titles */
            QLabel[class="page-title"] { 
                font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; 
            }
            
            /* Cards */
            QFrame[class="card"] { 
                background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; 
            }
            
            /* Tables */
            QTableWidget { background-color: white; border: 1px solid #dcdcdc; gridline-color: #ecf0f1; font-size: 13px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 8px; border: none; font-weight: bold; color: #2c3e50; }
            
            /* Action Buttons */
            QPushButton[class="action-btn"] { background-color: #2980b9; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="action-btn"]:hover { background-color: #3498db; }
            
            QPushButton[class="danger-btn"] { background-color: #c0392b; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="danger-btn"]:hover { background-color: #e74c3c; }
        """)

    # =======================================================
    # SIDEBAR SETUP
    # =======================================================
    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(240)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Logo
        logo = QLabel("KAU Portal")
        logo.setObjectName("LogoLabel")
        layout.addWidget(logo)

        # Nav Buttons
        self.nav_dashboard = self.create_nav_button("Dashboard Overview")
        self.nav_plan = self.create_nav_button("My Program Plan") 
        self.nav_register = self.create_nav_button("Register for Courses")
        self.nav_schedule = self.create_nav_button("My Class Schedule")
        self.nav_transcript = self.create_nav_button("Academic Transcript")
        
        layout.addWidget(self.nav_dashboard)
        layout.addWidget(self.nav_plan)
        layout.addWidget(self.nav_register)
        layout.addWidget(self.nav_schedule)
        layout.addWidget(self.nav_transcript)
        layout.addStretch()

        # User Profile Mini-Section
        user_frame = QFrame()
        user_frame.setStyleSheet("background-color: #243342; padding: 15px;")
        user_layout = QVBoxLayout(user_frame)
        
        self.lbl_user_name = QLabel("Loading...")
        self.lbl_user_name.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        self.lbl_user_program = QLabel("General Engineering")
        self.lbl_user_program.setStyleSheet("color: #95a5a6; font-size: 12px;")
        
        user_layout.addWidget(self.lbl_user_name)
        user_layout.addWidget(self.lbl_user_program)
        layout.addWidget(user_frame)

        self.main_layout.addWidget(self.sidebar)

        # Connect Navigation
        self.nav_dashboard.clicked.connect(lambda: self.switch_page(0, self.nav_dashboard))
        self.nav_plan.clicked.connect(lambda: self.switch_page(4, self.nav_plan))
        self.nav_register.clicked.connect(lambda: self.switch_page(1, self.nav_register))
        self.nav_schedule.clicked.connect(lambda: self.switch_page(2, self.nav_schedule))
        self.nav_transcript.clicked.connect(lambda: self.switch_page(3, self.nav_transcript))

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
    # PAGE 1: DASHBOARD HOME
    # =======================================================
    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Dashboard Overview")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # Info Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        self.card_gpa = self.create_info_card("GPA", "3.75", "#27ae60")
        self.card_credits = self.create_info_card("Registered Credits", "0 / 18", "#2980b9")
        self.card_status = self.create_info_card("Academic Status", "Regular", "#f39c12")
        
        cards_layout.addWidget(self.card_gpa)
        cards_layout.addWidget(self.card_credits)
        cards_layout.addWidget(self.card_status)
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
    # PAGE 2: REGISTRATION (TABLE)
    # =======================================================
    def create_registration_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QHBoxLayout()
        page_title = QLabel("Available Courses")
        page_title.setProperty("class", "page-title")
        header.addWidget(page_title)
        
        header.addStretch()
        self.btn_refresh = QPushButton("Refresh Data")
        self.btn_refresh.clicked.connect(self.refresh_ui)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # Table
        self.reg_table = QTableWidget()
        self.reg_table.setColumnCount(6)
        self.reg_table.setHorizontalHeaderLabels(["Code", "Course Name", "Credits", "Day/Time", "Room", "Capacity"])
        self.reg_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.reg_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.reg_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reg_table.setAlternatingRowColors(True)
        self.reg_table.verticalHeader().setVisible(False)
        layout.addWidget(self.reg_table)

        # Register Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_register = QPushButton("Register Selected Course")
        self.btn_register.setProperty("class", "action-btn")
        self.btn_register.clicked.connect(self.handle_register)
        btn_layout.addWidget(self.btn_register)
        layout.addLayout(btn_layout)

        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 3: SCHEDULE (TABLE)
    # =======================================================
    def create_schedule_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        sched_title = QLabel("My Weekly Schedule")
        sched_title.setProperty("class", "page-title")
        layout.addWidget(sched_title)

        # Table
        self.sched_table = QTableWidget()
        self.sched_table.setColumnCount(4)
        self.sched_table.setHorizontalHeaderLabels(["Code", "Course Name", "Day/Time", "Room"])
        self.sched_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sched_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sched_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.sched_table.setAlternatingRowColors(True)
        self.sched_table.verticalHeader().setVisible(False)
        layout.addWidget(self.sched_table)

        # Drop Button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_drop = QPushButton("Drop Selected Course")
        self.btn_drop.setProperty("class", "danger-btn")
        self.btn_drop.clicked.connect(self.handle_drop)
        btn_layout.addWidget(self.btn_drop)
        layout.addLayout(btn_layout)

        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 4: TRANSCRIPT
    # =======================================================
    def create_transcript_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        trans_title = QLabel("Academic Transcript")
        trans_title.setProperty("class", "page-title")
        layout.addWidget(trans_title)

        # Table
        self.transcript_table = QTableWidget()
        self.transcript_table.setColumnCount(4)
        self.transcript_table.setHorizontalHeaderLabels(["Course Code", "Course Name", "Credits", "Grade"])
        self.transcript_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transcript_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transcript_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.transcript_table.setAlternatingRowColors(True)
        self.transcript_table.verticalHeader().setVisible(False)
        layout.addWidget(self.transcript_table)

        self.content_area.addWidget(page)

    # =======================================================
    # PAGE 5: PROGRAM PLAN
    # =======================================================
    def create_plan_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("My Program Plan")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # Plan Table
        self.plan_table = QTableWidget()
        self.plan_table.setColumnCount(5)
        self.plan_table.setHorizontalHeaderLabels(["Level", "Code", "Course Name", "Credits", "Status"])
        self.plan_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.plan_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.plan_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.plan_table.verticalHeader().setVisible(False)
        
        self.plan_table.setStyleSheet("""
            QHeaderView::section { background-color: #ecf0f1; padding: 8px; font-weight: bold; }
            QTableWidget { font-size: 13px; }
        """)
        
        layout.addWidget(self.plan_table)
        self.content_area.addWidget(page)

    # =======================================================
    # LOGIC: DATA LOADING & ACTIONS
    # =======================================================
    def load_student_data(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT name, email, program, level FROM students WHERE id=?", (self.user_id,))
            row = cur.fetchone()

            if row:
                name, email, program, level = row
            else:
                cur.execute("SELECT name, email FROM users WHERE id=?", (self.user_id,))
                user_row = cur.fetchone()
                
                if user_row:
                    name, email = user_row
                    program, level = "General Engineering", 1
                    try:
                        cur.execute("INSERT INTO students (id, name, email, program, level) VALUES (?, ?, ?, ?, ?)",
                                    (self.user_id, name, email, program, level))
                        con.commit()
                        print(f"Auto-healed profile for {name}")
                    except Exception as e:
                        print(f"Failed to auto-heal profile: {e}")
                else:
                    name, email, program, level = "Guest", "N/A", "N/A", 0

            self.lbl_user_name.setText(name)
            self.lbl_user_program.setText(program)
            
            if name != "Guest":
                self.student_obj = Student(self.user_id, name, email, program, level, "dummy")
                
            con.close()
        except Exception as e:
            print(f"Error loading student: {e}")

    def refresh_ui(self):
        """Reloads all tables with fresh data"""
        if self.student_obj:
            self.logic_system.refresh_data()
            self.load_available_courses_table()
            self.load_schedule_table()
            self.load_transcript_table()
            self.load_plan_table()

    def get_val(self, data, keys, default=""):
        for k in keys:
            if k in data and data[k] is not None:
                return data[k]
        return default

    def load_available_courses_table(self):
        self.reg_table.setRowCount(0)
        courses = self.logic_system.courses_data
        
        con = sqlite3.connect("User.db")
        cur = con.cursor()

        for code, details in courses.items():
            name = self.get_val(details, ['course_name', 'name', 'Name'], 'Unknown')
            credits = str(self.get_val(details, ['credits', 'Credits'], '0'))
            room = self.get_val(details, ['room', 'Room'], 'TBA')
            max_cap = self.get_val(details, ['max_capacity', 'Max_Capacity', 'capacity'], 0)
            
            sched = details.get('schedule', [])
            day = self.get_val(details, ['day', 'Day'])
            start = self.get_val(details, ['start_time', 'Start_Time', 'start'])
            end = self.get_val(details, ['end_time', 'End_Time', 'end'])

            # --- FIX: DISPLAY START AND END TIME ---
            if sched and isinstance(sched, list) and len(sched) > 0:
                # sched[0] is typically (Day, Start, End)
                # We want: "Mon 08:00 - 10:00"
                if len(sched[0]) >= 3:
                     time_str = f"{sched[0][0]} {sched[0][1]} - {sched[0][2]}"
                else:
                     time_str = f"{sched[0][0]} {sched[0][1]}"
            elif day and start:
                if end:
                     time_str = f"{day} {start} - {end}"
                else:
                     time_str = f"{day} {start}"
            else:
                time_str = "TBA"

            current = 0
            try:
                cur.execute("SELECT COUNT(*) FROM registration WHERE course_code=?", (code,))
                current += cur.fetchone()[0]
            except: 
                try: cur.execute("SELECT COUNT(*) FROM registrations WHERE course_code=?", (code,)); current += cur.fetchone()[0]
                except: pass
            
            cap_str = f"{current} / {max_cap}"

            row = self.reg_table.rowCount()
            self.reg_table.insertRow(row)
            self.reg_table.setItem(row, 0, QTableWidgetItem(str(code)))
            self.reg_table.setItem(row, 1, QTableWidgetItem(name))
            self.reg_table.setItem(row, 2, QTableWidgetItem(credits))
            self.reg_table.setItem(row, 3, QTableWidgetItem(time_str))
            self.reg_table.setItem(row, 4, QTableWidgetItem(room))
            self.reg_table.setItem(row, 5, QTableWidgetItem(cap_str))
        
        con.close()

    def load_schedule_table(self):
        self.sched_table.setRowCount(0)
        if not self.student_obj: return

        my_codes = self.logic_system.get_student_registered_courses(self.student_obj)
        all_data = self.logic_system.courses_data
        
        total_credits = 0

        for code in my_codes:
            details = all_data.get(code, {})
            name = self.get_val(details, ['course_name', 'name', 'Name'], 'Unknown')
            room = self.get_val(details, ['room', 'Room'], 'TBA')
            credits = int(self.get_val(details, ['credits', 'Credits'], 0))

            sched = details.get('schedule', [])
            day = self.get_val(details, ['day', 'Day'])
            start = self.get_val(details, ['start_time', 'Start_Time', 'start'])
            end = self.get_val(details, ['end_time', 'End_Time', 'end'])

            # --- FIX: DISPLAY START AND END TIME IN SCHEDULE TAB TOO ---
            if sched and isinstance(sched, list) and len(sched) > 0:
                if len(sched[0]) >= 3:
                     time_str = f"{sched[0][0]} {sched[0][1]} - {sched[0][2]}"
                else:
                     time_str = f"{sched[0][0]} {sched[0][1]}"
            elif day and start:
                if end:
                     time_str = f"{day} {start} - {end}"
                else:
                     time_str = f"{day} {start}"
            else:
                time_str = "TBA"

            total_credits += credits

            row = self.sched_table.rowCount()
            self.sched_table.insertRow(row)
            self.sched_table.setItem(row, 0, QTableWidgetItem(str(code)))
            self.sched_table.setItem(row, 1, QTableWidgetItem(name))
            self.sched_table.setItem(row, 2, QTableWidgetItem(time_str))
            self.sched_table.setItem(row, 3, QTableWidgetItem(room))
        
        if hasattr(self, 'card_credits'):
             value_label = self.card_credits.layout().itemAt(1).widget()
             value_label.setText(f"{total_credits} / 18")

    def load_transcript_table(self):
        self.transcript_table.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            query = """
                SELECT t.course_code, c.course_name, c.credits, t.grade 
                FROM transcripts t
                LEFT JOIN courses c ON t.course_code = c.course_code
                WHERE t.student_id = ?
            """
            cur.execute(query, (self.user_id,))
            rows = cur.fetchall()
            for row_data in rows:
                code, name, credits, grade = row_data
                name = name if name else "Unknown Course"
                credits = str(credits) if credits else "-"
                row_idx = self.transcript_table.rowCount()
                self.transcript_table.insertRow(row_idx)
                self.transcript_table.setItem(row_idx, 0, QTableWidgetItem(str(code)))
                self.transcript_table.setItem(row_idx, 1, QTableWidgetItem(str(name)))
                self.transcript_table.setItem(row_idx, 2, QTableWidgetItem(str(credits)))
                self.transcript_table.setItem(row_idx, 3, QTableWidgetItem(str(grade)))
            con.close()
        except Exception as e:
            print(f"Error loading transcript: {e}")

    # =======================================================
    # LOAD PROGRAM PLAN
    # =======================================================
    def load_plan_table(self):
        self.plan_table.setRowCount(0)
        if not self.student_obj: return

        program = self.student_obj.program
        plan = self.logic_system.program_plan.get(program, {})

        try:
            completed = users_db.get_completed_courses(self.user_id)
            registered = set(self.logic_system.get_student_registered_courses(self.student_obj))
        except:
            completed = set()
            registered = set()

        all_courses = self.logic_system.courses_data

        sorted_levels = sorted(plan.keys())
        for level in sorted_levels:
            course_codes = plan[level]
            for code in course_codes:
                details = all_courses.get(code, {})
                name = self.get_val(details, ['course_name', 'name', 'Name'], 'Unknown')
                credits = str(self.get_val(details, ['credits', 'Credits'], '-'))

                if code in registered:
                    status = "In Progress"
                    color = QColor("#cce5ff") # Blueish
                elif code in completed:
                    status = "Completed"
                    color = QColor("#d4edda") # Greenish
                else:
                    status = "Not Started"
                    color = QColor("#f8d7da") # Redish

                row = self.plan_table.rowCount()
                self.plan_table.insertRow(row)
                self.plan_table.setItem(row, 0, QTableWidgetItem(f"Level {level}"))
                self.plan_table.setItem(row, 1, QTableWidgetItem(code))
                self.plan_table.setItem(row, 2, QTableWidgetItem(name))
                self.plan_table.setItem(row, 3, QTableWidgetItem(credits))
                
                item_status = QTableWidgetItem(status)
                item_status.setBackground(QBrush(color))
                item_status.setForeground(QBrush(Qt.black))
                self.plan_table.setItem(row, 4, item_status)

    def handle_register(self):
        if not self.student_obj: return
        
        row = self.reg_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Course", "Please select a course to register.")
            return

        course_code = self.reg_table.item(row, 0).text()

        current_regs = self.logic_system.get_student_registered_courses(self.student_obj)
        if course_code in current_regs:
            QMessageBox.warning(self, "Warning", f"You are already registered in {course_code}.")
            return

        success, msg = self.logic_system.register_courses_for_student(self.student_obj, [course_code])

        if success:
            QMessageBox.information(self, "Success", msg)
            self.refresh_ui()
        else:
            QMessageBox.warning(self, "Registration Failed", msg)

    def handle_drop(self):
        if not self.student_obj: return

        row = self.sched_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Course", "Please select a course to drop.")
            return

        course_code = self.sched_table.item(row, 0).text()

        success, msg = self.logic_system.drop_course_for_student(self.student_obj, course_code)
        
        if success:
            QMessageBox.information(self, "Dropped", msg)
            self.refresh_ui()
        else:
            QMessageBox.warning(self, "Error", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    window = StudentDashboard(user_id=1) 
    window.show()
    sys.exit(app.exec_())
