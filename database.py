import sqlite3 

con_user = sqlite3.connect('User.dp')
# Creat  users table
info = con_user.cursor()
info.execute("CREATE TABLE users(user INTEGAR,name TEXT,emal TEXT,membership TEXT)")
con_user.commit
con_user.close()
