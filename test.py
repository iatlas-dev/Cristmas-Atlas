import sqlite3 
import os
from datetime import datetime
import csv
import random

db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 
wish = [["Капец походу в зиме 4 месяца: Ноябрь,Декабрь,Январь,Февраль", 0],
["Наверное должен в эту пору пойти снег", 0],
["Вы должны съесть 5 штук мандаринов сейчас же", 0],
["Оливье на новый год ждет вас", 0],
["Робуксы не дают за паркур", 0],
["Мне не платят за то что я говорю", 0],
["Не забудьте поздравить родственников с Новым Годом когда он наступит!", 0],
["Поздравляю! Happy crisis!", 0],
["Посидим до следующей хорошей цитаты тут?", 0]]



with open('mandarin.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    mandarin = list(reader)
    print(mandarin[random.randint(0, len(mandarin)-1)][0])



