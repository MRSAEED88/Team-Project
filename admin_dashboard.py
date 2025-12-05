import sys
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
                             QLineEdit, QAbstractItemView, QMessageBox, QComboBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# --- IMPORT ADMIN LOGIC ---
from Admin import Admin

class AdminDashboard(QMainWindow):
    def __init__(self, user_id=None):
        super().__init__()
        self.setWindowTitle("KAU Admin Portal | Fall 2025")
        self.resize(1300, 800)
        
        # 1. Initialize Admin Logic (Mock credentials since we are already logged in)
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

        # 6. Initial Data Load
        self.load_dashboard_stats()
        self.load_students()
        self.load_courses()

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
            QLabel[class="section-title"] { 
                font-size: 16px; font-weight: bold; color: #27ae60; margin-top: 10px; 
            }
            
            /* Cards */
            QFrame[class="card"] { 
                background-color: white; border-radius: 8px; border: 1px solid #e0e0e0; 
            }
            
            /* Tables */
            QTableWidget { background-color: white; border: 1px solid #dcdcdc; gridline-color: #ecf0f1; font-size: 13px; }
            QHeaderView::section { background-color: #ecf0f1; padding: 8px; border: none; font-weight: bold; color: #2c3e50; }
            
            /* Inputs */
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px; border: 1px solid #bdc3c7; border-radius: 4px; background: white;
            }
            
            /* Action Buttons */
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
        
        layout.addWidget(self.nav_dashboard)
        layout.addWidget(self.nav_students)
        layout.addWidget(self.nav_courses)
        
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
        self.inp_day = QComboBox(); self.inp_day.addItems(["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"])
        self.inp_start = QSpinBox(); self.inp_start.setRange(8, 20); self.inp_start.setSuffix(":00"); self.inp_start.setPrefix("Start: ")
        self.inp_end = QSpinBox(); self.inp_end.setRange(9, 21); self.inp_end.setSuffix(":00"); self.inp_end.setPrefix("End: ")
        col2.addWidget(QLabel("Schedule"))
        col2.addWidget(self.inp_day)
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
            
            # Update Card Labels (2nd item in layout is value label)
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

    def handle_add_course(self):
        # Gather Data
        code = self.inp_code.text()
        name = self.inp_name.text()
        credits = self.inp_credits.value()
        day = self.inp_day.currentText()
        start = self.inp_start.value()
        end = self.inp_end.value()
        room = self.inp_room.text()
        cap = self.inp_cap.value()

        # Call Logic
        success, msg = self.admin_logic.add_course(code, name, credits, day, start, end, room, cap, [])
        
        if success:
            QMessageBox.information(self, "Success", "Course Added Successfully")
            self.load_courses()
            self.load_dashboard_stats()
            # Clear Inputs
            self.inp_code.clear()
            self.inp_name.clear()
            self.inp_room.clear()
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
            else:
                QMessageBox.warning(self, "Error", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = AdminDashboard()
    window.show()
    sys.exit(app.exec_())
