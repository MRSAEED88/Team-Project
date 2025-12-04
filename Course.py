class Course:
    def __init__(self, course_code, name, credits, lecture_hours, lab_hours, max_capacity, prerequisites=None):
        self.course_code = course_code
        self.name = name
        self.credits = credits
        self.lecture_hours = lecture_hours
        self.lab_hours = lab_hours
        self.max_capacity = max_capacity
        self.prerequisites = prerequisites if prerequisites is not None else []

    def check_prerequisites(self, student_transcript):
        for prereq in self.prerequisites:
            if prereq not in student_transcript:
                return False, f"Prerequisite {prereq} not completed."
        return True, "All prerequisites satisfied."

    def is_full(self, enrolled_students):
        return enrolled_students >= self.max_capacity
