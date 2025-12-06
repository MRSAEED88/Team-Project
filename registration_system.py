from typing import List, Tuple
import users_db
from registration_validator import RegistrationValidator
from Student import Student


class RegistrationSystem:
    """
    Executes the actual registration logic after validation.
    - Talks to the database (registration & waitlist tables).
    - Uses RegistrationValidator for all business rules.
    - Returns clear status messages to the GUI layer.
    """

    def __init__(self, max_credits: int = 18, min_credits: int = 0):
        # Load course and program data once (can be refreshed later if needed)
        self.courses_data = users_db.get_all_courses_data()
        self.program_plan = users_db.get_full_program_plan()

        # Create a validator instance that will be reused
        self.validator = RegistrationValidator(
            self.courses_data,
            self.program_plan,
            max_credits=max_credits,
            min_credits=min_credits
        )

    # ------------------------------------------------------------------
    def refresh_data(self):
        """
        Reloads course and program data from the database.
        Call this if the admin updates courses or program plans.
        """
        self.courses_data = users_db.get_all_courses_data()
        self.program_plan = users_db.get_full_program_plan()
        self.validator.courses_data = self.courses_data
        self.validator.program_plan = self.program_plan

    # ------------------------------------------------------------------
    def register_courses_for_student(
        self,
        student: Student,
        selected_courses: List[str]
    ) -> Tuple[bool, str]:
        """
        High-level registration flow:
        1) Load student completed courses + current enrollments.
        2) Run all validation checks through RegistrationValidator.
        3) If OK → insert into registration table, or waitlist if full.
        4) Return (status, message) for GUI / caller.

        This is the "Execution System", not the validator itself.
        """

        if not selected_courses:
            return False, "No courses selected."

        # Make sure data is up-to-date (optional, but safer)
        self.refresh_data()

        student_id = student.user_id

        # Load student's completed courses from transcripts
        completed_courses = users_db.get_completed_courses(student_id)

        # Current enrollments per course (for capacity / schedule checks)
        current_enrollments = users_db.get_current_enrollments()

        # 1) Run validation using RegistrationValidator
        is_valid, message = self.validator.validate_registration(
            selected_courses=selected_courses,
            completed_courses=completed_courses,
            student_program=student.program,
            student_level=student.level,
            current_enrollments=current_enrollments
        )

        if not is_valid:
            # Validation failed → do NOT touch the database
            return False, message

        # 2) Execute registration (DB changes)
        registered = []
        waitlisted = []

        # Refresh enrollments just before writing, to be extra safe
        current_enrollments = users_db.get_current_enrollments()

        for course_code in selected_courses:
            course_info = self.courses_data.get(course_code, {})
            max_cap = course_info.get("max_capacity", 0)
            enrolled_now = current_enrollments.get(course_code, 0)

            if enrolled_now < max_cap:
                # Seat available → register student
                users_db.register_course_for_student(student_id, course_code)
                registered.append(course_code)
                current_enrollments[course_code] = enrolled_now + 1
            else:
                # Course is full → add to waitlist
                users_db.add_to_waitlist(student_id, course_code)
                waitlisted.append(course_code)

        # 3) Build final message
        if registered and waitlisted:
            msg = (
                f"Registered in: {', '.join(registered)}. "
                f"Added to waitlist for: {', '.join(waitlisted)}."
            )
        elif registered:
            msg = f"Registered in: {', '.join(registered)}."
        elif waitlisted:
            msg = (
                "All selected courses are full. "
                f"Added to waitlist for: {', '.join(waitlisted)}."
            )
        else:
            msg = "No changes were made."

        return True, msg

    # ------------------------------------------------------------------
    def drop_course_for_student(
        self,
        student: Student,
        course_code: str
    ) -> Tuple[bool, str]:
        """
        Drops a course for the given student.
        Optionally, it can move the next student from the waitlist into the course.
        """

        student_id = student.user_id

        # First, remove the registration entry for this student
        users_db.drop_course_for_student(student_id, course_code)

        # Try to move the next student from waitlist to registration
        import sqlite3
        moved_from_waitlist = False
        next_student_id = None

        with sqlite3.connect('User.db') as con:
            cur = con.cursor()

            # Find the earliest student in waitlist for that course
            cur.execute(
                """
                SELECT student_id 
                FROM waitlist 
                WHERE course_code = ? 
                ORDER BY timestamp ASC 
                LIMIT 1
                """,
                (course_code,)
            )
            row = cur.fetchone()

            if row:
                next_student_id = row[0]
                # Register that student
                users_db.register_course_for_student(next_student_id, course_code)

                # Remove them from waitlist
                cur.execute(
                    "DELETE FROM waitlist WHERE student_id = ? AND course_code = ?",
                    (next_student_id, course_code)
                )
                con.commit()
                moved_from_waitlist = True

        if moved_from_waitlist:
            return True, (
                f"Dropped {course_code} for student {student_id}. "
                f"Next student from waitlist ({next_student_id}) was registered."
            )

        return True, f"Dropped {course_code} for student {student_id}. No one on waitlist."

    # ------------------------------------------------------------------
    def get_student_registered_courses(self, student: Student) -> List[str]:
        """
        Returns a set/list of course codes the student is currently registered in.
        Can be used by Student Dashboard to display the timetable.
        """
        return list(users_db.get_registered_courses(student.user_id))
from typing import List, Tuple
import users_db
from registration_validator import RegistrationValidator
from Student import Student


class RegistrationSystem:
    """
    Executes the actual registration logic after validation.
    - Talks to the database (registration & waitlist tables).
    - Uses RegistrationValidator for all business rules.
    - Returns clear status messages to the GUI layer.
    """

    def __init__(self, max_credits: int = 18, min_credits: int = 0):
        # Load course and program data once (can be refreshed later if needed)
        self.courses_data = users_db.get_all_courses_data()
        self.program_plan = users_db.get_full_program_plan()

        # Create a validator instance that will be reused
        self.validator = RegistrationValidator(
            self.courses_data,
            self.program_plan,
            max_credits=max_credits,
            min_credits=min_credits
        )

    # ------------------------------------------------------------------
    def refresh_data(self):
        """
        Reloads course and program data from the database.
        Call this if the admin updates courses or program plans.
        """
        self.courses_data = users_db.get_all_courses_data()
        self.program_plan = users_db.get_full_program_plan()
        self.validator.courses_data = self.courses_data
        self.validator.program_plan = self.program_plan

    # ------------------------------------------------------------------
    def register_courses_for_student(
        self,
        student: Student,
        selected_courses: List[str]
    ) -> Tuple[bool, str]:
        """
        High-level registration flow:
        1) Load student completed courses + current enrollments.
        2) Run all validation checks through RegistrationValidator.
        3) If OK → insert into registration table, or waitlist if full.
        4) Return (status, message) for GUI / caller.
        """

        if not selected_courses:
            return False, "No courses selected."

        # Ensure data is up-to-date
        self.refresh_data()

        student_id = student.user_id

        # Load student's completed courses from transcripts
        completed_courses = users_db.get_completed_courses(student_id)

        # Current enrollments per course (capacity / schedule)
        current_enrollments = users_db.get_current_enrollments()

        # -----------------------------
        # VALIDATION CHECK
        # -----------------------------
        is_valid, message = self.validator.validate_registration(
            selected_courses=selected_courses,
            completed_courses=completed_courses,
            student_program=student.program,
            student_level=student.level,
            current_enrollments=current_enrollments
        )

        if not is_valid:
            return False, message

        # -----------------------------
        # EXECUTION (write to DB)
        # -----------------------------
        registered = []
        waitlisted = []

        current_enrollments = users_db.get_current_enrollments()

        for course_code in selected_courses:
            course_info = self.courses_data.get(course_code, {})
            max_cap = course_info.get("max_capacity", 0)
            enrolled_now = current_enrollments.get(course_code, 0)

            if enrolled_now < max_cap:
                # Seat available → register student
                users_db.register_course_for_student(student_id, course_code)
                registered.append(course_code)
                current_enrollments[course_code] = enrolled_now + 1
            else:
                # Course full → send to waitlist
                users_db.add_to_waitlist(student_id, course_code)
                waitlisted.append(course_code)

        # -----------------------------
        # FINAL MESSAGE TO STUDENT
        # -----------------------------
        if registered and waitlisted:
            msg = (
                f"Registered in: {', '.join(registered)}. "
                f"Course is full — added to waitlist for: {', '.join(waitlisted)}."
            )
        elif registered:
            msg = f"Registered in: {', '.join(registered)}."
        elif waitlisted:
            msg = (
                f"The course is full. You have been added to the waitlist for: "
                f"{', '.join(waitlisted)}."
            )
        else:
            msg = "No changes were made."

        return True, msg

    # ------------------------------------------------------------------
    def drop_course_for_student(
        self,
        student: Student,
        course_code: str
    ) -> Tuple[bool, str]:
        """
        Drops a course for the given student.
        Moves next student from waitlist (if available).
        """

        student_id = student.user_id

        users_db.drop_course_for_student(student_id, course_code)

        import sqlite3
        moved_from_waitlist = False
        next_student_id = None

        with sqlite3.connect('User.db') as con:
            cur = con.cursor()

            # Get earliest waitlisted student
            cur.execute(
                """
                SELECT student_id 
                FROM waitlist 
                WHERE course_code = ? 
                ORDER BY timestamp ASC 
                LIMIT 1
                """,
                (course_code,)
            )
            row = cur.fetchone()

            if row:
                next_student_id = row[0]

                # Register that student
                users_db.register_course_for_student(next_student_id, course_code)

                # Remove them from waitlist
                cur.execute(
                    "DELETE FROM waitlist WHERE student_id = ? AND course_code = ?",
                    (next_student_id, course_code)
                )
                con.commit()

                moved_from_waitlist = True

        if moved_from_waitlist:
            return True, (
                f"Dropped {course_code}. "
                f"Waitlisted student ({next_student_id}) has now been registered."
            )

        return True, f"Dropped {course_code}. No waitlisted students."

    # ------------------------------------------------------------------
    def get_student_registered_courses(self, student: Student) -> List[str]:
        """
        Returns a list of all courses the student is currently registered in.
        """
        return list(users_db.get_registered_courses(student.user_id))
