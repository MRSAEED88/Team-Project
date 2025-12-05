import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QMessageBox, QTableWidget, QTableWidgetItem, 
                             QTabWidget, QHeaderView, QFormLayout, QComboBox, QCheckBox, 
                             QGroupBox)  
from PyQt5.QtCore import Qt

# Import your backend modules
import users_db
from Student import Student
from Admin import Admin
from registration_system import RegistrationValidator

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECE Registration System - Login")
        self.setGeometry(100, 100, 400, 300)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("Course Registration System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title)

        # Input Fields
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Student ID or Admin Email")
        layout.addWidget(self.user_input)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.pass_input)

        # Login Button
        btn_login = QPushButton("Login")
        btn_login.setStyleSheet("background-color: #007BFF; color: white; padding: 10px; border-radius: 5px;")
        btn_login.clicked.connect(self.handle_login)
        layout.addWidget(btn_login)

        self.setLayout(layout)

    def handle_login(self):
        user_id_input = self.user_input.text()
        password = self.pass_input.text()

        if not user_id_input or not password:
            QMessageBox.warning(self, "Error", "Please enter ID/Email and Password")
            return

        # 1. Search in Users Table
        # We try searching by ID first (for students)
        try:
            user_data = users_db.search(user_id_input, table="users", search_by="id").fetch()
            
            # If not found by ID, try email (for admins)
            if not user_data:
                user_data = users_db.search(user_id_input, table="users", search_by="email").fetch()

            if user_data:
                # user_data = (id, name, email, password, membership)
                db_pass = user_data[3]
                role = user_data[4]
                user_id = user_data[0]
                name = user_data[1]
                email = user_data[2]

                # Simple password check (replace with bcrypt check in production)
                if password == db_pass:
                    self.open_dashboard(role, user_id, name, email, password)
                else:
                    QMessageBox.warning(self, "Error", "Incorrect Password")
            else:
                 QMessageBox.warning(self, "Error", "User not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database Connection Failed: {e}")

    def open_dashboard(self, role, user_id, name, email, password):
        self.hide()
        if role.lower() == "student":
            # Fetch extra student details (program, level) from students table
            student_data = users_db.search(user_id, table="students", search_by="id").fetch()
            if student_data:
                # student_data = (id, name, email, program, level)
                program = student_data[3]
                level = student_data[4]
                
                current_student = Student(user_id, name, email, program, level, password)
                self.dash = StudentDashboard(current_student)
                self.dash.show()
            else:
                QMessageBox.critical(self, "Error", "Student record missing details.")
                self.show()

        elif role.lower() == "admin":
            current_admin = Admin(user_id, name, email, password)
            self.dash = AdminDashboard(current_admin)
            self.dash.show()

class StudentDashboard(QMainWindow):
    def __init__(self, student_obj):
        super().__init__()
        self.student = student_obj
        self.setWindowTitle(f"Student Dashboard - {self.student.name} ({self.student.program})")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    def initUI(self):
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Header Info
        info_label = QLabel(f"Welcome, {self.student.name} | Program: {self.student.program} | Level: {self.student.level}")
        info_label.setStyleSheet("font-weight: bold; padding: 10px; background-color: #f0f0f0;")
        main_layout.addWidget(info_label)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # --- Tab 1: Registration ---
        self.tab_register = QWidget()
        self.setup_registration_tab()
        self.tabs.addTab(self.tab_register, "Register for Courses")

        # --- Tab 2: My Schedule ---
        self.tab_schedule = QWidget()
        self.setup_schedule_tab()
        self.tabs.addTab(self.tab_schedule, "My Schedule")

        # --- Tab 3: Transcript ---
        self.tab_transcript = QWidget()
        self.setup_transcript_tab()
        self.tabs.addTab(self.tab_transcript, "Academic History")

    def setup_registration_tab(self):
        layout = QVBoxLayout()
        
        # Instructions
        layout.addWidget(QLabel("Select courses to register for next semester:"))

        # Table of available courses
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(7)
        self.course_table.setHorizontalHeaderLabels(["Select", "Code", "Name", "Credits", "Day/Time", "Room", "Prereqs"])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.course_table)

        # Load courses
        self.load_available_courses()

        # Action Buttons
        btn_validate = QPushButton("Validate & Register")
        btn_validate.setStyleSheet("background-color: #28a745; color: white; padding: 10px;")
        btn_validate.clicked.connect(self.process_registration)
        layout.addWidget(btn_validate)

        self.tab_register.setLayout(layout)

    def load_available_courses(self):
        print("DEBUG: Loading all courses...") # Check your terminal for this
        
        # 1. Fetch all courses (metadata)
        all_courses = users_db.get_all_courses() 
        all_data = users_db.get_all_courses_data() 
        
        # DEBUG PRINT: See what the database actually returns
        print(f"DEBUG: Found {len(all_courses)} courses in database.")

        self.course_table.setRowCount(0)
        
        for row_idx, course in enumerate(all_courses):
            # course tuple: (code, name, credits, capacity, day, start, end, room)
            code = course[0]
            name = course[1]
            credits = course[2]
            day_time = f"{course[4]} {course[5]}-{course[6]}"
            room = course[7]
            
            # Format prerequisites
            prereqs = all_data.get(code, {}).get("prerequisites", [])
            prereq_str = ", ".join(prereqs)

            # Insert Row
            self.course_table.insertRow(row_idx)

            # Add Checkbox
            chk_widget = QWidget()
            chk = QCheckBox()
            chk.setProperty("course_code", code)
            chk_layout = QHBoxLayout(chk_widget)
            chk_layout.addWidget(chk)
            chk_layout.setAlignment(Qt.AlignCenter)
            chk_layout.setContentsMargins(0,0,0,0)
            
            self.course_table.setCellWidget(row_idx, 0, chk_widget)
            self.course_table.setItem(row_idx, 1, QTableWidgetItem(str(code)))
            self.course_table.setItem(row_idx, 2, QTableWidgetItem(str(name)))
            self.course_table.setItem(row_idx, 3, QTableWidgetItem(str(credits)))
            self.course_table.setItem(row_idx, 4, QTableWidgetItem(day_time))
            self.course_table.setItem(row_idx, 5, QTableWidgetItem(str(room)))
            self.course_table.setItem(row_idx, 6, QTableWidgetItem(prereq_str))
            
        print("DEBUG: Table populated.")
    def process_registration(self):
        selected_courses = []
        for i in range(self.course_table.rowCount()):
            widget = self.course_table.cellWidget(i, 0)
            checkbox = widget.findChild(QCheckBox)
            if checkbox.isChecked():
                selected_courses.append(checkbox.property("course_code"))

        if not selected_courses:
            QMessageBox.warning(self, "Warning", "No courses selected.")
            return

        # --- Use RegistrationValidator Logic ---
        # 1. Gather Data
        courses_data = users_db.get_all_courses_data()
        program_plan = users_db.get_full_program_plan()
        current_enrollments = users_db.get_current_enrollments()
        completed_courses = self.student.load_transcript()

        # 2. Initialize Validator
        validator = RegistrationValidator(courses_data, program_plan)

        # 3. Validate
        valid, message = validator.validate_registration(
            selected_courses, 
            completed_courses, 
            self.student.program, 
            self.student.level, 
            current_enrollments
        )

        # --- THIS IS WHERE YOUR NEW CODE GOES ---
        if valid:
            # 4. Save to Database if valid
            try:
                for code in selected_courses:
                    users_db.register_course_for_student(self.student.user_id, code)
                
                QMessageBox.information(self, "Success", "Registration Successful!\nCheck your schedule tab.")
                self.load_schedule() # Refresh schedule tab
                self.load_available_courses() # Reset table
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
        else:
            # Check if the failure is due to capacity
            if "is full" in message:
                reply = QMessageBox.question(self, "Course Full", 
                                             f"{message}\nWould you like to join the waitlist?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    # Try to find which course caused the error
                    for code in selected_courses:
                        if code in message: 
                             users_db.add_to_waitlist(self.student.user_id, code)
                             QMessageBox.information(self, "Waitlist", f"Added to waitlist for {code}")
            else:
                QMessageBox.critical(self, "Registration Failed", message)
    def setup_schedule_tab(self):
        layout = QVBoxLayout()
        self.schedule_list = QTableWidget()
        self.schedule_list.setColumnCount(4)
        self.schedule_list.setHorizontalHeaderLabels(["Course", "Time", "Room", "Status"])
        self.schedule_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.schedule_list)
        
        btn_refresh = QPushButton("Refresh Schedule")
        btn_refresh.clicked.connect(self.load_schedule)
        layout.addWidget(btn_refresh)
        
        self.tab_schedule.setLayout(layout)
        # Initial load
        self.load_schedule()

    def load_schedule(self):
        registered_codes = users_db.get_registered_courses(self.student.user_id)
        courses_info = users_db.get_all_courses_data()
        
        self.schedule_list.setRowCount(0)
        for row, code in enumerate(registered_codes):
            if code in courses_info:
                data = courses_info[code]
                sched = data['schedule'][0] # (Day, Start, End)
                time_str = f"{sched[0]} {sched[1]}-{sched[2]}"
                
                self.schedule_list.insertRow(row)
                self.schedule_list.setItem(row, 0, QTableWidgetItem(code))
                self.schedule_list.setItem(row, 1, QTableWidgetItem(time_str))
                self.schedule_list.setItem(row, 2, QTableWidgetItem("TBD")) # Room logic needs update in users_db if missing
                self.schedule_list.setItem(row, 3, QTableWidgetItem("Registered"))

    def setup_transcript_tab(self):
        layout = QVBoxLayout()
        
        # Transcript Table
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(3)
        self.trans_table.setHorizontalHeaderLabels(["Course Code", "Grade", "Status"])
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.trans_table)
        
        # Refresh Button
        btn_refresh = QPushButton("Refresh Transcript")
        btn_refresh.clicked.connect(self.load_transcript_view)
        layout.addWidget(btn_refresh)
        
        self.tab_transcript.setLayout(layout)
        
        # Load data immediately
        self.load_transcript_view()

    def load_transcript_view(self):
        # We need to fetch transcripts. 
        # Note: You need a get_transcript_details(student_id) function in users_db
        # For now, let's assume we use the existing 'get_completed_courses' and assume a grade
        
        completed = self.student.load_transcript() # This returns a Set of codes e.g. {'EE250', 'MATH202'}
        
        self.trans_table.setRowCount(0)
        for row, code in enumerate(completed):
            self.trans_table.insertRow(row)
            self.trans_table.setItem(row, 0, QTableWidgetItem(code))
            self.trans_table.setItem(row, 1, QTableWidgetItem("Pass")) # Placeholder grade
            self.trans_table.setItem(row, 2, QTableWidgetItem("Completed"))

class AdminDashboard(QMainWindow):
    def __init__(self, admin_obj):
        super().__init__()
        self.admin = admin_obj
        self.setWindowTitle("Admin Dashboard - Course Management")
        self.setGeometry(100, 100, 900, 600)
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        title = QLabel(f"Logged in as: {self.admin.name} (Administrator)")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        main_layout.addWidget(title)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # ---------------------------
        # Tab 1: Add New Course
        # ---------------------------
        self.tab_add_course = QWidget()
        self.setup_add_course_tab()
        self.tabs.addTab(self.tab_add_course, "1. Add New Course")

        # ---------------------------
        # Tab 2: Manage Courses (NEW)
        # ---------------------------
        self.tab_manage = QWidget()
        self.setup_manage_tab()
        self.tabs.addTab(self.tab_manage, "2. Manage Courses")

        # ---------------------------
        # Tab 3: Assign Course to Program
        # ---------------------------
        self.tab_program_plan = QWidget()
        self.setup_program_plan_tab()
        self.tabs.addTab(self.tab_program_plan, "3. Assign Course to Program")

        # ---------------------------
        # Tab 4: Student Accounts (NEW)
        # ---------------------------
        self.tab_students = QWidget()
        self.setup_students_tab()
        self.tabs.addTab(self.tab_students, "4. Student Accounts")

    # ============================================================
    # TAB 1 — ADD COURSE (unchanged)
    # ============================================================
    def setup_add_course_tab(self):
        layout = QFormLayout()

        self.c_code = QLineEdit()
        self.c_name = QLineEdit()
        self.c_credits = QLineEdit()

        self.c_day = QComboBox()
        self.c_day.addItems(["Sun", "Mon", "Tue", "Wed", "Thu"])

        self.c_start = QLineEdit()
        self.c_start.setPlaceholderText("HH:MM")
        self.c_end = QLineEdit()
        self.c_end.setPlaceholderText("HH:MM")
        self.c_room = QLineEdit()
        self.c_cap = QLineEdit()
        self.c_prereqs = QLineEdit()
        self.c_prereqs.setPlaceholderText("EE201,EE250")

        layout.addRow("Course Code:", self.c_code)
        layout.addRow("Course Name:", self.c_name)
        layout.addRow("Credits:", self.c_credits)
        layout.addRow("Day:", self.c_day)
        layout.addRow("Start Time:", self.c_start)
        layout.addRow("End Time:", self.c_end)
        layout.addRow("Room:", self.c_room)
        layout.addRow("Capacity:", self.c_cap)
        layout.addRow("Prerequisites:", self.c_prereqs)

        btn = QPushButton("Add Course")
        btn.clicked.connect(self.submit_course)
        layout.addRow(btn)

        self.tab_add_course.setLayout(layout)

    def submit_course(self):
        try:
            code = self.c_code.text().strip()
            name = self.c_name.text().strip()
            credits = int(self.c_credits.text())
            day = self.c_day.currentText()
            start = self.c_start.text().strip()
            end = self.c_end.text().strip()
            room = self.c_room.text().strip()
            cap = int(self.c_cap.text())
            prereqs = [x.strip() for x in self.c_prereqs.text().split(",") if x.strip()]

            success, msg = self.admin.add_course(code, name, credits, day, start, end, room, cap, prerequisites=prereqs)

            if success:
                QMessageBox.information(self, "Success", msg)
                self.load_courses_table()
            else:
                QMessageBox.warning(self, "Error", msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ============================================================
    # TAB 2 — MANAGE COURSES (NEW)
    # ============================================================
    def setup_manage_tab(self):
        layout = QVBoxLayout()

        # Table of courses
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(8)
        self.course_table.setHorizontalHeaderLabels(
            ["Code", "Name", "Credits", "Day", "Start", "End", "Room", "Capacity"]
        )
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.course_table)

        btn_refresh = QPushButton("Refresh Course List")
        btn_refresh.clicked.connect(self.load_courses_table)
        layout.addWidget(btn_refresh)

        # -------------------
        # Update section
        # -------------------
        update_box = QGroupBox("Update Course")
        update_form = QFormLayout()

        self.u_code = QLineEdit()
        self.u_name = QLineEdit()
        self.u_credits = QLineEdit()
        self.u_day = QLineEdit()
        self.u_start = QLineEdit()
        self.u_end = QLineEdit()
        self.u_room = QLineEdit()
        self.u_cap = QLineEdit()

        update_form.addRow("Course Code:", self.u_code)
        update_form.addRow("New Name:", self.u_name)
        update_form.addRow("New Credits:", self.u_credits)
        update_form.addRow("New Day:", self.u_day)
        update_form.addRow("New Start:", self.u_start)
        update_form.addRow("New End:", self.u_end)
        update_form.addRow("New Room:", self.u_room)
        update_form.addRow("New Capacity:", self.u_cap)

        btn_upd = QPushButton("Apply Update")
        btn_upd.clicked.connect(self.submit_update)
        update_form.addRow(btn_upd)

        update_box.setLayout(update_form)
        layout.addWidget(update_box)

        # -------------------
        # Delete section
        # -------------------
        del_box = QGroupBox("Delete Course")
        del_form = QFormLayout()

        self.d_code = QLineEdit()
        btn_del = QPushButton("Delete Course")
        btn_del.clicked.connect(self.submit_delete)

        del_form.addRow("Course Code:", self.d_code)
        del_form.addRow(btn_del)

        del_box.setLayout(del_form)
        layout.addWidget(del_box)

        self.tab_manage.setLayout(layout)
        self.load_courses_table()

    def load_courses_table(self):
        data = self.admin.view_all_courses()
        if not data or isinstance(data, tuple):
            return
        
        self.course_table.setRowCount(0)
        for i, row in enumerate(data):
            self.course_table.insertRow(i)
            for j in range(1, 9):  # skip id
                self.course_table.setItem(i, j-1, QTableWidgetItem(str(row[j])))

    def submit_update(self):
        code = self.u_code.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Course code is required.")
            return

        updates = {}
        if self.u_name.text(): updates["name"] = self.u_name.text().strip()
        if self.u_credits.text(): updates["credits"] = int(self.u_credits.text())
        if self.u_day.text(): updates["day"] = self.u_day.text().strip()
        if self.u_start.text(): updates["start_time"] = self.u_start.text().strip()
        if self.u_end.text(): updates["end_time"] = self.u_end.text().strip()
        if self.u_room.text(): updates["room"] = self.u_room.text().strip()
        if self.u_cap.text(): updates["max_capacity"] = int(self.u_cap.text())

        success, msg = self.admin.update_course(code, **updates)
        QMessageBox.information(self, "Status", msg)
        self.load_courses_table()

    def submit_delete(self):
        code = self.d_code.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Course code required.")
            return

        success, msg = self.admin.delete_course(code)
        QMessageBox.information(self, "Status", msg)
        self.load_courses_table()

    # ============================================================
    # TAB 3 — PROGRAM PLAN (your original code kept)
    # ============================================================
    def setup_program_plan_tab(self):
        layout = QFormLayout()

        self.plan_program = QComboBox()
        self.plan_program.addItems(["Computer", "Comm", "Power", "Biomedical"])

        self.plan_level = QComboBox()
        self.plan_level.addItems([str(i) for i in range(1, 11)])

        self.plan_course = QLineEdit()

        btn_assign = QPushButton("Add to Plan")
        btn_assign.clicked.connect(self.submit_plan)

        layout.addRow("Program:", self.plan_program)
        layout.addRow("Level:", self.plan_level)
        layout.addRow("Course Code:", self.plan_course)
        layout.addRow(btn_assign)

        self.tab_program_plan.setLayout(layout)

    def submit_plan(self):
        program = self.plan_program.currentText()
        level = int(self.plan_level.currentText())
        course_code = self.plan_course.text().strip()

        success, msg = self.admin.define_program_plan(program, level, [course_code])
        QMessageBox.information(self, "Status", msg)

    # ============================================================
    # TAB 4 — STUDENT ACCOUNTS (NEW)
    # ============================================================
    def setup_students_tab(self):
        layout = QFormLayout()

        self.s_name = QLineEdit()
        self.s_email = QLineEdit()
        self.s_pass = QLineEdit()
        self.s_pass.setEchoMode(QLineEdit.Password)

        self.s_prog = QComboBox()
        self.s_prog.addItems(["Computer", "Comm", "Power", "Biomedical"])

        self.s_lvl = QComboBox()
        self.s_lvl.addItems([str(i) for i in range(1, 11)])

        btn_add = QPushButton("Create Student")
        btn_add.clicked.connect(self.add_student)

        layout.addRow("Name:", self.s_name)
        layout.addRow("Email:", self.s_email)
        layout.addRow("Password:", self.s_pass)
        layout.addRow("Program:", self.s_prog)
        layout.addRow("Level:", self.s_lvl)
        layout.addRow(btn_add)

        # Delete student
        self.s_delete = QLineEdit()
        btn_del = QPushButton("Delete Student")
        btn_del.clicked.connect(self.delete_student)
        layout.addRow("Student ID:", self.s_delete)
        layout.addRow(btn_del)

        self.tab_students.setLayout(layout)

    def add_student(self):
        success, msg = self.admin.create_student_account(
            self.s_name.text(), self.s_email.text(), self.s_pass.text(),
            self.s_prog.currentText(), int(self.s_lvl.currentText())
        )
        QMessageBox.information(self, "Status", msg)

    def delete_student(self):
        try:
            sid = int(self.s_delete.text())
        except:
            QMessageBox.warning(self, "Error", "Invalid ID.")
            return

        success, msg = self.admin.delete_student(sid)
        QMessageBox.information(self, "Status", msg)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize DB (creates tables if missing)
    users_db.setup_database()
    
    # Start Login Window
    login = LoginWindow()
    login.show()
    
    sys.exit(app.exec_())
