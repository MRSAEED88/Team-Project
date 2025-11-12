import sqlite3 
import random

# creat a file 
con_user = sqlite3.connect('User.db')
# Create users table
info = con_user.cursor()
info.execute("CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY,name TEXT,email TEXT,passWord TEXT,membership TEXT)")
info.execute("CREATE TABLE IF NOT EXISTS students(ID INTEGER PRIMARY KEY,name TEXT,email TEXT,program TEXT,level INTEGER)")





# data = info.execute("SELECT * FROM users")
# data = data.fetchall()
# for row in data:
#     print(row)




con_user.commit()
con_user.close()



class add_db:
    def __init__(self,userinfo, con='User.db'):
        self.con= sqlite3.connect(con)
        self.info= self.con.cursor()
        self.userinfo= userinfo
    def insertData(self):
        self.info.execute(f"INSERT INTO users Values {self.userinfo}")
        self.con.commit()
        self.con.close()
        return None
    


class add_student:
    def __init__(self):
        self.User = []
    
    def createstudent(self,number = 10):
        names = ["Abdulilah", "Saeed", "Sulaiman", "Alaa", "Mohtadi", "Baraa",
                 "Faisal", "Omar", "Khalid", "Ahmed", "Rayan", "Hassan"]
        programs = ["Power and Machines", "Communication and Electronics", "Computer",
                       "Biomedecal"]
        
        for i in range(1,11):
            name = random.choice(names)
            program = random.choice(programs)
            level = random.randint(1,4)
            ID = random.randint(2400000, 2499999)
            passw =random.randint(1234567,2345678)
            
            email = (f"{name.lower()}{i} @kau.edu.stu.com")
            user=add_db((ID,name,email,passw,"student")) 
            user.insertData()

            # student = student(ID, name, email, program, level)
            # self.User.append(student)
        pass
# s= add_student()
# s.createstudent()
