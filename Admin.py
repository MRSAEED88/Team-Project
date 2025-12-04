from User import User
import users_db

class Admin(User):
    def __init__(self, user_id, name, email, password):
        # Initialize parent User class
        super().__init__(user_id, name, email, password, membership="Admin")


    # ============================================================
    #                       ADD COURSE
    # ============================================================
    def add_course(self, code, name, credits, day, start_time, end_time, room, max_capacity, prerequisites=[]):
        """
        Adds a new course into the database.
        The method validates inputs, checks duplicates, validates prerequisites,
        then inserts the course and prerequisite records.
        """

        # ----- Input Validation -----
        if not all([code, name, credits, day, start_time, end_time, room, max_capacity]):
            return False, "All fields (Code, Name, Credits, Schedule, Capacity) are mandatory."

        if credits <= 0:
            return False, "Credits must be positive."

        # ----- Check if course exists -----
        if self._course_exists(code):
            return False, f"Course code '{code}' already exists."

        # ----- Validate prerequisites -----
        for pre in prerequisites:
            if not self._course_exists(pre):
                return False, f"Prerequisite '{pre}' does not exist."

        # ----- Insert Course -----
        course_data = (None, code, name, credits, day, start_time, end_time, room, max_capacity)

        try:
            # Insert course using users_db class
            new_course = users_db.courses_db(course_data)
            new_course.course_insert()

            # Insert prerequisites
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
        """
        Deletes a course only if:
        - Course exists
        - No students are currently registered for this course
        - Removes related prerequisites before deleting the course
        """

        # Check existence
        if not self._course_exists(course_code):
            return False, f"Course '{course_code}' does not exist."

        # Check if students are registered
        reg = users_db.search(course_code, table="registrations", search_by="course_code").fetch()
        if reg:
            return False, "Cannot delete course. Students are currently registered."

        try:
            # Delete prerequisites associated with the course
            users_db.execute_query(
                "DELETE FROM prerequisites WHERE course_code = ? OR prereq_code = ?",
                (course_code, course_code)
            )

            # Delete course
            users_db.execute_query(
                "DELETE FROM courses WHERE course_code = ?",
                (course_code,)
            )

            return True, f"Course '{course_code}' deleted successfully."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                       UPDATE COURSE
    # ============================================================
    def update_course(self, course_code, **kwargs):
        """
        Updates any course field:
        - name
        - credits
        - day
        - start_time
        - end_time
        - room
        - max_capacity

        Example:
        update_course("EE201", name="Circuits I", credits=4, room="B-23")
        """

        if not self._course_exists(course_code):
            return False, f"Course '{course_code}' does not exist."

        try:
            for field, value in kwargs.items():
                query = f"UPDATE courses SET {field} = ? WHERE course_code = ?"
                users_db.execute_query(query, (value, course_code))

            return True, f"Course '{course_code}' updated successfully."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                     VIEW ALL COURSES
    # ============================================================
    def view_all_courses(self):
        """
        Returns all courses from the database.
        Used by Admin Dashboard to display course list.
        """
        try:
            return users_db.fetch_all("SELECT * FROM courses")
        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                PREREQUISITE MANAGEMENT
    # ============================================================
    def add_prerequisite(self, course_code, prereq_code):
        """
        Adds a prerequisite to a course after validating both exist.
        """

        if not self._course_exists(course_code):
            return False, f"Course '{course_code}' does not exist."

        if not self._course_exists(prereq_code):
            return False, f"Prerequisite '{prereq_code}' does not exist."

        try:
            users_db.execute_query(
                "INSERT OR IGNORE INTO prerequisites (course_code, prereq_code) VALUES (?, ?)",
                (course_code, prereq_code)
            )
            return True, f"Prerequisite '{prereq_code}' added to course '{course_code}'."

        except Exception as e:
            return False, f"Database Error: {e}"


    def remove_prerequisite(self, course_code, prereq_code):
        """
        Removes a prerequisite from a course.
        """
        try:
            users_db.execute_query(
                "DELETE FROM prerequisites WHERE course_code = ? AND prereq_code = ?",
                (course_code, prereq_code)
            )
            return True, "Prerequisite removed."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                PROGRAM PLAN MANAGEMENT
    # ============================================================
    def view_program_plan(self, program, level):
        """
        Returns all course codes assigned to a program & level.
        """

        try:
            return users_db.fetch_all(
                "SELECT course_code FROM program_plans WHERE program = ? AND level = ?",
                (program, level)
            )

        except Exception as e:
            return False, f"Database Error: {e}"


    def remove_course_from_program(self, program, level, course_code):
        """
        Removes a course from a specific program and level.
        """

        try:
            users_db.execute_query(
                "DELETE FROM program_plans WHERE program = ? AND level = ? AND course_code = ?",
                (program, level, course_code)
            )
            return True, "Course removed from program plan."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                   STUDENT ACCOUNT MANAGEMENT
    # ============================================================
    def create_student_account(self, name, email, password, program, level):
        """
        Creates a new student entry + user login entry.
        """

        try:
            # Insert into students table
            users_db.execute_query(
                "INSERT INTO students (name, email, program, level) VALUES (?, ?, ?, ?)",
                (name, email, program, level)
            )

            # Insert into users table
            users_db.execute_query(
                "INSERT INTO users (name, email, password, membership) VALUES (?, ?, ?, ?)",
                (name, email, password, "Student")
            )

            return True, "Student account created successfully."

        except Exception as e:
            return False, f"Database Error: {e}"


    def delete_student(self, student_id):
        """
        Deletes student and related records (transcript, registrations).
        """

        try:
            # Delete transcript
            users_db.execute_query(
                "DELETE FROM transcripts WHERE student_id = ?",
                (student_id,)
            )

            # Delete registrations
            users_db.execute_query(
                "DELETE FROM registrations WHERE student_id = ?",
                (student_id,)
            )

            # Delete student table entry
            users_db.execute_query(
                "DELETE FROM students WHERE id = ?",
                (student_id,)
            )

            return True, "Student deleted successfully."

        except Exception as e:
            return False, f"Database Error: {e}"


    # ============================================================
    #                INTERNAL HELPER METHOD
    # ============================================================
    def _course_exists(self, course_code):
        """
        Returns True if a course exists in the database.
        """
        search_engine = users_db.search(course_code, table="courses", search_by="course_code")
        return search_engine.fetch() is not None
