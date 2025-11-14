import classes
import users_db
import random


class add_student:
    def __init__(self):
        self.User = []
    
    def createstudent(self,number = 10):
        names = ["Abdulilah", "Saeed", "Sulaiman", "Alaa", "Mohtadi", "Baraa",
                 "Faisal", "Omar", "Khalid", "Ahmed", "Rayan", "Hassan"]
        programs = ["Power and Machines", "Communication and Electronics", "Computer",
                       "Biomedecal"]
        
        for i in range(1,number):
            name = random.choice(names)
            program = random.choice(programs)
            level = random.randint(1,4)
            ID = random.randint(2400000, 2499999)
            passw =random.randint(1234567,2345678)
            
            email = (f"{name.lower()}{i}@kau.edu.stu.com")
            user=users_db.add_users((ID,name,email,passw,"student")) 
            user.insertData()

            student =classes.Student(ID, name, email,passw, program, level)
            student.store_data()
            self.User.append(student)
        # pass
s= add_student()
s.createstudent()

# # To test searching for a student by ID
# id=('2433632')
# serch_student= users_db.serach([id])
# student_data=serch_student.fetch_user()
# print(student_data)

