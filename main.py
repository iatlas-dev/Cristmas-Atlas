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

class letter(StatesGroup):
    letter = State()



@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?)", (, message.from_user.id, json.dumps([]), 'True'))
        db.commit()

    
    if " " in message.text:
        code = message.text.split()[1]
    
        sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
        value = sql.fetchone()
        value = list(value)
        date = json.loads(value[2])
        sql.execute(f"SELECT * FROM users WHERE idSanta = {code}")
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
        sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
        value = sql.fetchone()
        value = list(value)
        
        date = [datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second]
        day = 365 - datetime.now().timetuple().tm_yday
        hour = 23 - datetime.now().hour
        minute = 59 - datetime.now().minute
        second = 60 - datetime.now().second
        code = value[0]
        await message.answer(f"До нового года осталось🎄:\n{day} дней {hour} часов  {minute} минут {second} секунд!\n\nСсылка для вашей Тайной Санты🎅: https://t.me/ThisIsAtlas_Bot?start={str(code)}")



@dp.message(letter.letter)
async def letterMessage(message: types.Message, state: FSMContext):
    a = 0
    for i in letterId:
        if i[0] == message.from_user.id:
            sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
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
    audio = FSInputFile(f'music/{music[random.randint(0, len(music) - 1)]}')
    await bot.send_audio(message.chat.id, audio)

@dp.message(Command("snow"))
async def cmd_snow(message: types.Message):
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

dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    await message.answer("🎄Настройки Нового Года:")


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




