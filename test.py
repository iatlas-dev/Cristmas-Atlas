import sqlite3 
import os
from datetime import datetime
import csv
import random
import json
db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 
wish = [[json.dumps({0: 'Ну почти редко', 1: 'редко', 2: ' ничосе', 3: 'ФИГАСЕ', 4: '(⊙_⊙)', 5: 'СУПЕР|ПУПЕР|ОМЕГА|ГИПЕР|УЛЬТРА|ПРО|МАКС|НЕ|АЙФОН'}), 0], ['000', 0]]


with open('mandarin.csv', 'w', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerows(wish)

with open('mandarin.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    mandarin = list(reader)
    print(mandarin)



