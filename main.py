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
from contextlib import suppress
from aiogram.exceptions import TelegramBadRequest


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
musicFolder = os.listdir('music')
musics = []
for music in musicFolder:
    musics.append(FSInputFile(f'music/{music}'))


class letter(StatesGroup):
    letter = State()

def get_user(message):
    sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (None, secrets.token_urlsafe(10), message.from_user.id, message.from_user.full_name, json.dumps([]), json.dumps([True, True]), json.dumps([0, 0])))
        db.commit()
    sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    value = sql.fetchone()
    value = list(value)
    if message.chat.type == "group" or "supergroup":
        sql.execute(f"SELECT * FROM chats WHERE chat_id = ?", (message.chat.id,))
        if sql.fetchone() is None:
            sql.execute("INSERT INTO chats VALUES (?,?)", (message.chat.id, json.dumps([message.from_user.id])))
            db.commit()
            value_chat = sql.fetchone()
            return list(value)
        sql.execute(f"SELECT * FROM chats WHERE chat_id = ?", (message.chat.id,))
        value_chat = sql.fetchone()
        members = json.loads(value_chat[1])
        if message.from_user.id not in members:
            members.append(message.from_user.id)
            sql.execute('UPDATE chats SET members = ? WHERE chat_id = ?', (json.dumps(members), message.chat.id))
            db.commit()
    if value[3] != message.from_user.full_name:
        sql.execute('UPDATE users SET name = ? WHERE id = ?', (message.from_user.full_name, message.from_user.id))
    return value

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    value = get_user(message)

    if " " in message.text:
        code = message.text.split()[1]
        date = json.loads(value[4])
        sql.execute(f"SELECT * FROM users WHERE idSanta = ?", (code[0]))
        value = sql.fetchone()
        value = list(value)
        if value == None and value[1] != code[1:]:
            await message.answer("Ооу🤨 Кажеться такого пользователя не существует или ссылка не действительна")
            return
        if value[2] in date:
            await message.answer("Ооу🤨 Кажеться ты уже отправлял пожелания этому пользователю😶")
            return
        if json.loads(value[5])[1] == False:
            await message.answer("Ооу🤨 Кажеться этот пользователь закрыл эту ссылку...")
        await message.answer(f"Напиши мне свое пожелание которые ты хотел бы пожелать и я секретно передам человеку от которого ты получил ссылку😉")
        a = 0
        for i in letterId:
            if i[0] == message.from_user.id:
                letterId.pop(a)
            a += 1
        letterId.append([message.from_user.id, value[2]])
        await state.set_state(letter.letter.state)

    else: 
        builder = InlineKeyboardBuilder()
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
            sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
            value = sql.fetchone()
            value = list(value)
            date = json.loads(value[3])
            date.append(i[1])
            db.commit()
            sql.execute(f"UPDATE users SET idLetters = ? WHERE id = ?", (json.dumps(date), value[2]))
            db.commit()
            if message.photo:
                photo = message.photo[-1].file_id
                await bot.send_photo(i[1], photo=photo, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты!")
            if message.text:
                await bot.send_message(i[1], f"Хохохо🎅 Это новое пожелание от Тайного Санты!\n{message.text}")
            await message.answer("Прекрасно! уже отправил поздравление!📧")
            await state.clear()
            return
        a += 1


@dp.message(Command("music"))
async def cmd_music(message: types.Message):
    value = get_user(message)
    audio = musics[random.randint(0, len(musics)-1)]
    await bot.send_audio(message.chat.id, audio)

@dp.message(Command("snow"))
async def cmd_snow(message: types.Message):
    value = get_user(message)
    time.sleep(0.2)
    city = message.text.split()[1]
    res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params={'q': f'{city}', 'type': 'like', 'units': 'metric', 'APPID': '2b845cde2521735273dfaba14ada0b8f'})
    data = res.json()
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
    value = get_user(message)
    mandarins = json.loads(value[6])
    if random.randint(0, 100) <= 90:
        karma = random.randint(0, 10) if mandarins[1] == 0 else random.randint(0, round((mandarins[1] / 100) * 50))
    else:
        karma = -random.randint(0, 10) if mandarins[1] == 0 else random.randint(0, round((mandarins[1] / 100) * 10))
    mandarins[1] += karma
    sql.execute('UPDATE users SET mandarin = ? WHERE id = ?', (json.dumps(mandarins), message.from_user.id))
    db.commit()
    with open('mandarin.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        mandarin = list(reader)
        wish = mandarin[random.randint(1, len(mandarin)-1)]
        await message.answer(f'{message.from_user.full_name} сегодня {f'собрал {karma} мандраринок и теперь их у тебя целых {mandarins[1]}! Они отлично дополнят новогодний стол!' if karma > 0 else f'не твой день... {karma} теперь у тебя всего лишь {mandarins[1]} мандаринок. В следующий раз у тебя точно получиться!'} \n\n\n {f'Судьба говорит что: {wish[0]}\n\nРедкость: {json.loads(mandarin[0][0])[str(wish[1])]}' if random.randint(0,1) == 1 else 'Судьба ничего не сказала...'}')

@dp.message(Command("topchat"))
async def cmd_topchat(message: types.Message):
    if message.chat.type == "group" or "supergroup":
        sql.execute(f"SELECT * FROM chats WHERE chat_id = ?", (message.chat.id,))
        value = sql.fetchone()
        if value != None:
            members = json.loads(value[1])
            liders = []
            for user in members:
                sql.execute('SELECT * FROM users WHERE id = ?', (user,))
                user = sql.fetchone()
                user = list(user)
                if user != None:
                    liders.append([user[0], user[3], json.loads(user[6])[1]])
            
            liders.sort(key=lambda x: x[2], reverse=True)
            lidersText = ''
            for u in range(7 if len(liders) >= 7 else len(liders)):
                lidersText += f'{u+1}. {liders[u][1]} ({liders[u][2]} мандаринок)\n'
            await message.answer(f'Лучшие мастера в мандаринах этого чата:\n\n{lidersText}')


@dp.message(Command("top"))
async def cmd_topchat(message: types.Message):
    liders = []
    for value in sql.execute("SELECT * FROM users"):
        value = list(value)
        liders.append([value[0], value[3], json.loads(value[6])[1]])
            
    liders.sort(key=lambda x: x[2], reverse=True)
    lidersText = ''
    for u in range(7 if len(liders) >= 7 else len(liders)):
        lidersText += f'{u+1}. {liders[u][1]} ({liders[u][2]} мандаринок)\n'
    await message.answer(f'Лучшие мастера в мандаринах:\n\n{lidersText}')



@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    value = get_user(message)
    builder = InlineKeyboardBuilder()
    settings = json.loads(value[5])
    builder.add(types.InlineKeyboardButton(
        text=f"{'💔Выключить' if settings[0] == True else '❤Включить'} уведомления об отчете до НГ",
        callback_data = "settings_notifications"
    ))
    builder.add(types.InlineKeyboardButton(
        text=f"{'💔Не приимать' if settings[1] == True else '❤Принимать'} сообщения от Тайного Санты",
        callback_data = "settings_santa"
    ))
    builder.add(types.InlineKeyboardButton(
        text=f"Изменить ссылку на Тайного Санту",
        callback_data = "settings_retext"
    ))
    builder.adjust(1)
    await message.answer("🎄Настройки Нового Года:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith('settings_'))
async def call_notifications(call: types.CallbackQuery):
    value = get_user(call.message)
    settings = json.loads(value[5])
    result = ''
    action = call.data.split('_')[1]
    if action == 'retext':
        token = secrets.token_urlsafe(10)
        sql.execute("UPDATE users SET tokenSanta = ? WHERE id = ?", (token, call.message.from_user.id))
        db.commit()
        result = f'❄Ссылка успешно изменнна на https://t.me/ThisIsAtlas_Bot?start={str(value[0])+token}'
    else:
        actions = {'notifications': 0, 'santa': 1}
        settings[actions[action]] = not settings[actions[action]]
        sql.execute("UPDATE users SET Settings = ? WHERE id = ?", (json.dumps(settings), call.message.from_user.id))
        db.commit()
        result = f'❄Настройки успешно сохраненны'
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text=f"{'💔Выключить' if settings[0] == True else '❤Включить'} уведомления об отчете до НГ",
        callback_data = "settings_notifications"
    ))
    builder.add(types.InlineKeyboardButton(
        text=f"{'💔Не приимать' if settings[1] == True else '❤Принимать'} сообщения от Тайного Санты",
        callback_data = "settings_santa"
    ))
    builder.add(types.InlineKeyboardButton(
        text=f"Изменить ссылку на Тайного Санту",
        callback_data = "settings_retext"
    ))
    builder.adjust(1)
    with suppress(TelegramBadRequest):
        await call.message.edit_text(f"🎄Настройки Нового Года:/\n\n{result}", reply_markup=builder.as_markup())



async def send_message_day():
    time.sleep(0.22)
    day = 365 - datetime.now().timetuple().tm_yday
    text = f"До нового года осталось🎄:\n{int(day)} дней 0 часов  0 минут 0 секунд"
    if day == 0:
        text = "С НОВЫМ ГОДОМ!🎆\nКанал автора бота: https:/t.me/AtlasForAmerica"

    for value in sql.execute("SELECT * FROM users"):
        if json.loads(list(value)[5])[0] == True:
            await bot.send_message(chat_id=value[0], text=text)



async def main():
    scheduler.add_job(send_message_day,'cron', day="*", hour=0, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

