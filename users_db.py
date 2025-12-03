import sqlite3 
 

# CREAT A FILE
con_user = sqlite3.connect('User.db')
info = con_user.cursor()
#___________________________________________________________________________________
 # CREAT TABLE FOR USERS
# CREAT TABLE FOR USERS
info.execute("CREATE TABLE IF NOT EXISTS users("
"id INTEGER PRIMARY KEY,"
"name TEXT,"
"email TEXT UNIQUE,"
"password TEXT,"
"membership TEXT)")
#__________________________________________________________________________________
# CREAT TABLE FOR STUDENTS
# CREAT TABLE FOR STUDENTS
info.execute("CREATE TABLE IF NOT EXISTS students("
"id INTEGER PRIMARY KEY,"
"name TEXT,"
"email TEXT,"
"program TEXT,"
"level INTEGER)")


#TODO: we should change the table structure to store transcript instead of hours completed and remaining => (DONE!!)
# but we have to adjust the code accordingly

# #Transcript will be stored as a string so when we retrieve it we can convert it back to a list(we should also convert it to string when storing)


# CREAT TABLE FOR TRANSCRIPTS
info.execute("CREATE TABLE IF NOT EXISTS transcripts("
"student_id INTEGER,"
"course_code TEXT,"
"grade TEXT)")



#__________________________________________________________________________________
# CREATE TABLE FOR COURSES
# CREATE TABLE FOR COURSES

#TODO check here i added max capcity column to limit number of students in a course
info.execute("""CREATE TABLE IF NOT EXISTS courses(
    id INTEGER PRIMARY KEY,
    course_code TEXT UNIQUE,
    course_name TEXT,
    credits INTEGER,
    lecture_hours INTEGER,
    lab_hours INTEGER,
    max_capacity INTEGER)""")


# CREATE TABLE FOR PROGRAM PLANS
info.execute("""CREATE TABLE IF NOT EXISTS program_plans(
    program TEXT,
    level INTEGER,
    course_code TEXT,
    PRIMARY KEY (program, level, course_code))""")

# CREATE TABLE FOR PREREQUISITES
info.execute("CREATE TABLE IF NOT EXISTS prerequisites("
"course_code TEXT,"
"prereq_code TEXT)")
#__________________________________________________________________________________
# CREAT Registration Table
# CREAT Registration Table
info.execute("CREATE TABLE IF NOT EXISTS registration("
"student_id INTEGER,"
"course_code TEXT,"
"UNIQUE(student_id, course_code))")

# UNIQUE(student_id, course_id)) => Student can not recorde the subjects more than one


#TODO: We should work on removing unnecessary classes and try to make the code more efficient
# (for example merging claseses that do similar things)


class student_db:
    def __init__(self, ID, name, email, program, level):


        self.userinfo = (ID, name, email, program, level)

    def insertData(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT INTO students (id, name, email, program, level) VALUES (?, ?, ?, ?, ?)", self.userinfo)
        con_user.commit()
        con_user.close()



class add_users:
    def __init__(self,userinfo):
        self.userinfo= userinfo
    def insertData(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT INTO users (id, name, email, password, membership) VALUES (?, ?, ?, ?, ?)", self.userinfo)
        con_user.commit()
        con_user.close()
#The comment is for future use if we decide to add student through this class
    # def insertStudent(self):
    #     self.info.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)", self.userinfo)
    #     self.con.commit()
    #     self.con.close()

#This class is for adding courses to the database

class courses_db:
    def __init__(self,courseinfo):
        self.courseinfo= courseinfo
    def course_insert(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT OR REPLACE INTO courses (id, course_code, course_name, credits, lecture_hours, lab_hours, max_capacity) VALUES (?, ?, ?, ?, ?, ?, ?)",self.courseinfo)
        con_user.commit()
        con_user.close()






class search:
    def __init__(self, parameter, table="users", search_by="id"):
        self.table = table.lower()       # users / students / courses
        self.search_by = search_by.lower()
        self.parameter = parameter

    
    #TODO: This method should be tested to ensure it works as expected
  # As you can see here we made a class for creat a courses:



    def fetch(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()

        # ---------------- USERS TABLE ----------------
        if self.table == "users":
            if self.search_by == "id":
                info.execute("SELECT * FROM users WHERE id = ?", (self.parameter,))
            elif self.search_by == "email":
                info.execute("SELECT * FROM users WHERE email LIKE ?", (f"%{self.parameter}%",))
            elif self.search_by == "name":
                info.execute("SELECT * FROM users WHERE name LIKE ?", (f"%{self.parameter}%",))
            else:
                raise ValueError("Invalid search criteria for users")

        # ---------------- STUDENTS TABLE ----------------
        elif self.table == "students":
            if self.search_by == "id":
                info.execute("SELECT * FROM students WHERE id = ?", (self.parameter,))
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
                info.execute("SELECT * FROM courses WHERE id = ?", (self.parameter,))
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

if __name__ == "__main__":
    # This block is for testing the database script directly.
    # It's better to manage connections here rather than globally.
    db_conn = sqlite3.connect('User.db')
    cursor = db_conn.cursor()

    print("Students in the database:")
    for row in cursor.execute("SELECT * FROM students"):
        print(row)
    db_conn.close()
