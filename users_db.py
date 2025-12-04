import sqlite3 
 

def setup_database():
    """
    Connects to the database and creates all necessary tables if they don't exist.
    This function should be called once when the application starts.
    """
    with sqlite3.connect('User.db') as con:
        info = con.cursor()
        #___________________________________________________________________________________
        # CREAT TABLE FOR USERS
        info.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            membership TEXT)""")
        #__________________________________________________________________________________
        # CREAT TABLE FOR STUDENTS
        info.execute("""CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            program TEXT,
            level INTEGER)""")


        # CREAT TABLE FOR TRANSCRIPTS
        info.execute("""CREATE TABLE IF NOT EXISTS transcripts(
            student_id INTEGER,
            course_code TEXT,
            grade TEXT)""")


        #__________________________________________________________________________________
        # CREATE TABLE FOR COURSES
        info.execute("""CREATE TABLE IF NOT EXISTS courses(
            id INTEGER PRIMARY KEY,
            course_code TEXT UNIQUE,
            course_name TEXT,
            credits INTEGER,
            -- Schedule Info Needed for Conflict Checking:
            day TEXT,          -- e.g., 'Mon', 'Tue'
            start_time TEXT,   -- e.g., '10:00'
            end_time TEXT,     -- e.g., '11:30'
            room TEXT,         -- e.g., 'Room 101'
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
        info.execute("""CREATE TABLE IF NOT EXISTS registration(
            student_id INTEGER,
            course_code TEXT,
            UNIQUE(student_id, course_code))""")
        info.execute("""CREATE TABLE IF NOT EXISTS waitlist(
            student_id INTEGER,
            course_code TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id, course_code)
        )""")
    print("Database setup complete.")


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
    def __init__(self, courseinfo):
        self.courseinfo = courseinfo

    def course_insert(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()
        info.execute("INSERT OR REPLACE INTO courses (id, course_code, course_name, credits, day, start_time, end_time, room, max_capacity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",self.courseinfo)
        con_user.commit()
        con_user.close()






class search:
    def __init__(self, parameter, table="users", search_by="id"):
        self.table = table.lower()
        self.search_by = search_by.lower()
        self.parameter = parameter

    def fetch(self):
        con_user = sqlite3.connect('User.db')
        info = con_user.cursor()

        # -------- USERS --------
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


#---------------------------------------------New--------------------------------------------

def add_to_waitlist(student_id, course_code):
    """Adds a student to the waitlist for a specific course."""
    with sqlite3.connect('User.db') as con:
        # We use INSERT OR IGNORE to prevent crashing if they are already on the waitlist
        con.execute("INSERT OR IGNORE INTO waitlist (student_id, course_code) VALUES (?, ?)", 
                    (student_id, course_code))
        con.commit()
def get_all_courses_data():
    """Fetches all course data required for the RegistrationValidator."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("""
            SELECT c.course_code, c.course_name, c.credits, c.max_capacity, 
                   c.day, c.start_time, c.end_time, GROUP_CONCAT(p.prereq_code)
            FROM courses c
            LEFT JOIN prerequisites p ON c.course_code = p.course_code
            GROUP BY c.course_code
        """)
        courses_data = {}
        for row in cur.fetchall():
            prereqs = (row[7] or "").split(',') if row[7] else []
            courses_data[row[0]] = {
                "name": row[1],
                "credits": row[2],
                "max_capacity": row[3],
                "schedule": [(row[4], row[5], row[6])],
                "prerequisites": prereqs
            }
        return courses_data

def get_full_program_plan():
    """Fetches the entire program plan for the RegistrationValidator."""
    from collections import defaultdict
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT program, level, course_code FROM program_plans")
        program_plan = defaultdict(lambda: defaultdict(list))
        for prog, lvl, code in cur.fetchall():
            program_plan[prog][lvl].append(code)
        return program_plan

def get_current_enrollments():
    """Fetches a dictionary of current enrollments for each course."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT course_code, COUNT(student_id) FROM registration GROUP BY course_code")
        return {row[0]: row[1] for row in cur.fetchall()}

def get_registered_courses(student_id):
    """Fetches all course codes a student is registered for."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT course_code FROM registration WHERE student_id=?", (student_id,))
        return {row[0] for row in cur.fetchall()}

def get_plan_courses(program, level):
    """Fetches all course codes for a given program and level."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT course_code FROM program_plans WHERE program=? AND level=?", (program, level))
        return {row[0] for row in cur.fetchall()}

def get_completed_courses(student_id):
    """Fetches all course codes from a student's transcript."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT course_code FROM transcripts WHERE student_id=?", (student_id,))
        return {row[0] for row in cur.fetchall()}

def get_course_credits(course_code):
    """Fetches the credits for a single course."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT credits FROM courses WHERE course_code=?", (course_code,))
        result = cur.fetchone()
        return result[0] if result else 0

def get_credits_for_courses(course_codes):
    """Calculates the total credit hours for a given list of course codes."""
    return sum(get_course_credits(code) for code in course_codes)

def execute_query(query, params=()):
    """A general purpose function to execute insert/update/delete queries."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute(query, params)
        con.commit()

def register_course_for_student(student_id, course_code):
    """Registers a student for a specific course in the registration table."""
    query = "INSERT INTO registration (student_id, course_code) VALUES (?, ?)"
    execute_query(query, (student_id, course_code))

def drop_course_for_student(student_id, course_code):
    """Removes a student's course registration from the registration table."""
    query = "DELETE FROM registration WHERE student_id=? AND course_code=?"
    execute_query(query, (student_id, course_code))

def get_all_courses():
    """Fetches all courses from the database."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("SELECT course_code, course_name, credits, max_capacity, day, start_time, end_time, room FROM courses ORDER BY course_code")
        return cur.fetchall()

def delete_course(course_code):
    """Deletes a course from the courses table."""
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM courses WHERE course_code=?", (course_code,))
        cur.execute("DELETE FROM prerequisites WHERE course_code=? OR prereq_code=?", (course_code, course_code))
        cur.execute("DELETE FROM program_plans WHERE course_code=?", (course_code,))
        cur.execute("DELETE FROM registration WHERE course_code=?", (course_code,))

if __name__ == "__main__":
    # This block now correctly sets up the database and then runs a test.
    setup_database()

    # This block is for testing the database script directly.
    # It's better to manage connections here rather than globally.
    db_conn = sqlite3.connect('User.db')
    cursor = db_conn.cursor()

    print("Students in the database:")
    for row in cursor.execute("SELECT * FROM users"):
        print(row)
    db_conn.close()
