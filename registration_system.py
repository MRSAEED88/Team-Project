class RegistrationValidator:
    def __init__(self, courses_data, program_plan, max_credits=18, min_credits=12):
        self.courses_data = courses_data
        self.program_plan = program_plan
        self.max_credits = max_credits
        self.min_credits = min_credits

    
        #check that all prerequisites for selected courses are completed

    def check_prerequisites(self, selected_courses, completed_courses):
        #Check if the course exists in the system.
        for course in selected_courses: 
            if course not in self.courses_data:
                return False, f"Course {course} does not exist."
            # 
            prereqs = self.courses_data[course].get("prerequisites", [])
            for prereq in prereqs:
                if prereq not in completed_courses:
                    return False, f"Cannot register for {course}: prerequisite {prereq} not completed."
        return True, "Prerequisites OK."
    

    #                   Sum the credit hours of the courses to be registered, and confirm that the total is 
    # within the allowed maximum and minimum.


    def check_credit_hours(self, selected_courses):
        total_credits = sum(self.courses_data[course]["credits"] for course in selected_courses)
        if total_credits < self.min_credits:
            return False, f"Credit hours too low ({total_credits}). Minimum is {self.min_credits}."
        if total_credits > self.max_credits:
            return False, f"Credit hours too high ({total_credits}). Maximum is {self.max_credits}."
        return True, "Credit hours OK."

    def check_program_plan(self, selected_courses, student_program, student_level):
        allowed_courses = self.program_plan.get(student_program, {}).get(student_level, [])
        for course in selected_courses:
            if course not in allowed_courses:
                return False, f"{course} is not allowed in {student_program} Level {student_level}."
        return True, "Program plan OK."

    def check_schedule_conflicts(self, selected_courses):
        schedule_slots = {}
        for course in selected_courses:
            schedule = self.courses_data[course].get("schedule", [])
            for slot in schedule:
                if slot in schedule_slots:
                    return False, f"Schedule conflict: {course} overlaps with {schedule_slots[slot]} at {slot}."
                schedule_slots[slot] = course
        return True, "No schedule conflicts."

    def check_capacity(self, selected_courses, current_enrollments):
        for course in selected_courses:
            max_cap = self.courses_data[course].get("max_capacity", 0)
            enrolled = current_enrollments.get(course, 0)
            if enrolled >= max_cap:
                return False, f"{course} is full."
        return True, "Capacity OK."

    def validate_registration(self, selected_courses, completed_courses, student_program,student_level, current_enrollments):
        checks = [
            self.check_prerequisites(selected_courses, completed_courses),
            self.check_credit_hours(selected_courses),
            self.check_program_plan(selected_courses, student_program, student_level),
            self.check_schedule_conflicts(selected_courses),
            self.check_capacity(selected_courses, current_enrollments)
        ]
        for result, msg in checks:
            if result == False:
                return False, msg
        return True, "Registration successful!"
