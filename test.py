import sqlite3 
import os

db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 

sql.execute("INSERT INTO users VALUES (?,?,?,?)", (None, '1323232', '000', 'True'))
db.commit()


