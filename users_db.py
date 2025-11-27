import sqlite3 
 

# CREAT A FILE
con_user = sqlite3.connect('User.db')
info = con_user.cursor()
#___________________________________________________________________________________
 # CREAT TABLE FOR USERS
info.execute("CREATE TABLE IF NOT EXISTS users(ID INTEGER UNIQUE,name TEXT," 
"email TEXT,passWord TEXT,membership TEXT)")  
#__________________________________________________________________________________
# CREAT TABLE FOR STUDENTS
info.execute("CREATE TABLE IF NOT EXISTS students(ID INTEGER UNIQUE,name TEXT," 
"email TEXT,program TEXT,level INTEGER,transcript TEXT)")

#TODO: we should change the table structure to store transcript instead of hours completed and remaining => (DONE!!)
# but we have to adjust the code accordingly

# #Transcript will be stored as a string so when we retrieve it we can convert it back to a list(we should also convert it to string when storing)

#__________________________________________________________________________________
# CREATE TABLE FOR COURSES
info.execute("CREATE TABLE IF NOT EXISTS courses(ID INTEGER UNIQUE, course_code TEXT,"
"course_name TEXT, credits INTEGER, capacity INTEGER, prereq TEXT)")
#__________________________________________________________________________________
# CREAT Registration Table
info.execute("CREATE TABLE IF NOT EXISTS registration(student_id INTEGER,"
"course_id INTEGER,grade TEXT, UNIQUE(student_id, course_id))")
# UNIQUE(student_id, course_id)) => Student can not recorde the subjects more than one







# Here if we like to check table we uncomment this part

# data = info.execute("SELECT * FROM courses")
# data = data.fetchall()
# for row in data:
#     print(row)


con_user.commit()
con_user.close()


#TODO: We should work on removing unnecessary classes and try to make the code more efficient
# (for example merging claseses that do similar things)

# I commented this part becase its duplicated in added_users class below delete if not needed

# class user_db:
#     def __init__(self,userinfo):
#         self.userinfo = userinfo
#     def insertData(self):
#         info.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", self.userinfo)
         







class student_db:
    def __init__(self, ID, name, email, program, level, transcript):


        self.userinfo = (ID, name, email, program, level, transcript)

    def insertData(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", self.userinfo)
        con_user.commit()
        con_user.close()



class add_users:
    def __init__(self,userinfo):
        self.userinfo= userinfo
    def insertData(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", self.userinfo)
        con_user.commit()
        con_user.close()

#This class is for adding courses to the database
class courses_db:
    def __init__(self,courseinfo):
        self.courseinfo= courseinfo
    def course_insert(self,courseinfo):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT OR REPLACE INTO courses VALUES (?, ?, ?, ?, ?, ?)",self.courseinfo)
        con_user.commit()
        con_user.close()

#The comment is for future use if we decide to add student through this class
    # def insertStudent(self):
    #     self.info.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", self.userinfo)
    #     self.con.commit()
    #     self.con.close()

# class search:
#     def __init__(self, parameter, search_by='id'):
#         self.search_by = search_by.lower()
#         self.parameter = parameter

#     def fetch_user(self):
#         con_user = sqlite3.connect('User.db')
#         info = con_user.cursor()

#         if self.search_by == 'id':
#             info.execute("SELECT * FROM users WHERE ID = ?", (self.parameter,))
        
#         elif self.search_by == 'email':
#             info.execute("SELECT * FROM users WHERE email LIKE ?", (f"%{self.parameter}%"))   # % 
        
#         elif self.search_by == 'name':
#             info.execute("SELECT * FROM users WHERE name LIKE ?", (f"%{self.parameter}%"))
        
#         else:
#             con_user.close()
#             raise ValueError("Invalid search criteria")

#         user_data = info.fetchone()
#         con_user.close()
#         return user_data
class search:
    def __init__(self, parameter, table="users", search_by="id"):
        self.table = table.lower()       # users / students / courses
        self.search_by = search_by.lower()
        self.parameter = parameter

    def fetch(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()

        # ---------------- USERS TABLE ----------------
        if self.table == "users":
            if self.search_by == "id":
                info.execute("SELECT * FROM users WHERE ID = ?", (self.parameter,))
            elif self.search_by == "email":
                info.execute("SELECT * FROM users WHERE email LIKE ?", (f"%{self.parameter}%",))
            elif self.search_by == "name":
                info.execute("SELECT * FROM users WHERE name LIKE ?", (f"%{self.parameter}%",))
            else:
                raise ValueError("Invalid search criteria for users")

        # ---------------- STUDENTS TABLE ----------------
        elif self.table == "students":
            if self.search_by == "id":
                info.execute("SELECT * FROM students WHERE ID = ?", (self.parameter,))
            elif self.search_by == "email":
                info.execute("SELECT * FROM students WHERE email LIKE ?", (f"%{self.parameter}%",))
            elif self.search_by == "name":
                info.execute("SELECT * FROM students WHERE name LIKE ?", (f"%{self.parameter}%",))
            elif self.search_by == "program":
                info.execute("SELECT * FROM students WHERE program LIKE ?", (f"%{self.parameter}%",))
            else:
                raise ValueError("Invalid search criteria for students")

        # ---------------- COURSES TABLE ----------------
        elif self.table == "courses":
            if self.search_by == "id":
                info.execute("SELECT * FROM courses WHERE ID = ?", (self.parameter,))
            elif self.search_by == "course_code":
                info.execute("SELECT * FROM courses WHERE course_code LIKE ?", (f"%{self.parameter}%",))
            elif self.search_by == "name":
                info.execute("SELECT * FROM courses WHERE course_name LIKE ?", (f"%{self.parameter}%",))
            else:
                raise ValueError("Invalid search criteria for courses")
 
     #  WE HAVE TO CORRECT
        else:
            raise ValueError("Invalid table name")

        result = info.fetchone()
        con_user.close()
        return result

#TODO: This method should be tested to ensure it works as expected
  # As you can see here we made a class for creat a courses:


#TODO: I have transferred the code below to courseFactory.py if you dont need the code you can delete it from here


# class CourseFactory:
#     @staticmethod # => Does not Depend on main clss it is onle order function into the class:
#     def create_and_save_courses(): # We sved as a list
#         courses = [
#             (1, "EE250", "Fundamental of Electrical Circuits", 4, 40, "REQ"), #REQ = I dont know about its req yet.
#             (2, "EE201", "Python", 3, 40,"REQ"),
#             (3, "EE311", "Electronics", 4, 35,"REQ"),
#             (4, "EE300", "Complex", 3, 40,"REQ"),
#             (5, "EE301", "Circuit I", 3, 40, "EE2250"),
#             (6, "EE341", "Machines", 3, 35,"EE2250"),
#         ]

#         # Connect to DB
#         con = sqlite3.connect("User.db")
#         cur = con.cursor()

#         # Insert each course
#         for c in courses:
#             cur.execute("""
#                 INSERT OR REPLACE INTO courses(ID, course_code, course_name, credits, capacity, prereq)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             """, c)
#          # c.get_tuple() = (c.course_id, c.course_code, c.course_name, c.credits, c.capacity, c.prereq)

#         con.commit()
#         con.close()

#         # print("6 Courses added successfully!")



# CourseFactory.create_and_save_courses()
