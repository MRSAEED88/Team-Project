class RegistrationSystem:
    MIN_CREDITS = 12
    MAX_CREDITS = 18
    
    def __init__(self):
        self.courses = {}          # course_code -> Course object
        self.enrolled_counts = {}  # course_code -> number of enrolled students
        self.registrations = {}    # student_id -> list of course codes

    def add_course(self, course):
        code = course.course_code
        if code in self.courses:
            raise ValueError(f"Course {code} already exists.")
        self.courses[code] = course
        self.enrolled_counts[code] = 0

    def get_course(self, course_code):
        return self.courses.get(course_code)

    def validate_schedule(self, student, selected_courses):
        messages = []

        # credit limit check
        total_credits = sum(c.credits for c in selected_courses)
        if total_credits < self.MIN_CREDITS or total_credits > self.MAX_CREDITS:
            messages.append(
                f"Total credits {total_credits} is outside allowed range "
                f"[{self.MIN_CREDITS}, {self.MAX_CREDITS}]."
            )

        # build list of completed course codes from transcript
        completed_codes = [
            record["course_code"] for record in student.transcript
            if "course_code" in record
        ]

        # prerequisites check
        for course in selected_courses:
            ok, msg = course.check_prerequisites(completed_codes)
            if not ok:
                messages.append(f"Cannot register in {course.course_code}: {msg}")

        # capacity check
        for course in selected_courses:
            code = course.course_code
            enrolled = self.enrolled_counts.get(code, 0)
            if course.is_full(enrolled):
                messages.append(f"Cannot register in {code}: course is full.")

        # duplicate selection check
        codes = [c.course_code for c in selected_courses]
        if len(codes) != len(set(codes)):
            messages.append("You selected the same course more than once.")

        is_valid = len(messages) == 0
        return is_valid, messages

    def register_student(self, student, selected_courses):
        is_valid, messages = self.validate_schedule(student, selected_courses)
        if not is_valid:
            return False, messages

        # get student id (user_id from User parent, or student_id fallback)
        student_key = getattr(student, "user_id", None)
        if student_key is None:
            student_key = getattr(student, "student_id", None)
        if student_key is None:
            return False, ["Student has no valid ID."]

        # save registration
        self.registrations[student_key] = [c.course_code for c in selected_courses]

        # update enrolled counts safely
        for course in selected_courses:
            code = course.course_code
            if code not in self.enrolled_counts:
                self.enrolled_counts[code] = 0
            self.enrolled_counts[code] += 1

        messages.append("Registration completed successfully.")
        return True, messages

    def get_registered_courses(self, student):
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
