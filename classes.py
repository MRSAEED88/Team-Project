import users_db

# testcase_admin = users_db.add_users((1234,"Admin","admin@kau.edu.sa","12345678","Admin"))
# testcase_admin.insertData()
class User :
    def __init__(self,user_id,name,email,membership):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.membership = membership
    def store_data(self):
        user_info=users_db.add_users((self.user_id,self.name,self.email, self.password,self.membership))
        user_info.insertData()


    def is_admin(self):
        return self.membership == "Admin"
    def is_student(self):
        return self.membership == "student"
        pass

#-----------------------------------------------------------------------------------------------------------------

class Student(User):
    def __init__(self, user_id, name, email, program, level):
        super().__init__(user_id,name,email,"student")
        self.program = program
        self.level = level
        self.transcript = []
#______________________________________________________________________________________________________________________________________
    # Connect with data base:
     def store_data(self):
        student_info=users_db.add_students((self.user_id,self.name,self.email, self.password,self.membership,self.program,self.level,self.transcript))
        student_info.insertData()
#_______________________________________________________________________________________________________________________________________
    def validate_student(self):
        if not self.student_id or not self.name or not self.email:          # checking the inputs ID,NAME,EMAIL
            return False, "All fields are required."
        if self.program not in ["Computer", "Comm", "Power", "Biomedical"]: #Checking the program of student is from this choices
            return False, "Invalid program name."
        if self.level <= 0:
            return False, "Level must be greater than zero."  
        return True, "Student data is valid."
    
     # show academic history
    def view_transcript(self):
        if not self.transcript:                       #if the list of transcript is empty will print (no courses completed yet)
            print("no courses completed yet.")
        else:
            print(f"Transcript for {self.name}:")
            for record in self.transcript:
                print(f"- {record['course_code']}: {record['grade']}")

# When we have finished Courses Class  inshAllah ,we will add 3 methods more wich are (Add,remove,show) courses

#------------------------------------------------------------------------------------------------------------------------------

class Admin:
    def __init__(self):
        self.courses = {}  # storage the courses here
        self.program_plans = {}  #storage plans of programs here

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
    # of the required courses. for example (Power and machines) - level(3) its courses will be EE491 - EE351........                           
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
