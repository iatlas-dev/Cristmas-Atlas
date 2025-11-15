import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile
from aiogram import F
import random
import json
from datetime import datetime
import pytz
import sqlite3 
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
import requests
import os 
import secrets
import csv


logging.basicConfig(level=logging.INFO)
#8108818471:AAFlQ4YS8jiXS9tz11Z5qICIWrtQoUnEFcs official
#7323299180:AAGI8BXbwCxAjqz7umINVHVPrunnp-onASQ test
bot = Bot(token="7323299180:AAGI8BXbwCxAjqz7umINVHVPrunnp-onASQ")
dp = Dispatcher()


db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 
kyiv = pytz.timezone('Europe/Kyiv')
scheduler = AsyncIOScheduler()
letterId = []
music = os.listdir('music')
rality = {0: 'Ну почти редко', 1: 'редко', 2: ' ничосе', 3: 'ФИГАСЕ', 4: '(⊙_⊙)', 5: 'СУПЕР|ПУПЕР|ОМЕГА|ГИПЕР|УЛЬТРА|ПРО|МАКС|НЕ|АЙФОН'}

class letter(StatesGroup):
    letter = State()



@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?)", (None, secrets.token_urlsafe(6), message.from_user.id, json.dumps([]), json.dumps([True, True])))
        db.commit()
    
    if " " in message.text:
        code = message.text.split()[1]
    
        sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id))
        value = sql.fetchone()
        value = list(value)
        date = json.loads(value[2])
        sql.execute(f"SELECT * FROM users WHERE idSanta = ?", (code[0]))
        value = sql.fetchone()
        value = list(value)
        if value[0] in date:
            await message.answer("Ооу🤨 Кажеться ты уже отправлял пожелания этому пользователю😶")
            return
        await message.answer(f"Напиши мне свое пожелание которые ты хотел бы пожелать и я секретно передам человеку от которого ты получил ссылку😉")
        a = 0
        for i in letterId:
            if i[0] == message.from_user.id:
                letterId.pop(a)
            a += 1
        letterId.append([message.from_user.id, value[0]])
        await state.set_state(letter.letter.state)

    else: 
        sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
        value = sql.fetchone()
        value = list(value)
        
        date = [datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second]
        day = 365 - datetime.now().timetuple().tm_yday
        hour = 23 - datetime.now().hour
        minute = 59 - datetime.now().minute
        second = 60 - datetime.now().second
        code = str(value[0]) + value[1]
        await message.answer(f"До нового года осталось🎄:\n{day} дней {hour} часов  {minute} минут {second} секунд!\n\nСсылка для вашей Тайной Санты🎅: https://t.me/ThisIsAtlas_Bot?start={str(code)}")



@dp.message(letter.letter)
async def letterMessage(message: types.Message, state: FSMContext):
    a = 0
    for i in letterId:
        if i[0] == message.from_user.id:
            sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id))
            value = sql.fetchone()
            value = list(value)
            date = json.loads(value[2])
            date.append(i[1])
            db.commit()
            sql.execute(f"UPDATE users SET letter = ? WHERE id = ?", (json.dumps(date), value[0]))
            db.commit()
            await bot.send_message(i[1], f"Хохохо🎅 Это новое пожелание от Тайного Санты!\n{message.text}")
            await message.answer("Прекрасно! уже отправил поздравление!📧")
            await state.clear()
            return
        a += 1


@dp.message(Command("music"))
async def cmd_music(message: types.Message):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?)", (None, secrets.token_urlsafe(6), message.from_user.id, json.dumps([]), json.dumps([True, True])))
        db.commit()
    audio = FSInputFile(f'music/{music[random.randint(0, len(music) - 1)]}')
    await bot.send_audio(message.chat.id, audio)

@dp.message(Command("snow"))
async def cmd_snow(message: types.Message):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?)", (None, secrets.token_urlsafe(6), message.from_user.id, json.dumps([]), json.dumps([True, True])))
        db.commit()
    time.sleep(0.2)
    city = message.text.split()[1]
    res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params={'q': f'{city}', 'type': 'like', 'units': 'metric', 'APPID': '2b845cde2521735273dfaba14ada0b8f'})
    data = res.json()
    print(data)
    if data['cod'] != '200':
        await message.answer('Ошибка! Твой город не найден!😨\nПопбробуй ввести название на англиском, а еще лучше с аббревиатурой страны❗\nНапример:\nOdesa,UA\nKyiv,UA\nOttava,CA\nAkita,JP')

    date = "00-00-00"
    day = -1
    for i in data['list']:
        if i['dt_txt'][:10] != date:
            day += 1
            if "snow" in i['weather'][0]['description']:
                await message.answer(f"Ого☃! У тебя выпадет снег через {day} дней!❄")
                return
            date = i['dt_txt'][:10]
    
    await message.answer("Печально😢 У тебя пока что не наблюдаеться снег")   

@dp.message(Command("mandarin"))
async def cmd_mandrin(message: types.Message):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?)", (None, secrets.token_urlsafe(6), message.from_user.id, json.dumps([]), json.dumps([True, True])))
        db.commit()
    with open('mandarin.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        mandarin = list(reader)
        wish = mandarin[random.randint(0, len(mandarin)-1)]
        await message.answer(f'Судьба говорит что: {wish[0]}\n\nРедкость: {rality[int(wish[1])]}')

@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?)", (None, secrets.token_urlsafe(6), message.from_user.id, json.dumps([]), json.dumps([True, True])))
        db.commit()
    builder = InlineKeyboardBuilder()
    sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    value = sql.fetchone()
    value = list(value)
    settings = json.loads(value[4])
    builder.add(types.InlineKeyboardButton(
        text=f"{'Выключить' if settings[0] == True else 'Включить'} уведомления об отчете до НГ",
        callback_data = "notifactions"
    ))
    builder.add(types.InlineKeyboardButton(
        text=f"{'Не приимать' if settings[1] == True else 'Принимать'} сообщения от Тайного Санты",
        callback_data = "santa"
    ))
    await message.answer("🎄Настройки Нового Года:", reply_markup=builder.as_markup())


async def send_message_day():
    time.sleep(0.22)
    day = 365 - datetime.now().timetuple().tm_yday
    text = f"До нового года осталось🎄:\n{int(day) - 1} дней 0 часов  0 минут 0 секунд"
    if day == 1:
        text = "С НОВЫМ ГОДОМ!🎆\nКанал автора бота: https:/t.me/AtlasForAmerica"

    for value in sql.execute("SELECT * FROM users"):
        if value[3] == "True":
            await bot.send_message(chat_id=value[0], text=text)



async def main():
    scheduler.add_job(send_message_day,'cron', day="*", hour=0, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




