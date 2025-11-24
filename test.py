import sqlite3 
import os
from datetime import datetime, timedelta
import csv
import random
import json
import pytz

delta = timedelta(hours=5)

try:
    desired_timezone = pytz.timezone('Europe/Kyiv')
except:
    print('error timezone')
    

date = datetime.now()

print(int(date.timestamp()))
