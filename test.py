import sqlite3 
import os
from datetime import datetime
import csv
import random
import json

from datetime import datetime
import pytz

try:
    desired_timezone = pytz.timezone('America/New_Yok')
except:
    print('error timezone')
    


now_utc = datetime.now(pytz.utc)
now_in_desired_timezone = now_utc.astimezone(desired_timezone)

print(f"Current time in New York: {now_in_desired_timezone}")
