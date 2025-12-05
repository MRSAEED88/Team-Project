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

        for pre in prerequisites:
            if not self._course_exists(pre):
                return False, f"Prerequisite '{pre}' does not exist."

        try:
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
    #                       DELETE COURSE
    # ============================================================
    def delete_course(self, course_code):
        try:
            # Delete prerequisites
            users_db.execute_query(
                "DELETE FROM prerequisites WHERE course_code = ? OR prereq_code = ?",
                (course_code, course_code)
            )

            # Delete program plans
            users_db.execute_query(
                "DELETE FROM program_plans WHERE course_code = ?",
                (course_code,)
            )

            # Delete registrations (correct table)
            users_db.execute_query(
                "DELETE FROM registration WHERE course_code = ?",
                (course_code,)
            )

            # Delete course itself
            users_db.execute_query(
                "DELETE FROM courses WHERE course_code = ?",
                (course_code,)
            )

            return True, "Course deleted successfully."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                       UPDATE COURSE
    # ============================================================
    def update_course(self, course_code, **kwargs):
        if not self._course_exists(course_code):
            return False, f"Course '{course_code}' does not exist."

        try:
            for field, value in kwargs.items():
                users_db.execute_query(
                    f"UPDATE courses SET {field} = ? WHERE course_code = ?",
                    (value, course_code)
                )

            return True, f"Course '{course_code}' updated successfully."
        except Exception as e:
            return False, f"Database Error: {e}"

    # ============================================================
    #                STUDENT ACCOUNT MANAGEMENT
    # ============================================================

    def create_student_account(self, name, email, password, program, level):
        """
        Self registration (auto-generated student ID)
        """
        try:
            users_db.execute_query(
                "INSERT INTO users (name, email, password, membership) VALUES (?, ?, ?, 'student')",
                (name, email, password)
            )

            user_id = users_db.last_insert_id()

            users_db.execute_query(
                "INSERT INTO students (user_id, major, level) VALUES (?, ?, ?)",
                (user_id, program, level)
            )

            return True, "Student account created successfully."
        except Exception as e:
            return False, f"Database Error: {e}"

    def add_student(self, student_id, name, email, program, level, password):
        """
        Admin adds a student with a custom student_id
        """
        try:
            users_db.execute_query(
                "INSERT INTO users (user_id, name, email, password, membership) VALUES (?, ?, ?, ?, 'student')",
                (student_id, name, email, password)
            )

            users_db.execute_query(
                "INSERT INTO students (user_id, major, level) VALUES (?, ?, ?)",
                (student_id, program, level)
            )

            return True, "Student added successfully!"

        except Exception as e:
            return False, f"Database Error: {e}"

    def delete_student(self, student_id):
        try:
            # Delete transcript
            users_db.execute_query(
                "DELETE FROM transcripts WHERE student_id = ?",
                (student_id,)
            )

            # Delete registrations (correct table name)
            users_db.execute_query(
                "DELETE FROM registration WHERE student_id = ?",
                (student_id,)
            )

            # Delete student
            users_db.execute_query(
                "DELETE FROM students WHERE id = ?",
                (student_id,)
            )

            return True, "Student deleted successfully."

        except Exception as e:
            return False, f"Database Error: {e}"

    # ============================================================
    #                 INTERNAL: CHECK COURSE EXISTS
    # ============================================================
    def _course_exists(self, course_code):
        search_engine = users_db.search(course_code, table="courses", search_by="course_code")
        return search_engine.fetch() is not None
