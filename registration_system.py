class RegistrationSystem:

    # 1) this class is responsible for: 1)Store all courses. 2) tracks how many students are enrolled in each course.
    # 3) Validate students' schedule before registration. 4) Save the final list of registered courses for each student.
   
    MIN_CREDITS = 12             # all students must stay within this credit range
    MAX_CREDITS = 18
    
    def __init__(self):
        # Dictionary of all courses offered in the system.
        # Key: course code
        # Value: Course object
        self.courses = {}

        # Dictionary to track current number of enrolled students per course.
        # Key: course code
        # Value: integer count of enrolled students
        self.enrolled_counts = {}

        # Dictionary of students' final registrations.
        # Key: student id (user_id or student_id)
        # Value: list of course codes the student is registered in
        self.registrations = {}

    def add_course(self, course):     # Add a new course to the system. And give ValueError if a course with the same course code already exists.
        code = course.course_code

        # Don't allow two different courses with the same course code
        if code in self.courses:
            raise ValueError(f"Course {code} already exists.")

        # Store the course and initialize its enrollment count to zero
        self.courses[code] = course
        self.enrolled_counts[code] = 0

    def get_course(self, course_code):    # Return the Course object for a given course code, or None if not found.
        return self.courses.get(course_code)

    def validate_schedule(self, student, selected_courses):    # Check if a student's selected courses form a valid schedule.
        # The following constraints are checked:
            #1) Total credits must be between MIN_CREDITS and MAX_CREDITS.
            #2) Student must satisfy all prerequisites of each selected course.
            #3) Each course must be not full.
            #4) The same course cannot be selected more than once.
        # Returns:
            # (is_valid, messages)
            # is_valid : bool
            # messages : list of strings describing any problems found
      
        messages = []

        # 1 Credit limit check 
        # Compute total number of credits for the selected courses
        total_credits = sum(c.credits for c in selected_courses)

        # If total_credits is outside the allowed range ----> error message
        if total_credits < self.MIN_CREDITS or total_credits > self.MAX_CREDITS:
            messages.append(
                f"Total credits {total_credits} is outside allowed range "
                f"[{self.MIN_CREDITS}, {self.MAX_CREDITS}]."
            )

        # Build list of completed course code
        completed_codes = [
            record["course_code"] for record in student.transcript
            if "course_code" in record
        ]

        # 2 Prerequisite check
        # For each selected course, ask the course object to verify that all its prerequisites are present in completed_codes.
        for course in selected_courses:
            ok, msg = course.check_prerequisites(completed_codes)

            # If prerequisites are not satisfied ---> error message
            if not ok:
                messages.append(f"Cannot register in {course.course_code}: {msg}")
        # 3 Capacity check
        for course in selected_courses:
            code = course.course_code

            # How many students are currently enrolled in this course
            enrolled = self.enrolled_counts.get(code, 0)

            # Ask the course object if it's already full
            if course.is_full(enrolled):
                messages.append(f"Cannot register in {code}: course is full.")

        # 4 Duplicate selection check
        # Extract only the course codes from the selected courses
        codes = [c.course_code for c in selected_courses]

        # If there are duplicates, the length of the list and the set will be different
        if len(codes) != len(set(codes)):
            messages.append("You selected the same course more than once.")

        # If no messages appear ---> the schedule is valid
        is_valid = len(messages) == 0
        return is_valid, messages

    def register_student(self, student, selected_courses):    # Try to register a student in the given list of selected_courses.
       #Steps:
            # First validate the schedule using validate_schedule().
            # If validation fails, return False and the error messages.
            # Otherwise, save the registration and update enrollment counts.

       # Returns:
            # (success, messages)
            # success  : bool
            # messages : list of status / error messages
        
        # Run all validation checks
        is_valid, messages = self.validate_schedule(student, selected_courses)
        if not is_valid:
            # Don't modify any data if schedule is invalid
            return False, messages

        # ---------- Determine student key ----------
        # Prefer user_id (from User parent). If not present, go to student_id. If not present we can't store registration
        student_key = getattr(student, "user_id", None)
        if student_key is None:
            student_key = getattr(student, "student_id", None)
        if student_key is None:
            return False, ["Student has no valid ID."]

        # Store only course codes (not full Course objects) for simplicity
        self.registrations[student_key] = [c.course_code for c in selected_courses]

        # For each course in the student's schedule, increase the count
        for course in selected_courses:
            code = course.course_code

            # If the course wasn't in enrolled_counts --> initialize its count to zero before increment
            if code not in self.enrolled_counts:
                self.enrolled_counts[code] = 0

            self.enrolled_counts[code] += 1

        messages.append("Registration completed successfully.")
        return True, messages

    def get_registered_courses(self, student):   # Return the list of course codes that the student is registered in. If the student isn't found, return an empty list.
        # Use the same logic as before to obtain the student's unique key
        student_key = getattr(student, "user_id", None)
        if student_key is None:
            student_key = getattr(student, "student_id", None)

        return self.registrations.get(student_key, [])



# ---------------- This code is to test the registation system -----------------

from Course import Course
from Student import Student
from registration_system import RegistrationSystem


system = RegistrationSystem()

EE250 = Course(
    course_code="EE250",
    name="Fundamentals of Electrical Circuits",
    credits=4,            # total credits more than 11 & passed all prerequisites to get success:True
    lecture_hours=3,
    lab_hours=0,
    max_capacity=40,
    prerequisites=[]
)

EE201 = Course(
    course_code="EE201",
    name="Python",
    credits=3,
    lecture_hours=4,
    lab_hours=0,
    max_capacity=40,
    prerequisites=[]
)

EE311 = Course(
    course_code="EE311",
    name="Electronics",
    credits=4,
    lecture_hours=3,
    lab_hours=0,
    max_capacity=35,
    prerequisites=[]
)

EE300 = Course(
    course_code="EE300",
    name="Complex",
    credits=3,
    lecture_hours=3,
    lab_hours=0,
    max_capacity=40,
    prerequisites=[]
)

EE301 = Course(
    course_code="EE301",
    name="Circuits",
    credits=3,
    lecture_hours=3,
    lab_hours=0,
    max_capacity=40,
    prerequisites=["EE250"]
)

EE331 = Course(
    course_code="EE341",
    name="Machines",
    credits=3,
    lecture_hours=3,
    lab_hours=0,
    max_capacity=35,
    prerequisites=["EE250"]
)
system.add_course(EE250)
system.add_course(EE201)
system.add_course(EE311)
system.add_course(EE300)
system.add_course(EE301)
system.add_course(EE331)

student = Student(
    user_id=2433632,
    name="Sulaiman",
    email="sulaiman@stu.kau.edu.sa",
    program="Computer",
    level=3,
    password="3625487"
)

student.transcript.append({"course_code": "EE250", "grade": "A"})

selected = [EE250, EE201, EE311, EE300, EE301]

success, messages = system.register_student(student, selected)

print("Success:", success)
print("Messages:")
for m in messages:
    print("-", m)

print("Registered courses:", system.get_registered_courses(student))
