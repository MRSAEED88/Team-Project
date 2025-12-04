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
    # ============================================================
    #                       DELETE COURSE
    # ============================================================
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
        try:
            # 1. Check existence
            if not self._course_exists(course_code):
                return False, f"Course '{course_code}' does not exist."

            # 2. Check if students are registered
            # FIX: We use 'get_current_enrollments' instead of 'search' to avoid the Invalid Table error
            enrollments = users_db.get_current_enrollments()
            
            # If the course code is in the dictionary and count > 0, we can't delete it
            if enrollments.get(course_code, 0) > 0:
                return False, "Cannot delete course. Students are currently registered."

            # 3. Delete prerequisites associated with the course
            users_db.execute_query(
                "DELETE FROM prerequisites WHERE course_code = ? OR prereq_code = ?",
                (course_code, course_code)
            )

            # 4. Delete program plan entries
            users_db.execute_query(
                "DELETE FROM program_plans WHERE course_code = ?",
                (course_code,)
            )

            # 5. Delete course
            users_db.execute_query(
                "DELETE FROM courses WHERE course_code = ?",
                (course_code,)
            )

            return True, f"Course '{course_code}' deleted successfully."

        except Exception as e:
            return False, f"Database Error: {e}"
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
    # ============================================================
    #                     VIEW ALL COURSES
    # ============================================================
    def view_all_courses(self):
        """
        Returns all courses from the database.
        Uses the existing users_db.get_all_courses() and formats it for the GUI.
        """
        try:
            # 1. Get raw data from the existing function in users_db
            # Raw format from DB: (Code, Name, Credits, Capacity, Day, Start, End, Room)
            raw_data = users_db.get_all_courses()
            
            formatted_data = []
            for row in raw_data:
                # 2. Re-arrange data to match what the GUI expects:
                # GUI expects: (ID, Code, Name, Credits, Day, Start, End, Room, Capacity)
                # Note: We add a dummy '0' at the start because the GUI skips the first item (ID).
                
                formatted_row = (
                    0,          # Dummy ID (ignored by GUI)
                    row[0],     # Code
                    row[1],     # Name
                    row[2],     # Credits
                    row[4],     # Day
                    row[5],     # Start
                    row[6],     # End
                    row[7],     # Room
                    row[3]      # Capacity (Moved to the end to match GUI headers)
                )
                formatted_data.append(formatted_row)
                
            return formatted_data

        except Exception as e:
            # Return an empty list if something goes wrong, so the GUI doesn't crash
            print(f"Error viewing courses: {e}")
            return []


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

    # ============================================================
    #              DEFINE PROGRAM PLAN (Was Missing)
    # ============================================================
    def define_program_plan(self, program, level, course_codes):
        """
        Assigns a list of courses to a specific Program and Level.
        called by AdminDashboard.submit_plan()
        """
        if not course_codes:
            return False, "No course code provided."

        try:
            for code in course_codes:
                # 1. Verify the course actually exists first
                if not self._course_exists(code):
                    return False, f"Error: Course '{code}' does not exist in the system."

                # 2. Insert into the program_plans table
                users_db.execute_query(
                    "INSERT OR IGNORE INTO program_plans (program, level, course_code) VALUES (?, ?, ?)",
                    (program, level, code)
                )
            return True, f"Successfully assigned {course_codes[0]} to {program} Level {level}."

        except Exception as e:
            return False, f"Database Error: {e}"
        
        
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
