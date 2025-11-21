import sqlite3 
 

# CREAT A FILE
con_user = sqlite3.connect('User.db')
info = con_user.cursor()
 # CREAT TABLE FOR USERS
info.execute("CREATE TABLE IF NOT EXISTS users(ID INTEGER UNIQUE,name TEXT," 
"email TEXT,passWord TEXT,membership TEXT)")  
#__________________________________________________________________________________
# CREAT TABLE FOR STUDENTS
info.execute("CREATE TABLE IF NOT EXISTS students(ID INTEGER UNIQUE,name TEXT," 
"email TEXT,program TEXT,level INTEGER,hours_completed INTEGER," 
"hours_remaining INTEGER)")
#__________________________________________________________________________________
# CREATE TABLE FOR COURSES
info.execute("CREATE TABLE IF NOT EXISTS courses(ID INTEGER UNIQUE, course_code TEXT,"
"course_name TEXT, credits INTEGER, capacity INTEGER, prereq TEXT)")
#__________________________________________________________________________________

# Here we would like to tcheck from student's table
# data = info.execute("SELECT * FROM students")
# data = data.fetchall()
# for row in data:
#     print(row)


con_user.commit()
con_user.close()



class user_db:
    def __init__(self,userinfo):
        self.userinfo = userinfo
    def insertData(self):
        info.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", self.userinfo)
         







class student_db:
    def __init__(self, ID, name, email, program, level, hours_completed, hours_remaining):


        self.userinfo = (ID, name, email, program, level, hours_completed, hours_remaining)

    def insertData(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", self.userinfo)
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


#The comment is for future use if we decide to add student through this class
    # def insertStudent(self):
    #     self.info.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", self.userinfo)
    #     self.con.commit()
    #     self.con.close()

class serach:
    def __init__(self,parameter,serch_by='id'):
        self.serch_by = serch_by
        self.parameter = parameter


    def fetch_user(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()

        info.execute("SELECT * FROM users WHERE id = (?)", self.parameter)
        user_data = info.fetchone()
        con_user.commit()
        con_user.close()

        return user_data

  # As you can see here we made a class for creat a courses:

class CourseFactory:
    @staticmethod # => Does not Depend on main clss it is onle order function into the class:
    def create_and_save_courses(): # We sved as a list
        courses = [
            Course(1, "EE250", "Fundamental of Electrical Circuits", 4, 40, "REQ"), #REQ = I dont know about its req yet.
            Course(2, "EE201", "Python", 3, 40,"REQ"),
            Course(3, "EE311", "Electronics", 4, 35,"REQ"),
            Course(4, "EE300", "Complex", 3, 40,"REQ"),
            Course(5, "EE301", "Circuit I", 3, 40, "EE2250"),
            Course(6, "EE341", "Machines", 3, 35,"EE2250"),
        ]

        # Connect to DB
        con = sqlite3.connect("User.db")
        cur = con.cursor()

        # Insert each course
        for c in courses:
            cur.execute("""
                INSERT OR REPLACE INTO courses(ID, course_code, course_name, credits, capacity, prereq)
                VALUES (?, ?, ?, ?, ?, ?)
            """, c.get_tuple())
         # c.get_tuple() = (c.course_id, c.course_code, c.course_name, c.credits, c.capacity, c.prereq)

        con.commit()
        con.close()

        # print("6 Courses added successfully!")




