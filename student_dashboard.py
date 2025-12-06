import sys
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
                             QAbstractItemView, QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

# --- IMPORTS ---
from registration_system import RegistrationSystem
from Student import Student
import users_db

# =============================================================================
# TAB 1: OVERVIEW (GPA & Stats)
# =============================================================================
class OverviewTab(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dash = parent_dashboard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Dashboard Overview")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        cards = QHBoxLayout()
        cards.setSpacing(20)
        self.card_gpa = self.create_card("GPA", "0.00 / 5.00", "#27ae60")
        self.card_credits = self.create_card("Registered Credits", "0 / 18", "#2980b9")
        self.card_status = self.create_card("Academic Status", "Regular", "#f39c12")
        
        cards.addWidget(self.card_gpa)
        cards.addWidget(self.card_credits)
        cards.addWidget(self.card_status)
        layout.addLayout(cards)
        layout.addStretch()

    def create_card(self, title, value, color):
        card = QFrame()
        card.setProperty("class", "card")
        card.setStyleSheet(f"border-top: 4px solid {color}; background: white; border-radius: 8px;")
        
        l = QVBoxLayout(card)
        l.setContentsMargins(20, 20, 20, 20)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #7f8c8d; font-size: 14px; font-weight: bold;")
        
        lbl_value = QLabel(value)
        lbl_value.setStyleSheet("color: #2c3e50; font-size: 28px; font-weight: bold;")
        
        l.addWidget(lbl_title)
        l.addWidget(lbl_value)
        return card

    def refresh(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            cur.execute("SELECT course_code, grade FROM transcripts WHERE student_id = ? AND grade != 'IP'", (self.dash.user_id,))
            rows = cur.fetchall()
            con.close()

            pts = 0; creds = 0
            pmap = {"A+":5.00, "A":4.75, "B+":4.50, "B":4.00, "C+":3.50, "C":3.00, "D+":2.50, "D":2.00, "F":1.00}
            
            for code, grade in rows:
                if grade.upper() in pmap:
                    c_cred = 0
                    for db_code, data in self.dash.logic_system.courses_data.items():
                        if str(db_code).replace(" ","").upper() == str(code).replace(" ","").upper():
                            c_cred = data.get('credits', 0); break
                    if c_cred: pts += pmap[grade.upper()] * c_cred; creds += c_cred
            
            gpa = pts / creds if creds > 0 else 0.0
            self.card_gpa.layout().itemAt(1).widget().setText(f"{gpa:.2f}")
        except: pass

# =============================================================================
# TAB 2: REGISTRATION (With Plan Filtering)
# =============================================================================
class RegistrationTab(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dash = parent_dashboard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        h = QHBoxLayout()
        title = QLabel("Available Courses")
        title.setProperty("class", "page-title") 
        h.addWidget(title)
        h.addStretch()
        
        btn = QPushButton("Refresh Data")
        btn.clicked.connect(self.dash.refresh_ui)
        h.addWidget(btn)
        layout.addLayout(h)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Code", "Name", "Credits", "Time", "Room", "Prereqs", "Cap"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        layout.addWidget(self.table)

        btn_reg = QPushButton("Register Selected")
        btn_reg.setProperty("class", "action-btn")
        btn_reg.clicked.connect(self.register)
        layout.addWidget(btn_reg, alignment=Qt.AlignRight)

    def refresh(self):
        self.table.setRowCount(0)
        if not self.dash.student_obj: return

        courses = self.dash.logic_system.courses_data
        
        try: completed = users_db.get_completed_courses(self.dash.user_id)
        except: completed = set()

        user_program = self.dash.student_obj.program
        plan_dict = self.dash.logic_system.program_plan.get(user_program, {})
        allowed_courses = set()
        for level_list in plan_dict.values():
            for code in level_list: allowed_courses.add(code)

        for c, d in courses.items():
            if c in completed: continue
            if c not in allowed_courses: continue
            
            name = d.get('name', 'Unknown')
            creds = str(d.get('credits', 0))
            room = d.get('room', 'TBA')
            cap = d.get('max_capacity', 0)
            prereq = ", ".join(d.get('prerequisites', [])) or "-"
            
            sch = d.get('schedule', [])
            time = "TBA"
            if sch and len(sch[0]) >= 3: time = f"{sch[0][0]} {sch[0][1]}-{sch[0][2]}"
            elif d.get('day') and d.get('start_time'): 
                time = f"{d['day']} {d['start_time']}" + (f"-{d['end_time']}" if d.get('end_time') else "")

            curr = 0
            try:
                con = sqlite3.connect("User.db")
                curr = con.execute("SELECT COUNT(*) FROM registration WHERE course_code=?", (c,)).fetchone()[0]
                con.close()
            except: pass

            row = self.table.rowCount()
            self.table.insertRow(row)
            for i, txt in enumerate([c, name, creds, time, room, prereq, f"{curr}/{cap}"]):
                self.table.setItem(row, i, QTableWidgetItem(str(txt)))

    def register(self):
        r = self.table.currentRow()
        if r < 0: return QMessageBox.warning(self, "Warning", "Select a course.")
        code = self.table.item(r, 0).text()
        
        if code in self.dash.logic_system.get_student_registered_courses(self.dash.student_obj):
            return QMessageBox.warning(self, "Warning", "Already registered.")

        ok, msg = self.dash.logic_system.register_courses_for_student(self.dash.student_obj, [code])
        if ok: QMessageBox.information(self, "Info", msg)
        else: QMessageBox.warning(self, "Error", msg)
        self.dash.refresh_ui()

# =============================================================================
# TAB 3: SCHEDULE (Visual & Lists)
# =============================================================================
# [In student_dashboard.py]

class ScheduleTab(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dash = parent_dashboard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl_vis = QLabel("Visual Timetable")
        lbl_vis.setProperty("class", "section-title")
        layout.addWidget(lbl_vis)
        
        self.cal = QTableWidget(11, 5)
        self.cal.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu"])
        self.cal.setVerticalHeaderLabels([f"{h}:00" for h in range(8, 19)])
        self.cal.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cal.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cal.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.cal.setMinimumHeight(300)
        layout.addWidget(self.cal)

        lbl_reg = QLabel("Registered Courses")
        lbl_reg.setProperty("class", "section-title")
        layout.addWidget(lbl_reg)
        
        self.list = QTableWidget(0, 4)
        self.list.setHorizontalHeaderLabels(["Code", "Name", "Time", "Room"])
        self.list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.list.setFixedHeight(100)
        layout.addWidget(self.list)
        
        btn_drop = QPushButton("Drop Course")
        btn_drop.setProperty("class", "danger-btn")
        btn_drop.clicked.connect(self.drop)
        layout.addWidget(btn_drop)

        lbl_wait = QLabel("Waitlist Position")
        lbl_wait.setProperty("class", "section-title")
        layout.addWidget(lbl_wait)
        
        self.wait = QTableWidget(0, 4)
        self.wait.setHorizontalHeaderLabels(["Code", "Name", "Requested", "Position"])
        self.wait.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.wait.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.wait.setFixedHeight(100)
        layout.addWidget(self.wait)
        
        btn_leave = QPushButton("Leave Waitlist")
        btn_leave.setProperty("class", "warning-btn")
        btn_leave.clicked.connect(self.leave)
        layout.addWidget(btn_leave)

    def refresh(self):
        self.cal.clearContents()
        self.list.setRowCount(0)
        self.wait.setRowCount(0)
        if not self.dash.student_obj: return

        my_codes = self.dash.logic_system.get_student_registered_courses(self.dash.student_obj)
        data = self.dash.logic_system.courses_data
        colors = ["#e74c3c", "#3498db", "#2ecc71", "#9b59b6", "#f1c40f", "#e67e22"]
        
        # Mapping for day names
        d_map = {"Sunday":0, "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, 
                 "Sun":0, "Mon":1, "Tue":2, "Wed":3, "Thu":4}
        
        color_i = 0
        tot_creds = 0

        for c in my_codes:
            d = data.get(c, {})
            name = d.get('name', 'Unknown')
            room = d.get('room', 'TBA')
            tot_creds += d.get('credits', 0)
            
            # 1. Get the raw day string (e.g., "Sun, Tue" or "Mon/Wed")
            raw_day_str = str(d.get('day', '')).strip()
            start = d.get('start_time')
            end = d.get('end_time')

            # List View Update
            r = self.list.rowCount()
            self.list.insertRow(r)
            self.list.setItem(r, 0, QTableWidgetItem(str(c)))
            self.list.setItem(r, 1, QTableWidgetItem(name))
            self.list.setItem(r, 2, QTableWidgetItem(f"{raw_day_str} {start}"))
            self.list.setItem(r, 3, QTableWidgetItem(room))

            # 2. Calendar View Update (The Fix)
            if start and end:
                # Normalize separators: replace '/' with ',' just in case CSV used slashes
                normalized_days = raw_day_str.replace('/', ',')
                
                # Split into a list: "Sun, Tue" -> ["Sun", "Tue"]
                day_list = [x.strip() for x in normalized_days.split(',')]

                for single_day in day_list:
                    if single_day in d_map:
                        try:
                            col = d_map[single_day]
                            # Calculate Start Row (assuming 8:00 is index 0)
                            s_hour = int(str(start).split(':')[0])
                            row_s = s_hour - 8
                            
                            # Calculate Duration
                            e_hour = int(str(end).split(':')[0])
                            dur = e_hour - s_hour
                            if dur < 1: dur = 1 # Minimum 1 hour block
                            
                            # Paint Cells
                            if 0 <= row_s < 11:
                                item = QTableWidgetItem(f"{c}\n{room}")
                                item.setBackground(QBrush(QColor(colors[color_i % 6])))
                                item.setForeground(QBrush(Qt.white))
                                item.setTextAlignment(Qt.AlignCenter)
                                
                                # Loop to fill duration (e.g. 2 hour lab)
                                for i in range(dur):
                                    if row_s + i < 11: 
                                        self.cal.setItem(row_s + i, col, QTableWidgetItem(item))
                        except Exception as e:
                            print(f"Error drawing {c} on {single_day}: {e}")
                
                color_i += 1
        
        # Update Total Credits in Overview
        try:
            self.dash.tab_overview.card_credits.layout().itemAt(1).widget().setText(f"{tot_creds} / 18")
        except: pass

        # Load Waitlist Data
        con = sqlite3.connect("User.db")
        cur = con.cursor()
        cur.execute("SELECT course_code, timestamp FROM waitlist WHERE student_id=?", (self.dash.user_id,))
        for c, ts in cur.fetchall():
            pos = con.execute("SELECT COUNT(*) FROM waitlist WHERE course_code=? AND timestamp <= ?", (c, ts)).fetchone()[0]
            name = data.get(c, {}).get('name', 'Unknown')
            r = self.wait.rowCount()
            self.wait.insertRow(r)
            for i, txt in enumerate([c, name, ts, f"#{pos}"]): self.wait.setItem(r, i, QTableWidgetItem(str(txt)))
        con.close()

    def drop(self):
        r = self.list.currentRow()
        if r < 0: return QMessageBox.warning(self, "Msg", "Select course to drop.")
        code = self.list.item(r, 0).text()
        ok, msg = self.dash.logic_system.drop_course_for_student(self.dash.student_obj, code)
        QMessageBox.information(self, "Info", msg)
        self.dash.refresh_ui()

    def leave(self):
        r = self.wait.currentRow()
        if r < 0: return QMessageBox.warning(self, "Msg", "Select course to leave.")
        code = self.wait.item(r, 0).text()
        with sqlite3.connect("User.db") as con:
            con.execute("DELETE FROM waitlist WHERE student_id=? AND course_code=?", (self.dash.user_id, code))
        QMessageBox.information(self, "Info", "Left waitlist.")
        self.dash.refresh_ui()

# =============================================================================
# TAB 6: SETTINGS (NEW PROFILE MAINTENANCE)
# =============================================================================
class SettingsTab(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dash = parent_dashboard
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("Account Settings")
        title.setProperty("class", "page-title")
        layout.addWidget(title)

        # Email
        layout.addWidget(QLabel("Update Email", styleSheet="font-weight:bold; font-size:14px; margin-top:10px;"))
        self.inp_email = QLineEdit()
        self.inp_email.setPlaceholderText("New email")
        layout.addWidget(self.inp_email)
        
        btn_email = QPushButton("Save New Email")
        btn_email.setProperty("class", "action-btn")
        btn_email.clicked.connect(self.update_email)
        layout.addWidget(btn_email)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #ccc; margin: 20px 0;")
        layout.addWidget(line)

        # Password
        layout.addWidget(QLabel("Change Password", styleSheet="font-weight:bold; font-size:14px;"))
        self.inp_old = QLineEdit(); self.inp_old.setPlaceholderText("Current Password"); self.inp_old.setEchoMode(QLineEdit.Password)
        self.inp_new = QLineEdit(); self.inp_new.setPlaceholderText("New Password"); self.inp_new.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.inp_old)
        layout.addWidget(self.inp_new)

        btn_pass = QPushButton("Update Password")
        btn_pass.setProperty("class", "warning-btn")
        btn_pass.clicked.connect(self.update_password)
        layout.addWidget(btn_pass)
        layout.addStretch()

    def refresh(self):
        if self.dash.student_obj:
            self.inp_email.setText(self.dash.student_obj.email)

    def update_email(self):
        new_e = self.inp_email.text().strip()
        if not new_e: return
        try:
            con = sqlite3.connect("User.db")
            con.execute("UPDATE users SET email=? WHERE id=?", (new_e, self.dash.user_id))
            con.execute("UPDATE students SET email=? WHERE id=?", (new_e, self.dash.user_id))
            con.commit(); con.close()
            self.dash.student_obj.email = new_e
            QMessageBox.information(self, "Success", "Email updated.")
        except Exception as e: QMessageBox.warning(self, "Error", str(e))

    def update_password(self):
        old, new = self.inp_old.text(), self.inp_new.text()
        if not old or not new: return QMessageBox.warning(self, "Input", "Fill all fields.")
        try:
            con = sqlite3.connect("User.db")
            real = con.execute("SELECT password FROM users WHERE id=?", (self.dash.user_id,)).fetchone()[0]
            if real == old:
                con.execute("UPDATE users SET password=? WHERE id=?", (new, self.dash.user_id))
                con.commit(); QMessageBox.information(self, "Success", "Password updated.")
                self.inp_old.clear(); self.inp_new.clear()
            else: QMessageBox.warning(self, "Error", "Incorrect current password.")
            con.close()
        except Exception as e: QMessageBox.warning(self, "Error", str(e))

# =============================================================================
# MAIN WINDOW CLASS
# =============================================================================
class StudentDashboard(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        self.student_obj = None  
        self.setWindowTitle("KAU Student Portal | Fall 2025")
        self.resize(1100, 800)

        self.logic_system = RegistrationSystem()

        cw = QWidget(); self.setCentralWidget(cw)
        main_layout = QHBoxLayout(cw); main_layout.setContentsMargins(0,0,0,0); main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        sl = QVBoxLayout(sidebar)
        
        logo = QLabel("KAU Portal")
        logo.setObjectName("LogoLabel")
        sl.addWidget(logo)
        
        self.stack = QStackedWidget()
        
        # Tabs
        self.tab_overview = OverviewTab(self)
        self.tab_register = RegistrationTab(self)
        self.tab_schedule = ScheduleTab(self)
        
        self.tab_trans = QWidget(); tl = QVBoxLayout(self.tab_trans)
        tl.setContentsMargins(30,30,30,30)
        tl_title = QLabel("Transcript"); tl_title.setProperty("class", "page-title"); tl.addWidget(tl_title)
        self.tbl_trans = QTableWidget(0,4); self.tbl_trans.setHorizontalHeaderLabels(["Code","Name","Credits","Grade"]); self.tbl_trans.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); tl.addWidget(self.tbl_trans)
        
        self.tab_plan = QWidget(); pl = QVBoxLayout(self.tab_plan)
        pl.setContentsMargins(30,30,30,30)
        pl_title = QLabel("Program Plan"); pl_title.setProperty("class", "page-title"); pl.addWidget(pl_title)
        self.tbl_plan = QTableWidget(0,5); self.tbl_plan.setHorizontalHeaderLabels(["Level","Code","Name","Credits","Status"]); self.tbl_plan.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); pl.addWidget(self.tbl_plan)

        self.tab_settings = SettingsTab(self)

        for t in [self.tab_overview, self.tab_register, self.tab_schedule, self.tab_trans, self.tab_plan, self.tab_settings]:
            self.stack.addWidget(t)

        names = ["Overview", "Registration", "Schedule", "Transcript", "My Plan", "Settings"]
        self.btns = []
        for i, name in enumerate(names):
            b = QPushButton(name)
            b.setCheckable(True)
            b.setAutoExclusive(True)
            b.setProperty("class", "nav-btn")
            b.clicked.connect(lambda _, x=i: self.switch(x))
            sl.addWidget(b); self.btns.append(b)
        
        sl.addStretch()
        self.lbl_user = QLabel("Loading...")
        self.lbl_user.setStyleSheet("color:white; padding:10px; font-weight:bold;")
        sl.addWidget(self.lbl_user)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)

        self.setup_styles()
        self.load_data()
        self.refresh_ui()
        self.btns[0].setChecked(True)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #f4f6f9; }
            QFrame#Sidebar { background-color: #2c3e50; color: white; border: none;}
            QLabel#LogoLabel { font-size: 22px; font-weight: bold; color: #ecf0f1; padding: 20px; }
            QPushButton[class="nav-btn"] {
                background-color: transparent; border: none; color: #bdc3c7;
                text-align: left; padding: 15px 25px; font-size: 14px;
                border-left: 4px solid transparent;
            }
            QPushButton[class="nav-btn"]:hover { background-color: #34495e; color: white; }
            QPushButton[class="nav-btn"]:checked { background-color: #34495e; color: white; border-left: 4px solid #3498db; }
            QLabel[class="page-title"] { font-size: 24px; font-weight: bold; color: #2c3e50; margin-bottom: 10px; }
            QLabel[class="section-title"] { font-size: 16px; font-weight: bold; color: #7f8c8d; margin-top: 15px; }
            QPushButton[class="action-btn"] { background-color: #2980b9; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="danger-btn"] { background-color: #c0392b; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
            QPushButton[class="warning-btn"] { background-color: #f39c12; color: white; border-radius: 4px; padding: 8px 15px; font-weight: bold; }
        """)

    def switch(self, i):
        self.stack.setCurrentIndex(i)
        self.refresh_ui()

    def load_data(self):
        try:
            con = sqlite3.connect("User.db")
            cur = con.cursor()
            row = cur.execute("SELECT name, email, program, level FROM students WHERE id=?", (self.user_id,)).fetchone()
            if not row:
                u = cur.execute("SELECT name, email FROM users WHERE id=?", (self.user_id,)).fetchone()
                if u: 
                    cur.execute("INSERT INTO students VALUES (?,?,?,?,?)", (self.user_id, u[0], u[1], "General Engineering", 1))
                    con.commit(); row = (u[0], u[1], "General Engineering", 1)
            
            if row:
                self.student_obj = Student(self.user_id, row[0], row[1], row[2], row[3], "")
                self.lbl_user.setText(f"{row[0]}\n{row[2]}")
            con.close()
        except: pass

    def refresh_ui(self):
        if not self.student_obj: return
        self.logic_system.refresh_data()
        self.tab_overview.refresh()
        self.tab_register.refresh()
        self.tab_schedule.refresh()
        self.tab_settings.refresh()
        
        self.tbl_trans.setRowCount(0)
        try:
            con = sqlite3.connect("User.db")
            for r_data in con.execute("SELECT t.course_code, c.course_name, c.credits, t.grade FROM transcripts t LEFT JOIN courses c ON t.course_code=c.course_code WHERE student_id=?", (self.user_id,)):
                row = self.tbl_trans.rowCount(); self.tbl_trans.insertRow(row)
                for i, d in enumerate(r_data): self.tbl_trans.setItem(row, i, QTableWidgetItem(str(d if d else "-")))
            con.close()
        except: pass

        self.tbl_plan.setRowCount(0)
        plan = self.logic_system.program_plan.get(self.student_obj.program, {})
        comp = set(users_db.get_completed_courses(self.user_id))
        reg = set(self.logic_system.get_student_registered_courses(self.student_obj))
        
        for lvl in sorted(plan.keys()):
            for code in plan[lvl]:
                d = self.logic_system.courses_data.get(code, {})
                st, col = ("Not Started", "#f8d7da")
                if code in reg: st, col = ("In Progress", "#cce5ff")
                elif code in comp: st, col = ("Completed", "#d4edda")
                
                r = self.tbl_plan.rowCount(); self.tbl_plan.insertRow(r)
                for i, txt in enumerate([f"Level {lvl}", code, d.get('name','-'), str(d.get('credits','-')), st]):
                    it = QTableWidgetItem(txt); 
                    if i==4: it.setBackground(QColor(col)); it.setForeground(QBrush(Qt.black))
                    self.tbl_plan.setItem(r, i, it)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = StudentDashboard(user_id=2454896)  # Example user ID
    window.show()
    sys.exit(app.exec_())
