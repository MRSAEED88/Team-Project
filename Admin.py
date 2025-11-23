from User import User 

class Admin(User):
    def __init__(self):
        self.__courses = {}        # private # storage the courses here
        self.__program_plans = {}  # private #storage plans of programs here


    # Getter: allow reading courses 
    def get_courses(self):
        return self.__courses

    # Getter: allow reading program plans 
    def get_program_plans(self):
        return self.__program_plans

    #from here the admin can be able to add new course
    def add_course(self, code, name, credits, lec_hours, lab_hours, prerequisites, max_capacity):

        #Check for missing required data
        if not all([code, name, credits, lec_hours, lab_hours, max_capacity]) or prerequisites is None:
            return False, "All fields are mandatory."

        #here we check if the code of course is already exists before
        if code in self.courses:
            return False, f"Course code '{code}' already exists."

        #check is the credits positve
        if credits <= 0:
            return False, "Credits must be positive."

        #check that all the prerequisite courses the admin wants to set are already defined in {self.courses} 
        for pre in prerequisites:
            if pre not in self.courses: 
                return False, f"Prerequisite '{pre}' is not a valid course."

        # Now after we verified everything is ok we can now add the course as a new course
        
        self.courses[code] = {
            "name": name,
            "credits": credits,
            "lec_hours": lec_hours,           #self.cources is a storage for all courses and the key for each course is "corse code" 
            "lab_hours": lab_hours,           #such as (ISLS301,EE250), and its value is a second dictionary with all the course details inside(name,lec_hours.......)
            "prerequisites": prerequisites,
            "max_capacity": max_capacity
        }

        return True, f"Course '{code}' added successfully."
    


    ##Enable administrators to define and manage the program plans##

    #Allow the Admin to specify the Program Plan for every program such as(Computer Engineering) with detail 
    # of the required courses per level or semester. for example (Power) - level(3) its courses will be EE491 - EE351........
    def define_program_plan(self, program, level, course_codes):
        if program not in ["Computer", "Comm", "Power", "Biomedical"]:
            return False, "Invalid program."

        #here, check is the all courses that admin want to added in the program are defined in the system before (self.courses)
        for c in course_codes:
            if c not in self.courses:
                return False, f"Course '{c}' not found in system."

       # Add or update the plan for this program and level
        
        if program not in self.program_plans: # Check if the program was defined before in the system (self.program_plans)
            self.program_plans[program] = {}         # if one of the four programs was not defined before, it will be defined here.
        self.program_plans[program][level] = course_codes  #Here, the program is actually saved in the system by its name and level
        #                              ##the course_codes refers to the list of courses belonging to that program##
        # now the admin can make updates in the plans of program
        #                      for example: self.program_plans["Computer"]["Level 3 - Semester 1"] = ["MATH241", "EE203", "EE300"]

        # Finally, adding the program
        return True, f"Program plan for {program} - {level} added successfully."
