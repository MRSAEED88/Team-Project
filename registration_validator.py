class RegistrationValidator:
    def __init__(self, courses_data, program_plan, max_credits=18, min_credits=0):
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
        """
        Checks if the course belongs to the student's Program.
        UPDATED: Allows courses from ANY level within that program.
        """
        # Get the dictionary of all levels for this specific program
        # Structure: {1: ['EE201'], 2: ['EE250'], ...}
        program_levels = self.program_plan.get(student_program, {})

        # Flatten into a single list of all allowed courses for this Major
        allowed_in_major = []
        for level_courses in program_levels.values():
            allowed_in_major.extend(level_courses)

        for course in selected_courses:
            if course not in allowed_in_major:
                return False, f"{course} is not in the {student_program} plan."
        
        return True, "Program plan OK."

    def check_schedule_conflicts(self, selected_courses):
        # Helper to convert HH:MM to minutes
        def to_minutes(t_str):
            h, m = map(int, t_str.split(':'))
            return h * 60 + m

        # 1. Build a list of time slots for all selected courses
        # Structure: {'CourseCode': [('Day', StartMin, EndMin), ...]}
        course_slots = {}
        
        for course in selected_courses:
            schedule_list = self.courses_data[course].get("schedule", [])
            slots = []
            for item in schedule_list:
                # item is (DaysString, StartStr, EndStr) -> e.g., ('Sun/Tue', '10:00', '11:20')
                days_str, start_str, end_str = item
                
                # --- Modification Here ---
                # We normalize the separator (replace / with ,) and split to handle each day individually.
                # This ensures "Sun/Tue" creates two separate checks: one for Sun, one for Tue.
                individual_days = days_str.replace('/', ',').split(',')
                
                start_min = to_minutes(start_str)
                end_min = to_minutes(end_str)

                for day in individual_days:
                    day = day.strip() # Remove any extra whitespace
                    if day:
                        slots.append((day, start_min, end_min))
            
            course_slots[course] = slots

        # 2. Compare every course against every other course
        courses_list = list(course_slots.keys())
        for i in range(len(courses_list)):
            for j in range(i + 1, len(courses_list)):
                c1 = courses_list[i]
                c2 = courses_list[j]
                
                for slot1 in course_slots[c1]:
                    for slot2 in course_slots[c2]:
                        # Check Day Match
                        if slot1[0] == slot2[0]:
                            # Check Time Overlap: (StartA < EndB) and (StartB < EndA)
                            if slot1[1] < slot2[2] and slot2[1] < slot1[2]:
                                return False, f"Conflict: {c1} overlaps with {c2} on {slot1[0]}."

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
