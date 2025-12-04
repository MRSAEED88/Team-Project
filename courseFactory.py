import users_db

class CourseFactory:
    @staticmethod 
    def create_and_save_courses():
        # Format: (id, code, name, credits, day, start, end, room, capacity, [prerequisites_list])
        # Note: We added Day, Time, and Room to match your database schema
        courses_data = [
            (1, "EE250", "Fund. of Electrical Circuits", 4, "Mon", "08:00", "09:20", "201", 40, []), 
            (2, "EE201", "Python Programming", 3, "Tue", "10:00", "11:20", "LAB1", 40, []),
            (3, "EE311", "Electronics", 4, "Wed", "09:00", "10:20", "202", 35, ["EE250"]),
            (4, "EE300", "Complex Analysis", 3, "Sun", "11:00", "12:20", "203", 40, ["MATH202"]),
            (5, "EE301", "Circuit I", 3, "Mon", "13:00", "14:20", "201", 40, ["EE250"]),
            (6, "EE341", "Machines", 3, "Thu", "08:00", "09:20", "LAB2", 35, ["EE250"]),
        ]

        print("--- Adding Courses ---")
        for c in courses_data:
            # 1. Prepare data for 'courses' table (exclude the prerequisite list at the end)
            # Tuple: (id, code, name, credits, day, start, end, room, capacity)
            course_tuple = c[:9] 
            
            # Insert Course
            course_obj = users_db.courses_db(course_tuple)
            course_obj.course_insert()
            print(f"Course {c[1]} added.")

            # 2. Insert Prerequisites into 'prerequisites' table
            prereq_list = c[9]
            if prereq_list:
                for pre in prereq_list:
                    # Using the execute_query helper from users_db
                    users_db.execute_query(
                        "INSERT OR IGNORE INTO prerequisites (course_code, prereq_code) VALUES (?, ?)", 
                        (c[1], pre)
                    )

        print("All courses added successfully!")

if __name__ == "__main__":
    users_db.setup_database() # Ensure tables exist
    CourseFactory.create_and_save_courses()
