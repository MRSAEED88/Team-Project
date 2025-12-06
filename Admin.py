import bcrypt
import csv
from User import User
import users_db

class Admin(User):
    def __init__(self, user_id, name, email, password):
        super().__init__(user_id, name, email, password, membership="Admin")

    # ============================================================
    #                       ADD COURSE
    # ============================================================
    def add_course(self, code, name, credits, day, start_time, end_time, room, max_capacity, prerequisites=[]):
        if not all([code, name, credits, day, start_time, end_time, room, max_capacity]):
            return False, "All fields are required."

        if credits <= 0:
            return False, "Credits must be positive."

        if self._course_exists(code):
            return False, f"Course '{code}' already exists."

        # Check prereqs existence
        for pre in prerequisites:
            if not self._course_exists(pre):
                return False, f"Prerequisite '{pre}' does not exist."

        try:
            # Use tuple matching schema
            new_course = users_db.courses_db((None, code, name, credits, day, start_time, end_time, room, max_capacity))
            new_course.course_insert()

            for pre in prerequisites:
                users_db.execute_query(
                    "INSERT INTO prerequisites (course_code, prereq_code) VALUES (?, ?)",
                    (code, pre)
                )

            return True, f"Course '{code}' added successfully."
        except Exception as e:
            return False, f"Database Error: {e}"

    # ============================================================
    #                  BULK IMPORT (CSV)
    # ============================================================
    def import_courses_from_csv(self, file_path):
        success_count = 0
        errors = []
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader, None)
                
                for row_num, row in enumerate(reader, start=1):
                    if len(row) < 8:
                        errors.append(f"Row {row_num}: Incomplete data.")
                        continue

                    code, name, credits, day, start, end, room, cap = row[0:8]
                    try:
                        success, msg = self.add_course(
                            code.strip(), name.strip(), int(credits), day.strip(), 
                            str(start).strip(), str(end).strip(), room.strip(), int(cap), []
                        )
                        if success: success_count += 1
                        else: errors.append(f"Row {row_num} ({code}): {msg}")
                    except ValueError:
                        errors.append(f"Row {row_num}: Invalid number format.")
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

            return True, f"Imported {success_count} courses successfully.", errors
        except Exception as e:
            return False, f"File Error: {str(e)}", []

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
        except Exception as e:
            return False, f"Database Error: {e}"

    # ============================================================
    #                STUDENT ACCOUNT MANAGEMENT
    # ============================================================
    def create_student_account(self, name, email, password, program, level):
        """ Self registration (auto-generated ID) """
        try:
            # ENCRYPT PASSWORD
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            users_db.execute_query(
                "INSERT INTO users (name, email, password, membership) VALUES (?, ?, ?, 'student')",
                (name, email, hashed_pw)
            )
            # Fetch the auto-generated ID
            # Note: You might need a way to get the last row ID here if users_db doesn't return it
            # For now, assuming direct insertion works or logic is handled elsewhere.
            return True, "Student account created."
        except Exception as e:
            return False, f"Database Error: {e}"

    def add_student(self, student_id, name, email, program, level, password):
        """ Admin adds a student manually """
        try:
            # ENCRYPT PASSWORD
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            # 1. Insert into Users Table
            # Note: using 'id' not 'user_id' to match users_db schema
            users_db.execute_query(
                "INSERT INTO users (id, name, email, password, membership) VALUES (?, ?, ?, ?, 'student')",
                (student_id, name, email, hashed_pw)
            )

            # 2. Insert into Students Table
            users_db.execute_query(
                "INSERT INTO students (id, name, email, program, level) VALUES (?, ?, ?, ?, ?)",
                (student_id, name, email, program, level)
            )

            return True, "Student added successfully!"
        except Exception as e:
            return False, f"Database Error: {e}"

    def delete_student(self, student_id):
        try:
            users_db.execute_query("DELETE FROM transcripts WHERE student_id = ?", (student_id,))
            users_db.execute_query("DELETE FROM registration WHERE student_id = ?", (student_id,))
            users_db.execute_query("DELETE FROM students WHERE id = ?", (student_id,))
            users_db.execute_query("DELETE FROM users WHERE id = ?", (student_id,))
            return True, "Student deleted successfully."
        except Exception as e:
            return False, f"Database Error: {e}"

    # ============================================================
    #                 INTERNAL: CHECK COURSE EXISTS
    # ============================================================
    def _course_exists(self, course_code):
        search_engine = users_db.search(course_code, table="courses", search_by="course_code")
        return search_engine.fetch() is not None
