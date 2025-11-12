import sqlite3 

# creat a file 
con_user = sqlite3.connect('User.db')
# Create users table
info = con_user.cursor()
info.execute("CREATE TABLE IF NOT EXISTS users(ID INTEGER PRIMARY KEY,name TEXT,email TEXT ,membership TEXT)")

con_user.commit()
con_user.close()


class add_db:
    def __init__(self,userinfo, con='User.db'):
        self.con= sqlite3.connect(con)
        self.info= self.con.cursor()
        self.userinfo= userinfo
    def insertData(self):
        self.info.execute("INSERT INTO users Values(?,?,?,?)", self.userinfo)
        self.con.commit()
        self.con.close()
        return None
    
