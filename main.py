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
from datetime import datetime, timedelta, time
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
import psutil

with open('settings.json', 'r') as file: #Load Settings File
    settingsDat = json.load(file)

logging.basicConfig(level=logging.INFO)


bot = Bot(token=settingsDat["tokenBot"])
admin_id = settingsDat["idAdmin"]
db = sqlite3.connect('user.db', check_same_thread = False)
dp = Dispatcher()
sql = db.cursor() 
scheduler = AsyncIOScheduler()
letterId = {}
musicFolder = os.listdir('assets/music')
musics = [FSInputFile(f'assets/music/{music}') for music in musicFolder]

photoFolder = os.listdir('assets/photo')
photos = [FSInputFile(f'assets/photo/{photo}') for photo in photoFolder]



class states(StatesGroup):
    letter = State()
    retime = State()

def get_user(message): #Function for get user get_user(his message)
    sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    if sql.fetchone() is None:
        sql.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (None, secrets.token_urlsafe(10), message.from_user.id, message.from_user.full_name, json.dumps([]), json.dumps([True, True, 'Europe/Kyiv']), json.dumps([0, 0])))
        db.commit()
    sql.execute(f"SELECT * FROM users WHERE id = ?", (message.from_user.id,))
    value = sql.fetchone()
    value = list(value)
    if message.chat.type in ["group", "supergroup"]:
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


def settings_button(value): #Generate buttons for settings
    settings = json.loads(value[5])
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
    builder.add(types.InlineKeyboardButton(
        text=f"Изменить часовой пояс",
        callback_data = "settings_retime"
    ))
    builder.adjust(1)
    return builder.as_markup()


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    value = get_user(message)
    if " " in message.text:
        code = message.text.split()[1]
        date = json.loads(value[4])
        token = code.split('i')[1]
        id = code.split('i')[0]
        sql.execute(f"SELECT * FROM users WHERE idSanta = ?", (id,))
        value = sql.fetchone()
        value = list(value) if value != None else None
        if value == None or value[1] != token:
            await message.answer("Ооу🤨 Кажеться такого пользователя не существует или ссылка не действительна")
            return
        if value[2] in date:
            await message.answer("Ооу🤨 Кажеться ты уже отправлял пожелания этому пользователю😶")
            return
        if json.loads(value[5])[1] == False:
            await message.answer("Ооу🤨 Кажеться этот пользователь закрыл эту ссылку...")
            return
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data = "close_letter"
        ))
        await message.answer(f"Напиши мне свое пожелание которые ты хотел бы пожелать и я секретно передам человеку от которого ты получил ссылку😉\n\n🎄Поддерживаються: обычные сообщеия, фото, видео, файлы, аудио, кружки, голосовые (важно что нельзя отправлять больше одного фото или видео в сообщении)", reply_markup=builder.as_markup())
        letterId[message.from_user.id] = value[2]
        await state.set_state(states.letter.state)

    else: 
        builder = InlineKeyboardBuilder()

        desired_timezone = pytz.timezone(json.loads(value[5])[2])
        now_utc = datetime.now(pytz.utc)
        dateCristmas = now_utc.astimezone(desired_timezone)
        year = dateCristmas.timetuple().tm_year
        day = 366 if year % 400 == 0 else 365 - dateCristmas.timetuple().tm_yday
        hour = 23 - dateCristmas.hour
        minute = 59 - dateCristmas.minute
        second = 60 - dateCristmas.second
        code = f'{str(value[0])}i{value[1]}'
        myBot = await bot.get_me()
        await bot.send_photo(message.chat.id, photo=photos[random.randint(0, len(photos)-1)], caption=f"До нового года осталось🎄:\n{day} дней {hour} часов  {minute} минут {second} секунд!\n\nСсылка для вашей Тайной Санты🎅: https://t.me/{myBot.username}?start={str(code)}")



@dp.message(states.letter)
async def letterMessage(message: types.Message, state: FSMContext):
    value = get_user(message)
    if message.from_user.id in letterId:
        if message.media_group_id:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(
                text="Отмена",
            callback_data = "close_letter"
            ))
            await message.answer(f"Ооу🤨 Но несколько медиа нельзя загружать\n\nПовтори еще раз только читай правила!", reply_markup=builder.as_markup())
            return
        recipient = letterId[message.from_user.id] 
        date = json.loads(value[4])
        
        if message.photo:
            file = message.photo[-1].file_id
            await bot.send_photo(recipient, photo=file, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты! {'' if message.caption is None else f'\n\n{message.caption}'}")
        elif message.video:
            file = message.video.file_id
            await bot.send_video(recipient, video=file, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты! {'' if message.caption is None else f'\n\n{message.caption}'}")
        elif message.document:
            file = message.document.file_id
            await bot.send_document(recipient, document=file, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты! {'' if message.caption is None else f'\n\n{message.caption}'}") 
        elif message.audio:
            file = message.audio.file_id
            await bot.send_audio(recipient, audio=file, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты! {'' if message.caption is None else f'\n\n{message.caption}'}") 
        elif message.voice:
            file = message.voice.file_id
            await bot.send_voice(recipient, voice=file, caption=f"Хохохо🎅 Это новое пожелание от Тайного Санты! {'' if message.caption is None else f'\n\n{message.caption}'}") 
        elif message.video_note:
            file = message.video_note.file_id
            await bot.send_video_note(recipient, video_note=file)
            await bot.send_message(recipient, f"Хохохо🎅 Это новое пожелание от Тайного Санты!") 
        elif message.text:
            await bot.send_message(recipient, f"Хохохо🎅 Это новое пожелание от Тайного Санты!\n\n{message.text}")
        await message.answer("Прекрасно! уже отправил поздравление!📧")
        date.append(recipient)
        sql.execute(f"UPDATE users SET idLetters = ? WHERE id = ?", (json.dumps(date), value[2]))
        db.commit()
    await state.clear()
           


@dp.message(Command("music"))
async def cmd_music(message: types.Message):
    value = get_user(message)
    audio = musics[random.randint(0, len(musics)-1)]
    await bot.send_audio(message.chat.id, audio=audio, caption="❄🎶Твоя новогодняя музыка уже сегодня!")

@dp.message(Command("snow"))
async def cmd_snow(message: types.Message):
    value = get_user(message)
    time.sleep(0.2)
    city = message.text.split()[1]
    res = requests.get('http://api.openweathermap.org/data/2.5/forecast', params={'q': f'{city}', 'type': 'like', 'units': 'metric', 'APPID': settingsDat["tokenWeather"]})
    data = res.json()
    if data['cod'] != '200':
        await message.answer('Ошибка! Твой город не найден!😨\nПопбробуй ввести название на англиском, а еще лучше с аббревиатурой страны❗\nНапример:\nOdesa,UA\nKyiv,UA\nOttava,CA\nAkita,JP')

    date = "00-00-00"
    day = -1
    for i in data['list']:
        if i['dt_txt'][:10] != date:
            day += 1
            if "snow" in i['weather'][0]['description']:
                await message.answer(f"Ого☃! У тебя выпадет снег через {day if day != 0 or 1 else ['сегодня', 'завтра'][day]} дней!❄")
                return
            date = i['dt_txt'][:10]
    
    await message.answer("Печально😢 У тебя пока что не наблюдаеться снег")   

@dp.message(Command("mandarin"))
async def cmd_mandrin(message: types.Message):
    value = get_user(message)
    date = datetime.now()
    mandarins = json.loads(value[6])
    if datetime.fromtimestamp(mandarins[0]) + timedelta(hours=2) >= date:
        time_free = str((datetime.fromtimestamp(mandarins[0]) + timedelta(hours=2) - date)).split(':', 2)[:4]
        await message.answer(f'🧊Тише тише... Отдохни от мандаринов\n\nПриходи через {time_free[0]} часов {time_free[1]} минут и {round(float(time_free[2]))} секунд')
        return
    if random.randint(0, 100) <= 90 or mandarins[1] <= 0:
        karma = random.randint(1, 10) if mandarins[1] <= 1 else random.randint(0, round((mandarins[1] / 100) * 50))
    else:
        karma = -random.randint(0, 10) if mandarins[1] == 0 else random.randint(0, round((mandarins[1] / 100) * 10))
    mandarins[1] += karma
    mandarins[0] = int(date.timestamp())
    sql.execute('UPDATE users SET mandarin = ? WHERE id = ?', (json.dumps(mandarins), message.from_user.id))
    db.commit()
    with open('mandarin.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        mandarin = list(reader)
        wish = mandarin[random.randint(1, len(mandarin)-1)]
        result = f'🌠Судьба говорит что: {wish[0]} \nРедкость: {json.loads(mandarin[0][0])[str(wish[1])]}' if random.randint(0,1) == 1 else '💤Судьба ничего не сказала...'
         
        await message.answer(f"""🍊{message.from_user.full_name} сегодня {f'собрал {karma} мандраринок и теперь их у тебя целых {mandarins[1]}! Они отлично дополнят новогодний стол!' if karma > 0 else f'не твой день... {karma} теперь у тебя всего лишь {mandarins[1]} мандаринок. В следующий раз у тебя точно получиться!'} 
        
        
        {result}""")

@dp.message(Command("topchat"))
async def cmd_topchat(message: types.Message):
    value = get_user(message)
    if message.chat.type in ["group", "supergroup"]:
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
            await message.answer(f'🍊Лучшие мастера в мандаринах этого чата:\n\n{lidersText}')


@dp.message(Command("top"))
async def cmd_topchat(message: types.Message):
    value = get_user(message)
    liders = [[value[0], value[3], json.loads(value[6])[1]] for value in list(sql.execute("SELECT * FROM users"))]
    liders.sort(key=lambda x: x[2], reverse=True)
    lidersText = ''
    for u in range(7 if len(liders) >= 7 else len(liders)):
        lidersText += f'{u+1}. {liders[u][1]} ({liders[u][2]} мандаринок)\n'
    await message.answer(f'🍊Лучшие мастера в мандаринах:\n\n{lidersText}')



@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    value = get_user(message)
    builder = settings_button(value)
    settings = json.loads(value[5])
    await message.answer("🎄Настройки Нового Года:", reply_markup=builder)

@dp.callback_query(F.data.startswith('settings_'))
async def call_notifications(call: types.CallbackQuery, state: FSMContext):
    value = get_user(call.message)
    settings = json.loads(value[5])
    result = ''
    action = call.data.split('_')[1]
    if action == 'retext':
        token = secrets.token_urlsafe(10)
        sql.execute("UPDATE users SET tokenSanta = ? WHERE id = ?", (token, call.message.from_user.id))
        db.commit()
        code = f'{str(value[0])}i{token}'
        myBot = await bot.get_me()
        result = f'❄Ссылка успешно изменнна на https://t.me/{myBot.username}?start={code}'
    elif action == 'retime':
        await call.message.delete()
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(
            text="Отмена",
            callback_data = "close_retime"
        ))
        await call.message.answer(f"Отправь мне свой часовой пояс в формате Part_of_the_world/City \nПримеры:\nAmerica/New_York\nEurope/Kyiv\nEurope/Moscow")
        await state.set_state(states.retime.state)
        return
    else:
        settings[{'notifications': 0, 'santa': 1}[action]] = not settings[{'notifications': 0, 'santa': 1}[action]]
        sql.execute("UPDATE users SET Settings = ? WHERE id = ?", (json.dumps(settings), call.message.from_user.id))
        db.commit()
        result = f'❄Настройки успешно сохраненны'
    builder = settings_button(value)
    with suppress(TelegramBadRequest):
        await call.message.edit_text(f"🎄Настройки Нового Года:/\n\n{result}", reply_markup=builder)

@dp.message(states.retime)
async def cmd_retime(message: types.Message, state: FSMContext):
    result = ''
    value = get_user(message)
    try:
        desired_timezone = pytz.timezone(message.text)
        value = get_user(message)
        settings = json.loads(value[5])
        settings[2] = message.text
        sql.execute("UPDATE users SET Settings = ? WHERE id = ?", (json.dumps(settings), message.from_user.id))
        db.commit()
        result = f"Часовой пояс успешно изменен на {message.text}"
    except:
        result = "Ооу🤨 Кажеться это неверный часовой пояс или ты его не правильно ввел"
    builder = settings_button(value)
    await message.answer(f"🎄Настройки Нового Года:/\n\n{result}", reply_markup=builder)
    await state.clear()
    
@dp.callback_query(F.data.startswith('close_'))
async def call_notifications(call: types.CallbackQuery, state: FSMContext): 
    value = get_user(call.message)
    action = call.data.split('_')[1]
    if action == 'retime':
        builder = settings_button(value)
        await call.message.answer(f"🎄Настройки Нового Года:/\n\nДействие отмененно", reply_markup=builder)
    if action == 'letter':
        await call.message.answer("Действие отмененно")
    await state.clear()

@dp.message(Command('monitor'))
async def cmd_monitor(message: types.Message):
    if message.from_user.id != admin_id:
        return
    if " " in message.text:
        code = message.text.split()[1]
        if code == 'get_db':
            await bot.send_document(chat_id=message.chat.id, document=FSInputFile('user.db'))
        if code == 'set_db':
            try:
                sql.execute(message.text.split('set_db', 1)[1][1:])
                result = sql.fetchone()
            except Exception as error:
                await message.answer(f"Error: {error}")
            await message.answer(str(result))
    else:
        sql.execute('SELECT COUNT(*) FROM users')
        await message.answer(text=f"Нагруженость хоста:\nЗагрузка CPU: {psutil.cpu_percent(interval=1)}%\nКоличетсво юзеров: {list(sql.fetchone())[0]}")


async def send_message_day():
    time.sleep(0.22)
    for value in sql.execute("SELECT * FROM users"):
        value = list(value)
        settings = json.loads(value[5])

        if settings[0] == True:
            desired_timezone = pytz.timezone(settings[2])
            now_utc = datetime.now(pytz.utc)
            dateCristmas = now_utc.astimezone(desired_timezone)
            year = dateCristmas.timetuple().tm_year
            day = 366 if year % 400 == 0 else 365 - dateCristmas.timetuple().tm_yday
            hour = 23 - dateCristmas.hour
            minute = 59 - dateCristmas.minute
            second = 60 - dateCristmas.second
            text = f"До нового года осталось🎄:\n{int(day)} дней {int(hour)} часов {int(minute)} минут {int(second)} секунд" if dateCristmas.timetuple().tm_yday == 1 else "С НОВЫМ ГОДОМ!🎆\nКанал автора бота: https:/t.me/AtlasForAmerica"
            await bot.send_message(chat_id=value[2], text=text)



async def main():
    
    scheduler.add_job(send_message_day,'cron', day="*", hour=0, minute=0)
    scheduler.start()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())