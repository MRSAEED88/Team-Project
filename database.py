import sqlite3 as sql
con=sql.connect("Database.db")
cursor=con.cursor()

con.commit()
con.close()