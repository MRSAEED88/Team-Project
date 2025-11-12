import Users_db

class User :
    def __init__(self,user_id,name,email,membership):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.membership = membership
    def store_data(self):
        user_info=Users_db.add_db((self.user_id,self.name,self.email,self.membership))
        user_info.insertData()


    def is_admin(self):
        return self.membership == "Admin"
    def is_student(self):
        return self.membership == "student"
        pass


