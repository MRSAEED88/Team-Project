from users_db import courses_db
#TODO: we should make the code accept arguments so we can create different sets of courses if needed 
#and it should be available for the admin only
class CourseFactory:
    @staticmethod # => Does not Depend on main clss it is onle order function into the class:
    def create_and_save_courses(): # We sved as a list
        courses = [
            (1, "EE250", "Fundamental of Electrical Circuits", 4, 40, "REQ"), #REQ = I dont know about its req yet.
            (2, "EE201", "Python", 3, 40,"REQ"),
            (3, "EE311", "Electronics", 4, 35,"REQ"),
            (4, "EE300", "Complex", 3, 40,"REQ"),
            (5, "EE301", "Circuit I", 3, 40, "EE2250"),
            (6, "EE341", "Machines", 3, 35,"EE2250"),
        ]

        # Insert each course
        
        for c in courses:
            course=courses_db(c)
            course.course_insert(c)

         # c.get_tuple() = (c.course_id, c.course_code, c.course_name, c.credits, c.capacity, c.prereq)


        # print("6 Courses added successfully!")



CourseFactory.create_and_save_courses()
