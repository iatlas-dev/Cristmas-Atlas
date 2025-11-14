import sqlite3 
import os
from datetime import datetime

db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 

print(datetime.now().timetuple().tm_yday)


