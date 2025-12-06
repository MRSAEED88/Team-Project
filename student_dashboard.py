import sys
import sqlite3
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QStackedWidget,
                             QAbstractItemView, QMessageBox, QLineEdit, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap

# --- IMPORTS ---
from registration_system import RegistrationSystem
from Student import Student
import users_db


class SimulationLogic:
    """
    Helper logic specifically for the What-If scenarios.
    Checks for 'softer conflicts' like back-to-back classes in different rooms.
    """
    @staticmethod
    def check_soft_conflicts(courses_data, selected_codes):
        warnings = []
        
        # 1. Gather Schedule Details for selected courses
        schedule_points = []
        
        for code in selected_codes:
            data = courses_data.get(code, {})
            room = data.get('room', 'Unknown')
            schedule_list = data.get('schedule', [])
            
            for item in schedule_list:
                days_str, start_str, end_str = item
                # Handle "Sun/Tue" or "Sun, Tue"
                days = days_str.replace('/', ',').split(',')
                
                # Convert times to minutes for comparison
                try:
                    s_h, s_m = map(int, start_str.split(':'))
                    e_h, e_m = map(int, end_str.split(':'))
                    start_min = s_h * 60 + s_m
                    end_min = e_h * 60 + e_m
                    
                    for day in days:
                        schedule_points.append({
                            'day': day.strip(),
                            'start': start_min,
                            'end': end_min,
                            'room': room,
                            'code': code
                        })
                except:
                    continue

        # 2. Sort by Day, then by Start Time
        schedule_points.sort(key=lambda x: (x['day'], x['start']))

        # 3. Check for Back-to-Back (End Time A == Start Time B)
        for i in range(len(schedule_points) - 1):
            curr = schedule_points[i]
            next_c = schedule_points[i+1]
            
            # Must be same day
            if curr['day'] == next_c['day']:
                # Check for tight transition (0 to 10 minutes gap)
                gap = next_c['start'] - curr['end']
                
                if 0 <= gap <= 10:
                    # Ignore if it's the same room
                    if curr['room'] != next_c['room']:
                        warnings.append(
                            f"Tight Transition ({curr['day']}): {curr['code']} ends at "
                            f"{curr['end']//60}:{curr['end']%60:02d} in {curr['room']}, "
                            f"but {next_c['code']} starts immediately in {next_c['room']}."
                        )

        return warnings

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
# TAB 2: REGISTRATION
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
        
        current_registered = self.dash.logic_system.get_student_registered_courses(self.dash.student_obj)
        if code in current_registered:
            return QMessageBox.warning(self, "Warning", "Already registered.")

        # --- BONUS CHECK: SOFT CONFLICTS ---
        simulated_schedule = list(current_registered)
        simulated_schedule.append(code)
        warnings = SimulationLogic.check_soft_conflicts(
            self.dash.logic_system.courses_data, 
            simulated_schedule
        )
        if warnings:
            msg_text = "Soft Scheduling Conflict Detected:\n\n" + "\n".join(warnings) + "\n\nDo you still want to proceed?"
            reply = QMessageBox.question(self, "Soft Conflict Warning", msg_text, QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No: return
        # -----------------------------------

        ok, msg = self.dash.logic_system.register_courses_for_student(self.dash.student_obj, [code])
        if ok: QMessageBox.information(self, "Info", msg)
        else: QMessageBox.warning(self, "Error", msg)
        self.dash.refresh_ui()

# =============================================================================
# TAB 3: SCHEDULE (Visual & Lists)
# =============================================================================
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
        d_map = {"Sunday":0, "Monday":1, "Tuesday":2, "Wednesday":3, "Thursday":4, 
                 "Sun":0, "Mon":1, "Tue":2, "Wed":3, "Thu":4}
        color_i = 0; tot_creds = 0

        for c in my_codes:
            d = data.get(c, {})
            name = d.get('name', 'Unknown')
            room = d.get('room', 'TBA')
            tot_creds += d.get('credits', 0)
            raw_day_str = str(d.get('day', '')).strip()
            start = d.get('start_time')
            end = d.get('end_time')

            r = self.list.rowCount()
            self.list.insertRow(r)
            self.list.setItem(r, 0, QTableWidgetItem(str(c)))
            self.list.setItem(r, 1, QTableWidgetItem(name))
            self.list.setItem(r, 2, QTableWidgetItem(f"{raw_day_str} {start}"))
            self.list.setItem(r, 3, QTableWidgetItem(room))

            if start and end:
                normalized_days = raw_day_str.replace('/', ',')
                day_list = [x.strip() for x in normalized_days.split(',')]
                for single_day in day_list:
                    if single_day in d_map:
                        try:
                            col = d_map[single_day]
                            s_hour = int(str(start).split(':')[0])
                            row_s = s_hour - 8
                            e_hour = int(str(end).split(':')[0])
                            dur = e_hour - s_hour
                            if dur < 1: dur = 1
                            if 0 <= row_s < 11:
                                item = QTableWidgetItem(f"{c}\n{room}")
                                item.setBackground(QBrush(QColor(colors[color_i % 6])))
                                item.setForeground(QBrush(Qt.white))
                                item.setTextAlignment(Qt.AlignCenter)
                                for i in range(dur):
                                    if row_s + i < 11: self.cal.setItem(row_s + i, col, QTableWidgetItem(item))
                        except: pass
                color_i += 1
        
        try:
            self.dash.tab_overview.card_credits.layout().itemAt(1).widget().setText(f"{tot_creds} / 18")
        except: pass

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
# BONUS #7: WHAT-IF SCENARIO TAB (MULTI-COURSE + VISUALS)
# =============================================================================
class WhatIfTab(QWidget):
    def __init__(self, parent_dashboard):
        super().__init__()
        self.dash = parent_dashboard
        self.simulated_courses = set()  # Stores codes of temporarily selected courses

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("What-If Simulator")
        title.setProperty("class", "page-title")
        layout.addWidget(title)
        
        # 1. Controls Area
        controls_frame = QFrame()
        controls_frame.setProperty("class", "card")
        cl = QHBoxLayout(controls_frame)
        
        self.cmb_prog = QComboBox()
        self.cmb_prog.addItems(["Computer", "Comm", "Power", "Biomedical"])
        self.spin_lvl = QSpinBox()
        self.spin_lvl.setRange(1, 10)
        self.spin_lvl.setPrefix("Level ")
        btn_sim = QPushButton("Load Course Options")
        btn_sim.setProperty("class", "action-btn")
        btn_sim.clicked.connect(self.run_simulation_list)

        cl.addWidget(QLabel("Simulate Program:"))
        cl.addWidget(self.cmb_prog)
        cl.addWidget(QLabel("Simulate Level:"))
        cl.addWidget(self.spin_lvl)
        cl.addWidget(btn_sim)
        cl.addStretch()
        layout.addWidget(controls_frame)

        # 2. Main Content Area (Split: List vs Visual)
        content_split = QHBoxLayout()

        # LEFT: Course List
        list_layout = QVBoxLayout()
        lbl_list = QLabel("Click courses to add/remove from simulation:")
        lbl_list.setStyleSheet("font-weight:bold; color:#7f8c8d;")
        list_layout.addWidget(lbl_list)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Code", "Name", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumWidth(350)
        self.table.itemClicked.connect(self.toggle_course_selection)
        list_layout.addWidget(self.table)
        
        btn_clear = QPushButton("Clear Simulation")
        btn_clear.clicked.connect(self.clear_simulation)
        list_layout.addWidget(btn_clear)
        content_split.addLayout(list_layout, stretch=1)

        # RIGHT: Visual Timetable
        vis_layout = QVBoxLayout()
        lbl_vis = QLabel("Simulated Plan (Blue=Actual, Orange=Hypothetical)")
        lbl_vis.setStyleSheet("font-weight:bold; color:#7f8c8d;")
        vis_layout.addWidget(lbl_vis)

        self.sim_cal = QTableWidget(11, 5)
        self.sim_cal.setHorizontalHeaderLabels(["Sun", "Mon", "Tue", "Wed", "Thu"])
        self.sim_cal.setVerticalHeaderLabels([f"{h}:00" for h in range(8, 19)])
        self.sim_cal.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sim_cal.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sim_cal.setEditTriggers(QAbstractItemView.NoEditTriggers)
        vis_layout.addWidget(self.sim_cal)
        content_split.addLayout(vis_layout, stretch=2)

        layout.addLayout(content_split)

        # 3. Conflict Button
        btn_check = QPushButton("Analyze Full Plan for Conflicts")
        btn_check.setProperty("class", "warning-btn")
        btn_check.clicked.connect(self.check_full_plan_conflicts)
        layout.addWidget(btn_check)

    def refresh(self):
        if self.dash.student_obj:
            self.cmb_prog.setCurrentText(self.dash.student_obj.program)
            self.spin_lvl.setValue(self.dash.student_obj.level)
        self.clear_simulation()

    def clear_simulation(self):
        self.simulated_courses.clear()
        self.draw_schedule_grid()
        for r in range(self.table.rowCount()):
            for c in range(3):
                item = self.table.item(r, c)
                if item: item.setBackground(QBrush(Qt.white))

    def run_simulation_list(self):
        """Populates the list. Resets current simulation."""
        self.simulated_courses.clear()
        self.draw_schedule_grid()

        sim_prog = self.cmb_prog.currentText()
        plan_dict = self.dash.logic_system.program_plan.get(sim_prog, {})
        allowed_courses = set()
        for level_courses in plan_dict.values():
            for c in level_courses: allowed_courses.add(c)

        completed = users_db.get_completed_courses(self.dash.user_id)
        current_reg = self.dash.logic_system.get_student_registered_courses(self.dash.student_obj)
        courses_db = self.dash.logic_system.courses_data

        self.table.setRowCount(0)
        for code in sorted(list(allowed_courses)):
            d = courses_db.get(code, {})
            name = d.get('name', 'Unknown')
            prereqs = d.get('prerequisites', [])
            
            status = "Eligible"
            if code in completed: status = "Completed"
            elif code in current_reg: status = "Registered"
            else:
                missing = [p for p in prereqs if p not in completed]
                if missing: status = "Missing Prereqs"

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(code))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            
            item_status = QTableWidgetItem(status)
            if "Missing" in status: item_status.setForeground(QBrush(QColor("red")))
            elif "Completed" in status or "Registered" in status: item_status.setForeground(QBrush(QColor("green")))
            else: item_status.setForeground(QBrush(QColor("blue")))
            self.table.setItem(row, 2, item_status)

    def toggle_course_selection(self, item):
        row = item.row()
        code = self.table.item(row, 0).text()
        status = self.table.item(row, 2).text()

        if "Registered" in status or "Completed" in status: return

        if code in self.simulated_courses:
            self.simulated_courses.remove(code)
            for c in range(3): self.table.item(row, c).setBackground(QBrush(Qt.white))
        else:
            self.simulated_courses.add(code)
            for c in range(3): self.table.item(row, c).setBackground(QBrush(QColor("#fff3e0")))

        self.draw_schedule_grid()

    def draw_schedule_grid(self):
        self.sim_cal.clearContents()
        registered_codes = self.dash.logic_system.get_student_registered_courses(self.dash.student_obj)
        courses_to_draw = []
        for c in registered_codes: courses_to_draw.append({"code": c, "color": "#3498db", "type": "actual"})
        for c in self.simulated_courses: courses_to_draw.append({"code": c, "color": "#e67e22", "type": "simulated"})

        data = self.dash.logic_system.courses_data
        d_map = {"Sun":0, "Mon":1, "Tue":2, "Wed":3, "Thu":4}

        for item_info in courses_to_draw:
            c_code = item_info["code"]
            c_color = item_info["color"]
            d = data.get(c_code, {})
            room = d.get('room', 'TBA')
            raw_day_str = str(d.get('day', '')).strip()
            start = d.get('start_time')
            end = d.get('end_time')

            if start and end:
                normalized_days = raw_day_str.replace('/', ',')
                day_list = [x.strip() for x in normalized_days.split(',')]
                for single_day in day_list:
                    if single_day in d_map:
                        try:
                            col = d_map[single_day]
                            s_hour = int(str(start).split(':')[0])
                            row_s = s_hour - 8
                            e_hour = int(str(end).split(':')[0])
                            dur = e_hour - s_hour
                            if dur < 1: dur = 1
                            if 0 <= row_s < 11:
                                cell_text = f"{c_code}\n{room}"
                                if item_info["type"] == "simulated": cell_text += "\n(PLAN)"
                                cell = QTableWidgetItem(cell_text)
                                cell.setBackground(QBrush(QColor(c_color)))
                                cell.setForeground(QBrush(Qt.white))
                                cell.setTextAlignment(Qt.AlignCenter)
                                for i in range(dur):
                                    if row_s + i < 11: self.sim_cal.setItem(row_s + i, col, QTableWidgetItem(cell))
                        except: pass

    def check_full_plan_conflicts(self):
        if not self.simulated_courses:
            return QMessageBox.information(self, "Info", "No courses simulated yet.")
        
        current_registered = self.dash.logic_system.get_student_registered_courses(self.dash.student_obj)
        full_plan = list(current_registered) + list(self.simulated_courses)
        warnings = SimulationLogic.check_soft_conflicts(self.dash.logic_system.courses_data, full_plan)
        
        msg = f"Analyzing plan with {len(full_plan)} courses (Actual + Simulated)...\n\n"
        if warnings:
            msg += "⚠️ Soft Conflicts Found:\n" + "\n".join(warnings)
            QMessageBox.warning(self, "Plan Analysis", msg)
        else:
            msg += "✅ No scheduling conflicts detected in this plan!"
            QMessageBox.information(self, "Plan Analysis", msg)

# =============================================================================
# TAB 6: SETTINGS
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

        layout.addWidget(QLabel("Update Email", styleSheet="font-weight:bold; font-size:14px; margin-top:10px;"))
        self.inp_email = QLineEdit(); self.inp_email.setPlaceholderText("New email")
        layout.addWidget(self.inp_email)
        btn_email = QPushButton("Save New Email"); btn_email.setProperty("class", "action-btn")
        btn_email.clicked.connect(self.update_email)
        layout.addWidget(btn_email)

        line = QFrame(); line.setFrameShape(QFrame.HLine); line.setStyleSheet("color: #ccc; margin: 20px 0;")
        layout.addWidget(line)

        layout.addWidget(QLabel("Change Password", styleSheet="font-weight:bold; font-size:14px;"))
        self.inp_old = QLineEdit(); self.inp_old.setPlaceholderText("Current Password"); self.inp_old.setEchoMode(QLineEdit.Password)
        self.inp_new = QLineEdit(); self.inp_new.setPlaceholderText("New Password"); self.inp_new.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.inp_old); layout.addWidget(self.inp_new)

        btn_pass = QPushButton("Update Password"); btn_pass.setProperty("class", "warning-btn")
        btn_pass.clicked.connect(self.update_password)
        layout.addWidget(btn_pass); layout.addStretch()

    def refresh(self):
        if self.dash.student_obj: self.inp_email.setText(self.dash.student_obj.email)

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
        sl.setSpacing(15)  # Spacing for logo

        # --- UPDATED LOGO SECTION ---
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap("kau_logo.png") 
        if not pixmap.isNull():
            scaled = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img_label.setPixmap(scaled)
        else:
            img_label.setText("ECE Department")
            img_label.setStyleSheet("color: #bdc3c7; font-weight: bold;")
        sl.addWidget(img_label)

        text_logo = QLabel("ECE Registration\nSystem")
        text_logo.setObjectName("LogoLabel")
        text_logo.setAlignment(Qt.AlignCenter)
        text_logo.setWordWrap(True) 
        text_logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecf0f1; padding: 10px;")
        sl.addWidget(text_logo)
        # ----------------------------
        
        self.stack = QStackedWidget()
        
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

        self.tab_whatif = WhatIfTab(self)
        self.tab_settings = SettingsTab(self)

        for t in [self.tab_overview, self.tab_register, self.tab_schedule, self.tab_trans, self.tab_plan, self.tab_whatif, self.tab_settings]:
            self.stack.addWidget(t)

        names = ["Overview", "Registration", "Schedule", "Transcript", "My Plan", "What-If Simulator", "Settings"]
        self.btns = []
        for i, name in enumerate(names):
            b = QPushButton(name)
            b.setCheckable(True)
            b.setAutoExclusive(True)
            b.setProperty("class", "nav-btn")
            b.clicked.connect(lambda _, x=i: self.switch(x))
            sl.addWidget(b); self.btns.append(b)
        
        sl.addStretch()

        # --- LOGOUT BUTTON ---
        btn_logout = QPushButton("Log Out")
        btn_logout.setProperty("class", "nav-btn")
        btn_logout.clicked.connect(self.handle_logout)
        sl.addWidget(btn_logout)
        # ---------------------

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

    def handle_logout(self):
        # We import here to avoid circular dependencies with Login_Window.py
        from Login_Window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.showMaximized()
        self.close()

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
        self.tab_whatif.refresh()
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
    # Replace with a real user ID from your database for testing
    window = StudentDashboard(user_id=2454896) 
    window.show()
    sys.exit(app.exec_())
