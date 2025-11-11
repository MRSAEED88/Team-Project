class User :
    def __init__(self,user_id,name,emal,membership):
        self.user_id = user_id
        self.name = name
        self.emal = emal
        self.membership = membership

    def is_admin(self):
        return self.membership == "Admin"
    
        pass
