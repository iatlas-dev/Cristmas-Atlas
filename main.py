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
from PyRandomPassword.PyRandomPassword import RandomGeneratePassword as RandomPassword
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
import requests


logging.basicConfig(level=logging.INFO)
#8108818471:AAFlQ4YS8jiXS9tz11Z5qICIWrtQoUnEFcs official
#7323299180:AAGjSoI3TvYGOVsnjCv7Zu_RDgTpIsm2iCU test
bot = Bot(token="7323299180:AAGjSoI3TvYGOVsnjCv7Zu_RDgTpIsm2iCU")

dp = Dispatcher()

db = sqlite3.connect('user.db', check_same_thread = False)
sql = db.cursor() 
db.commit() 
kyiv = pytz.timezone('Europe/Kyiv')
scheduler = AsyncIOScheduler()
letterId = []
ad = [
    "Не можешь придумать поздравление?🤔\nСпроси у chat gpt! https://t.me/GPTAppBot?start=_tgr_L5gBVf4wMzMy",
    "Надо срочно купить или вывести звезды телеграм на подарок твоему другу🎁? Не проблема! https://t.me/starscat_bot?start=_tgr_-IzqPbw5ODli всегда надежно обменивайте свои звезды⭐️"
]

music = [
    "Cristmas Atlas - All I Want for Christmas Is You.mp3",
    "Cristmas Atlas - Deck The Halls.mp3",
    "Cristmas Atlas - Happy New Year.mp3",
    "Cristmas Atlas - Jingle Bell Rock.mp3",
    "Cristmas Atlas - Last Cristmas.mp3",
    "Cristmas Atlas - Let It Snow! Let It Snow! Let It Snow! (with The B. Swanson Quartet).mp3",
    "Cristmas Atlas - Man With The Bag.mp3",
    "Cristmas Atlas - Rockin' Around The Christmas Tree.mp3",
    "Cristmas Atlas - Snowman.mp3",
    "Cristmas Atlas - Щедрик.mp3",
]

class letter(StatesGroup):
    letter = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    if sql.fetchone() is None:
        code = random.randint(1000000,9999999)
        while (True):
            for value in sql.execute("SELECT * FROM game"):
                if str(value[0]) == str(code):
                    code = random.randint(1000000,9999999)
            break
        sql.execute(f"INSERT INTO users VALUES (?,?)", (str(code), json.dumps([])))
        db.commit()

    sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
    value = sql.fetchone()
    value = list(value)

    date = [datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second]
    day = 31 - datetime.now().day
    hour = 23 - datetime.now().hour
    minute = 59 - datetime.now().minute
    second = 60 - datetime.now().second
    code = value[1]
    await message.answer(f"До нового года осталось🎄:\n{day} дней {hour} часов  {minute} минут {second} секунд!\nСсылка для вашей Тайной Санты🎅: https://t.me/ThisIsAtlas_Bot?start={code}")

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


@dp.message(letter.letter)
async def letterMessage(message: types.Message, state: FSMContext):
    messageText = await state.get_data()
    print(message.text)
    a = 0
    for i in letterId:
        if i[0] == message.from_user.id:
            sql.execute(f"SELECT * FROM users WHERE id = {message.from_user.id}")
            value = sql.fetchone()
            value = list(value)
            date = json.loads(value[2])
            date.append(i[1])
            print(date)
            db.commit()
            sql.execute(f"UPDATE users SET letter = ? WHERE id = ?", (json.dumps(date), value[0]))
            db.commit()
            await bot.send_message(i[1], f"Хохохо🎅 Это новое пожелание от Тайного Санты!\n{message.text}")
            await message.answer("Прекрасно! уже отправил поздравление!📧")
            letterId.pop(a)
            if random.randint(1,2) == 1:
                await bot.send_message(message.chat.id, ad[random.randint(0,1)])
            await state.clear()
            return
        a += 1


@dp.message(Command("music"))
async def cmd_start(message: types.Message):
    audio = FSInputFile(music[random.randint(0,9)])
    await bot.send_audio(message.chat.id, audio)

@dp.message(Command("snow"))
async def cmd_start(message: types.Message):
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


async def send_message_day():
    time.sleep(0.22)
    date = [datetime.now().day, datetime.now().hour, datetime.now().minute, datetime.now().second]
    day = 31 - datetime.now().day
    hour = 23 - datetime.now().hour
    minute = 59 - datetime.now().minute
    second = 60 - datetime.now().second
    text = f"До нового года осталось🎄:\n{int(day) - 1} дней 0 часов  0 минут 0 секунд"
    if day == 1:
        text = "С НОВЫМ ГОДОМ!🎆\nКанал автора бота: https:/t.me/AtlasForAmerica"

    for value in sql.execute("SELECT * FROM users"):
        await bot.send_message(chat_id=value[0], text=text)



async def main():
    scheduler.add_job(send_message_day,'cron', day="*", hour=0, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())




