#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
from telebot import types
from collections import defaultdict
import datetime as dt
import json
from pathlib import Path
import pickle
import requests
import toml
import sys
import asyncio
import datetime
from urllib.error import HTTPError
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Константы
bot = telebot.TeleBot("1663223257:AAEUtGJ4JXyuyz9k3YG5WJeCdum9iZbgoSg")
SUBJECTS = {
    113703: "Английский язык",
    113704: "Немецкий язык",
}
SESSION_PATH = "dnevnik.session.pkl"
HEADERS_PATH = "headers.json"
config = {
    'urls':
        {
            'marks_for_period': 
                {
                    'url': 'https://dnevnik2.petersburgedu.ru/api/journal/estimate/table', 
                    'params': 
                        {
                            'p_educations[]': 0, 
                            'p_date_from': '1.03.2021', 
                            'p_date_to': '30.05.2021', 
                            'p_limit': 200, 
                            'p_page': 1
                        }
                }
        }
}
headers = [
            {
              "name": "Cookie",
              "value": "X-JWT-Token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VySWQiOiI1YzVkMDAwMjhhY2I1MDc4MDY2YjRmNWQiLCJsYXN0QWN0aXZpdHkiOjE2MTU2Mjk5NTEsInR5cGUiOiJlbWFpbCIsImxhc3RJZCI6bnVsbH0.-SFLIA3h3hUMy4tqC7uCcbzqYIh-B5LMIbVdAEPK7mQ; _ga=GA1.2.1294280872.1615051155; _gat=1; _gid=GA1.2.1787608313.1615558039; __utma=263703443.1294280872.1615051155.1615558024.1615629943.3; __utmb=263703443.1.10.1615629943; __utmc=263703443; __utmt=1; __utmz=263703443.1615629943.3.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); _ym_visorc=b; _ym_isad=2; _ym_d=1615051155; _ym_uid=1615051155649273694"
            },
            {
              "name": "Accept",
              "value": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            {
              "name": "Accept-Encoding",
              "value": "gzip, deflate, br"
            },
            {
              "name": "Host",
              "value": "dnevnik2.petersburgedu.ru"
            },
            {
              "name": "User-Agent",
              "value": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"
            },
            {
              "name": "Accept-Language",
              "value": "ru"
            },
            {
              "name": "Referer",
              "value": "https://petersburgedu.ru/"
            },
            {
              "name": "Connection",
              "value": "keep-alive"
            }
]
# Use a service account
cred = credentials.Certificate("firebase-sdk.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

users_ref = db.collection(u'users')

# Enables redemption mode
@bot.message_handler(commands=["admin"])
def admin_command(message):
    if message.chat.id == 288076865:
        users = users_ref.where(u'tele', u'==', message.chat.username).stream()
        user = False
        for user in users:
            user = True

        msg = "Kindly enter your code"
        if user:
            msg = "You have already redeemed for this event!"
        else:
            global redeeming
            redeeming = True
        bot.send_message(message.chat.id,msg)

# handle commands, /start
@bot.message_handler(commands=["start"])
def handle_command(message):
    # addNewUser(message.from_user.username, message.from_user.id)
    bot.send_message(288076865, "Челик стартанул бота!\n Username: " + str(message.from_user.username) + " ID: " + str(message.from_user.id))
    bot.send_message(message.chat.id, "Здравствуйте! У вас есть ID?", reply_markup=keyboard1())
    
@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Есть":
        msg = bot.send_message(message.chat.id, "Укажите ваше ID")
        bot.register_next_step_handler(msg, makeID)
    elif message.text == "Нету":
        bot.send_message(message.chat.id, "<a href='https://github.com/newtover/dnevnik'>Вот инструкция</a> по получению ID", parse_mode="HTML", reply_markup=keyboard3())
    elif message.text == "Оценки за Сегодня":
        # Создаем сегодняшнюю и неделю назад
        cur = datetime.datetime.now()
        ago = datetime.timedelta(days = 1)
        day = cur + ago

        # Обрабатывем эти даты
        cur = str(cur.strftime("%x"))
        day_n = cur[3] + cur[4]
        month_n = cur[0] + cur[1]
        year_n = "20" + cur[6] + cur[7]
        cur = day_n + "." + month_n + "." + year_n

        day = str(day.strftime("%x"))
        day_d = day[3] + day[4]
        month_d = day[0] + day[1]
        year_d = "20" + day[6] + day[7]
        day = day_d + "." + month_d + "." + year_d

        # Отправляем
        try:
            text = asyncio.run(showMarks(cur, day))
        except:
            text = "В настоящее время на портале «Петербургское образование» ведутся технические работы. В ближайшее время портал возобновит свою работу. Приносим свои извинения за доставленные неудобства."
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    elif message.text == "Оценки за Неделю":
        # Создаем сегодняшнюю и неделю назад
        cur = datetime.datetime.now()
        ago = datetime.timedelta(days = 7)
        week = cur - ago

        # Обрабатывем эти даты
        cur = str(cur.strftime("%x"))
        day_n = cur[3] + cur[4]
        month_n = cur[0] + cur[1]
        year_n = "20" + cur[6] + cur[7]
        cur = day_n + "." + month_n + "." + year_n

        week = str(week.strftime("%x"))
        day_w = week[3] + week[4]
        month_w = week[0] + week[1]
        year_w = "20" + week[6] + week[7]
        week = day_w + "." + month_w + "." + year_w

        # Отправляем
        try:
            text = asyncio.run(showMarks(week, cur))
        except:
            text = "В настоящее время на портале «Петербургское образование» ведутся технические работы. В ближайшее время портал возобновит свою работу. Приносим свои извинения за доставленные неудобства."
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    elif message.text == "Оценки за Месяц":
        # Создаем сегодняшнюю и неделю назад
        cur = datetime.datetime.now()
        ago = datetime.timedelta(days = 30)
        month = cur - ago

        # Обрабатывем эти даты
        cur = str(cur.strftime("%x"))
        day_n = cur[3] + cur[4]
        month_n = cur[0] + cur[1]
        year_n = "20" + cur[6] + cur[7]
        cur = day_n + "." + month_n + "." + year_n

        month = str(month.strftime("%x"))
        day_m = month[3] + month[4]
        month_m = month[0] + month[1]
        year_m = "20" + month[6] + month[7]
        month = day_m + "." + month_m + "." + year_m

        # Отправляем
        try:
            text = asyncio.run(showMarks(month, cur))
        except:
            text = "В настоящее время на портале «Петербургское образование» ведутся технические работы. В ближайшее время портал возобновит свою работу. Приносим свои извинения за доставленные неудобства."
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    elif message.text == "Мой Средний Балл":
        try:
            text = asyncio.run(showAverage())
        except:
            text = "В настоящее время на портале «Петербургское образование» ведутся технические работы. В ближайшее время портал возобновит свою работу. Приносим свои извинения за доставленные неудобства."
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    elif message.text == "Получилось":
        msg = bot.send_message(message.chat.id, "Укажите ваше ID")
        bot.register_next_step_handler(msg, makeID)
    elif message.text == "Не получилось":
        msg = bot.send_message(message.chat.id, "Напишите админу - @romanrakhlin. Он вам поможет разобраться.")
        bot.register_next_step_handler(msg, makeID)
    else:
        bot.send_message(message.chat.id, "Такой команды нет")

# Функция обработки ID
def makeID(message):
    chat_id = message.chat.id
    text = message.text
    if not text.isdigit():
        msg = bot.send_message(chat_id, "ID должно быть числом")
        bot.register_next_step_handler(msg, makeID) #askSource
        return
    config['urls']['marks_for_period']['params']["p_educations[]"] = int(message.text)
    bot.send_message(288076865, "Челик привязал дневник!\n Username: " + str(message.from_user.username) + " ID: " + str(message.from_user.id))
    msg = bot.send_message(chat_id, "Спасибо! Ваш дневник успешно связан с ботом!", reply_markup=keyboard2())

# Клавы
def keyboard1():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_1 = types.KeyboardButton("Есть")
    button_2 = types.KeyboardButton("Нету")
    markup.add(button_1)
    markup.add(button_2)
    return markup

def keyboard2():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_1 = types.KeyboardButton("Оценки за Сегодня")
    button_2 = types.KeyboardButton("Оценки за Неделю")
    button_3 = types.KeyboardButton("Оценки за Месяц")
    button_4 = types.KeyboardButton("Мой Средний Балл")
    markup.add(button_1)
    markup.add(button_2)
    markup.add(button_3)
    markup.add(button_4)
    return markup

def keyboard3():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_1 = types.KeyboardButton("Получилось")
    button_2 = types.KeyboardButton("Не получилось")
    markup.add(button_1)
    markup.add(button_2)
    return markup

# Фунция получения предметов
def get_subject(item):
    return SUBJECTS.get(item['subject_id'], item['subject_name'])

# Функция получения дат
def to_date(text):
    return dt.datetime.strptime(text, '%d.%m.%Y').date()

# Функция вывода оценок
async def showMarks(from_date, till_date):
    result = "<u>Вот твои оценки</u>\n"

    config['urls']['marks_for_period']['params']["p_date_from"] = from_date
    config['urls']['marks_for_period']['params']["p_date_to"] = till_date

    session = requests.Session()
    for header in headers:
        session.headers[header['name']] = header['value']

    url = config['urls']['marks_for_period']['url']
    params = config['urls']['marks_for_period']['params']

    with session.get(url, params=params) as res:
        res.raise_for_status()
        text = res.text
        data = res.json()

    out_lines = []
    grouped = defaultdict(list)
    for item in sorted(data['data']['items'], key=lambda x: (to_date(x['date']), x['estimate_value_name'])):
        s_name = item['subject_name'] = get_subject(item)
        mark = item['estimate_value_name']
        if mark.isdigit():
            grouped[s_name].append(int(mark))
        comment = ('# ' + item['estimate_comment']) if item['estimate_comment'] else ''
        out_lines.append(("*{subject_name}* - {estimate_value_code}".format(**item), comment))

    if not out_lines:
        return "Извините, к сожаленю у вас нет оценок за сегодня"

    arr = []
    for s_name in sorted(grouped):
        s_marks = ' '.join(str(mark) for mark in grouped[s_name])
        arr.append("<strong>" + str(s_name) + "</strong>" + " - " + "<em>" + str(s_marks) + "</em>")

    for i in arr:
        if i not in result:
            result += str(i) + "\n"

    return result

# Функция вывода среднего балла
async def showAverage():
    result = "<u>Вот твой средний балл</u>\n"

    config['urls']['marks_for_period']['params']["p_date_from"] = "01.01.2021"
    config['urls']['marks_for_period']['params']["p_date_to"] = "30.05.2021"

    session = requests.Session()
    for header in headers:
        session.headers[header['name']] = header['value']

    url = config['urls']['marks_for_period']['url']
    params = config['urls']['marks_for_period']['params']

    with session.get(url, params=params) as res:
        res.raise_for_status()
        text = res.text
        data = res.json()

    out_lines = []
    grouped = defaultdict(list)
    for item in sorted(data['data']['items'], key=lambda x: (to_date(x['date']), x['estimate_value_name'])):
        s_name = item['subject_name'] = get_subject(item)
        mark = item['estimate_value_name']
        if mark.isdigit():
            grouped[s_name].append(int(mark))
        comment = ('# ' + item['estimate_comment']) if item['estimate_comment'] else ''
        out_lines.append((
            to_date(item['date']),
            "{subject_name:25s} {estimate_value_code:5s} {estimate_value_name:9s} {estimate_type_name:20s}".format(**item),
            comment
        ))

    if not out_lines:
        exit(1)

    arr = []
    
    for s_name in sorted(grouped):
        avg = round(sum(grouped[s_name]) / len(grouped[s_name]), 1)
        arr.append("<strong>" + str(s_name) + "</strong>" + " - " + "<em>" + str(avg) + "</em>")
    
    for i in arr:
        if i not in result:
            result += i + "\n"

    return result

# Функция для записи юзера в txt файл
# def addNewUser(user, uid):
#     file = open("users.txt", "w") # Открываем файл для записи
#     file.write("User: {}, id: {}\n".format(user, uid)) # Записываем
#     file.close() # Закрываем файл

bot.polling()