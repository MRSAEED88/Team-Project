from users_db import add_users
class User :
    def __init__(self,user_id : int,name : str,email : str,password : str ,membership : str ):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.membership = membership
    def store_data(self):
        user_info=add_users((self.user_id,self.name,self.email, self.password,self.membership))
        user_info.insertData()


    def is_admin(self):
        return self.membership == "Admin"
    def is_student(self):
        return self.membership == "student"
        pass

