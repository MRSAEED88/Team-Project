import csv
from User import User
import users_db
import sqlite3

class Admin(User):
    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, membership="Admin")

    # ============================================================
    #                       ADD COURSE
    # ============================================================
    def add_course(self, code, name, credits, day, start_time, end_time, room, max_capacity, prerequisites=[]):
        if not all([code, name, credits, day, start_time, end_time, room, max_capacity]):
            return False, "All fields are required."
        if credits <= 0: return False, "Credits must be positive."
        if self._course_exists(code): return False, f"Course '{code}' already exists."
        
        try:
            new_course = users_db.courses_db((None, code, name, credits, day, start_time, end_time, room, max_capacity))
            new_course.course_insert()
            for pre in prerequisites:
                users_db.execute_query("INSERT INTO prerequisites (course_code, prereq_code) VALUES (?, ?)", (code, pre))
            return True, f"Course '{code}' added successfully."
        except Exception as e: return False, f"Database Error: {e}"

    # ============================================================
    #                  BULK IMPORT (CSV)
    # ============================================================
    def import_courses_from_csv(self, file_path):
        success_count = 0
        errors = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None) # Skip header
                for row_num, row in enumerate(reader, start=1):
                    if len(row) < 8:
                        errors.append(f"Row {row_num}: Incomplete data.")
                        continue
                    code, name, credits, day, start, end, room, cap = row[0:8]
                    try:
                        success, msg = self.add_course(code.strip(), name.strip(), int(credits), day.strip(), str(start).strip(), str(end).strip(), room.strip(), int(cap), [])
                        if success: success_count += 1
                        else: errors.append(f"Row {row_num} ({code}): {msg}")
                    except Exception as e: errors.append(f"Row {row_num}: {str(e)}")
            return True, f"Imported {success_count} courses.", errors
        except Exception as e: return False, f"File Error: {str(e)}", []

    # ============================================================
    #                       DELETE COURSE
    # ============================================================
    def delete_course(self, course_code):
        try:
            users_db.execute_query("DELETE FROM prerequisites WHERE course_code = ? OR prereq_code = ?", (course_code, course_code))
            users_db.execute_query("DELETE FROM program_plans WHERE course_code = ?", (course_code,))
            users_db.execute_query("DELETE FROM registration WHERE course_code = ?", (course_code,))
            users_db.execute_query("DELETE FROM courses WHERE course_code = ?", (course_code,))
            return True, "Course deleted successfully."
        except Exception as e: return False, f"Database Error: {e}"

    # ============================================================
    #                STUDENT ACCOUNT MANAGEMENT
    # ============================================================
    def add_student(self, student_id, name, email, program, level, password):
        """ Admin adds a student manually (PLAIN TEXT PASSWORD) """
        try:
            # 1. Insert into Users Table (PLAIN TEXT)
            users_db.execute_query(
                "INSERT INTO users (id, name, email, password, membership) VALUES (?, ?, ?, ?, 'student')",
                (student_id, name, email, password)
            )
            # 2. Insert into Students Table
            users_db.execute_query(
                "INSERT INTO students (id, name, email, program, level) VALUES (?, ?, ?, ?, ?)",
                (student_id, name, email, program, level)
            )
            return True, "Student added successfully!"
        except Exception as e: return False, f"Database Error: {e}"

    def delete_student(self, student_id):
        try:
            users_db.execute_query("DELETE FROM transcripts WHERE student_id = ?", (student_id,))
            users_db.execute_query("DELETE FROM registration WHERE student_id = ?", (student_id,))
            users_db.execute_query("DELETE FROM students WHERE id = ?", (student_id,))
            users_db.execute_query("DELETE FROM users WHERE id = ?", (student_id,))
            return True, "Student deleted successfully."
        except Exception as e: return False, f"Database Error: {e}"

# ============================================================
    #                 INTERNAL: CHECK COURSE EXISTS
    # ============================================================
    def _course_exists(self, course_code):
        # We perform a direct SQL query for an EXACT match, 
        # bypassing the fuzzy search engine to avoid false positives.
        with sqlite3.connect('User.db') as con:
            cur = con.cursor()
            cur.execute("SELECT 1 FROM courses WHERE course_code = ?", (course_code,))
            return cur.fetchone() is not None
