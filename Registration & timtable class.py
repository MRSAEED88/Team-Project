class Course:
    def __init__(self, code, name, credits,
                 prerequisites=None,
                 capacity=30,
                 enrolled=0,
                 schedule=None):
        
        self.code = code
        self.name = name
        self.credits = credits
        self.prerequisites = prerequisites or []
        self.capacity = capacity
        self.enrolled = enrolled
        self.schedule = schedule or []  # list of (day, start, end)

class Student:
    def __init__(self, student_id, name, program, level,
                 completed_courses,
                 allowed_courses=None,
                 min_credits=12,
                 max_credits=18):
        
        self.student_id = student_id
        self.name = name
        self.program = program
        self.level = level
        self.completed_courses = completed_courses  # list of course codes
        self.allowed_courses = allowed_courses or []  # program plan
        self.min_credits = min_credits
        self.max_credits = max_credits

class RegistrationModule:
    def __init__(self, student, available_courses):
        # input sources
        self.student = student
        # dict: "COE310" -> Course object
        self.available_courses = {c.code: c for c in available_courses}

        self.selected = []           # list of Course objects
        self.messages = []           # validation messages (errors/warnings)
        self.waitlist = {}

    # ------------------------- course selection -------------------------

    def add_course(self, course_code):
        if course_code not in self.available_courses:
            self.messages.append(f"Unknown course {course_code}.")
            return

        course = self.available_courses[course_code]

        if course in self.selected:
            return  # already selected

        self.selected.append(course)
        self.validate()  # real-time feedback

    def remove_course(self, course_code):
        self.selected = [c for c in self.selected if c.code != course_code]
        self.validate()

    # ------------------------- validation logic -------------------------

    def validate(self):
        self.messages = []
        ok = True

        if not self._check_credits():
            ok = False
        if not self._check_prereqs():
            ok = False
        if not self._check_program_plan():
            ok = False
        if not self._check_schedule_conflicts():
            ok = False
        if not self._check_capacity():
            ok = False

        return ok

    def _check_credits(self):
        total = sum(c.credits for c in self.selected)
        if total < self.student.min_credits:
            self.messages.append(
                f"Total credits {total} is below minimum {self.student.min_credits}."
            )
            return False
        if total > self.student.max_credits:
            self.messages.append(
                f"Total credits {total} is above maximum {self.student.max_credits}."
            )
            return False
        return True

    def _check_prereqs(self):
        ok = True
        completed = set(self.student.completed_courses)

        for c in self.selected:
            missing = [p for p in c.prerequisites if p not in completed]
            if missing:
                ok = False
                msg = (f"Cannot register for {c.code}: "
                       f"missing prerequisite(s): {', '.join(missing)}.")
                self.messages.append(msg)
        return ok

    def _check_program_plan(self):
        ok = True
        allowed = set(self.student.allowed_courses)  # program plan list

        # if allowed is empty, we skip the check
        if not allowed:
            return True

        for c in self.selected:
            if c.code not in allowed:
                ok = False
                self.messages.append(
                    f"Course {c.code} is not in your program plan "
                    f"for {self.student.program}, Level {self.student.level}."
                )
        return ok

    def _check_schedule_conflicts(self):
        ok = True
        for i in range(len(self.selected)):
            for j in range(i + 1, len(self.selected)):
                a = self.selected[i]
                b = self.selected[j]
                if self._overlap(a, b):
                    ok = False
                    self.messages.append(
                        f"Schedule conflict: {a.code} overlaps with {b.code}."
                    )
        return ok

    def _overlap(self, c1, c2):
      
        for d1, s1, e1 in c1.schedule:
            for d2, s2, e2 in c2.schedule:
                if d1 != d2:
                    continue
                # if NOT (one ends before the other starts)
                if not (e1 <= s2 or e2 <= s1):
                    return True
        return False

    def _check_capacity(self):
        ok = True
        for c in self.selected:
            if c.enrolled >= c.capacity:
                ok = False
                self.messages.append(
                    f"Course {c.code} is full. Added to waitlist."
                )
                wait = self.waitlist.setdefault(c.code, [])
                if self.student.student_id not in wait:
                    wait.append(self.student.student_id)
        return ok

    # ------------------------- outputs -------------------------

    def build_timetable(self):
        timetable = {}
        for c in self.selected:
            for day, start, end in c.schedule:
                timetable.setdefault(day, []).append((start, end, c.code))

        # sort each day
        for day in timetable:
            timetable[day].sort(key=lambda x: x[0])

        return timetable

    def get_messages(self):
        return self.messages