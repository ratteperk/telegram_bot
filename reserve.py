# Packages and files # 

import telebot
from telebot import types
import sqlite3
from pprint import pprint

# Variables #


## ----------- Bot -------------- ##
api_key = open('API.txt', 'r').readline()
bot = telebot.TeleBot(api_key)

## ----------- Txt -------------- ##
bot_messages = open('./text_data/messages.txt', 'r').readlines()
facs = open('./text_data/faculties.txt', 'r').readlines()
dirs = open('./text_data/directions.txt', 'r').readlines()

## ---------- Helpers ----------- ##

hide_markup = types.ReplyKeyboardRemove()

def message_handler_fix(message):
    if message.text and (message.text.startswith('/')):
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.process_new_messages([message])
        return True
    
    return False

#Ensures that the user with give id exists 
def ensure_user_exists(user_id):
    con = sqlite3.connect('resumes.sql')
    cur = con.cursor()
    cur.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id))
    con.commit()
    con.close()

#Updates one field 
def update_user_field(user_id, field, value):
    con = sqlite3.connect('resumes.sql')
    cur = con.cursor()
    cur.execute(f'UPDATE users SET {field} = ? WHERE id = ?', (value, user_id))
    con.commit()
    con.close()

def get_user_field(user_id, field):
    con = sqlite3.connect('resumes.sql')
    cur = con.cursor()
    cur.execute(f'SELECT {field} = ? FROM users WHERE id = ?', (user_id,))
    result = cur.fetchone()
    con.close()
    return result[0] if result and result[0] is not None else None


#------------------------- Bot Functions --------------------------# 
@bot.message_handler(commands=['start'])
def start(message):

    bot.clear_step_handler_by_chat_id(message.chat.id)

    # DB creation
    con = sqlite3.connect('resumes.sql')
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                fullname TEXT,
                faculty TEXT, 
                courseNumber INTEGER, 
                "group" TEXT, 
                ScoreType INTEGER, 
                avgScore REAL, 
                direction TEXT, 
                topic TEXT, 
                experience TEXT, 
                MotivationLetter TEXT, 
                skills TEXT, 
                contact TEXT)''')

    con.commit()
    cur.close()

    # Initial message 
    bot.send_message(message.chat.id, bot_messages[0])

    start_message(message)


def start_message(message):

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Председатель СНО')
    btn2 = types.KeyboardButton('Студент')
    markup.row(btn1, btn2)

    bot.send_message(message.chat.id, bot_messages[1], reply_markup=markup)

    bot.register_next_step_handler(message, mode)


def mode(message):
    if message_handler_fix(message):
        return
    

    if message.text == 'Председатель СНО':
        bot.send_message(message.chat.id, bot_messages[-1], reply_markup=hide_markup)
        bot.register_next_step_handler(message, superuser)
    elif message.text == 'Студент':
        bot.send_message(message.chat.id, bot_messages[3], reply_markup=hide_markup)
        bot.register_next_step_handler(message, student)
    else:
         bot.send_message(message.chat.id, bot_messages[2])
         bot.register_next_step_handler(message, mode)


################### Student Part ######################
def student(message):
    if message_handler_fix(message):
        return

    ensure_user_exists(message.from_user.id)

    fullname = message.text
    markup = types.ReplyKeyboardMarkup()
    for fac in facs:
        markup.add(types.KeyboardButton(fac))

    bot.send_message(message.chat.id, bot_messages[5], reply_markup=markup)
    bot.register_next_step_handler(message, Faculty)


def Faculty(message): 
    print(name)
    if message_handler_fix(message):
        return
    
    faculty = message.text
    if (faculty in facs) or (faculty + '\n' in facs):
        bot.send_message(message.chat.id, bot_messages[7], reply_markup=hide_markup)
        bot.register_next_step_handler(message, Course)
    else:
        bot.send_message(message.chat.id, bot_messages[6])
        bot.register_next_step_handler(message, Faculty)


def Course(message):
    print(name)
    if message_handler_fix(message):
        return
    
    tmp = message.text
    try:
        courseNum = int(tmp)
        if courseNum > 5 or courseNum < 1: raise ValueError("invalid course number")
        bot.send_message(message.chat.id, bot_messages[9])
        bot.register_next_step_handler(message, Group)
    except ValueError:
        bot.send_message(message.chat.id, bot_messages[8])
        bot.register_next_step_handler(message, Course)


def Group(message):
    if message_handler_fix(message):
        return

    group = message.text
    markup = types.ReplyKeyboardMarkup()
    for d in dirs:
        markup.add(types.KeyboardButton(d))

    bot.send_message(message.chat.id, bot_messages[11], reply_markup=markup)
    bot.register_next_step_handler(message, Direction)

def Direction(message):
    if message_handler_fix(message):
        return

    direction = message.text
    if (direction in dirs) or (direction + '\n' in dirs):
        bot.send_message(message.chat.id, "o kurwa")
        bot.register_next_step_handler(message, Topic)
    else: 
        bot.send_message(message.chat.id, "o double kurwa")
        bot.register_next_step_handler(message, Direction)

def Topic(message):
    if message_handler_fix(message):
        return

    topic = message.text
    pass

################### Superuser Part ####################
def superuser(message):
    if message_handler_fix(message):
        return



bot.polling(none_stop=True)