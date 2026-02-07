# Packages and files # 

import telebot
from telebot import types
from telebot.storage import StateMemoryStorage
from telebot import custom_filters
import sqlite3
from pprint import pprint

# Variables #


## ----------- Bot -------------- ##
state_storage = StateMemoryStorage()
f = open('API.txt', 'r')
api_key = f.readline()
f.close()
bot = telebot.TeleBot(api_key, state_storage=state_storage)
bot.add_custom_filter(custom_filters.StateFilter(bot))

class States: 
    MODE = "mode"
    STUDENT_NAME = "student_name"
    FACULTY = "faculty"
    COURSE = "course"
    GROUP = "group"
    DIRECTION = "direction"
    TOPIC = "topic"
    SCORETYPE = "score_type"
    SCORE = "score"
    EXP = "experience"
    ML = "motivation_letter"
    SKILLS = "skills"
    CONTACT = "contact"
    AuthSU = "superuser_auth"
    SU = "superuser"
    DESCEXP = "describe_exp"

## ----------- Txt -------------- ##

f1 = open('./text_data/messages.txt', 'r')
f2 = open('./text_data/faculties.txt', 'r')
f3 = open('./text_data/directions.txt', 'r')
f4 = open('./text_data/password.txt', 'r')

bot_messages = f1.readlines()
facs = f2.readlines()
dirs = f3.readlines()
correct_pswd = f4.readline().strip()

f1.close()
f2.close()
f3.close()
f4.close()

## ---------- Helpers ----------- ##

hide_markup = types.ReplyKeyboardRemove()


#Ensures that the user with give id exists 
def ensure_user_exists(user_id):
    con = sqlite3.connect('resumes.sql')
    cur = con.cursor()
    cur.execute('INSERT OR IGNORE INTO users (id) VALUES (?)', (user_id,))
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
    cur.execute(f'SELECT {field} FROM users WHERE id = ?', (user_id,))
    result = cur.fetchone()
    con.close()
    return result[0] if result and result[0] is not None else None


#------------------------- Bot Functions --------------------------# 
@bot.message_handler(commands=['start'])
def start(message):

    bot.delete_state(message.from_user.id, message.chat.id)

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
                avgScore TEXT, 
                direction TEXT, 
                topic TEXT, 
                experience TEXT, 
                MotivationLetter TEXT, 
                skills TEXT, 
                contact TEXT)''')

    con.commit()
    cur.close()

    # Initial message 
    bot.send_message(message.chat.id, bot_messages[0] + '\n' + bot_messages[25])
    

    start_message(message)


def start_message(message):

    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('Председатель СНО')
    btn2 = types.KeyboardButton('Студент')
    markup.row(btn1, btn2)

    bot.send_message(message.chat.id, bot_messages[1], reply_markup=markup)

    bot.set_state(message.from_user.id, States.MODE, message.chat.id)

@bot.message_handler(state=States.MODE)
def mode(message):
    
    if message.text == 'Председатель СНО':
        bot.send_message(message.chat.id, bot_messages[23], reply_markup=hide_markup)
        bot.set_state(message.from_user.id, States.SU, message.chat.id)
    elif message.text == 'Студент':
        bot.send_message(message.chat.id, bot_messages[3], reply_markup=hide_markup)
        bot.set_state(message.from_user.id, States.STUDENT_NAME, message.chat.id)
    else:
        bot.send_message(message.chat.id, bot_messages[2])


################### Student Part ######################

@bot.message_handler(state=States.STUDENT_NAME)
def student(message):

    ensure_user_exists(message.from_user.id)

    fullname = message.text
    update_user_field(message.from_user.id, 'fullname', fullname)
    markup = types.ReplyKeyboardMarkup()
    for fac in facs:
        markup.add(types.KeyboardButton(fac))

    bot.send_message(message.chat.id, bot_messages[5], reply_markup=markup)
    bot.set_state(message.from_user.id, States.FACULTY, message.chat.id)

@bot.message_handler(state=States.FACULTY)
def Faculty(message): 
    faculty = message.text
    valid_facs = [f.strip() for f in facs]

    if (faculty in valid_facs):
        bot.send_message(message.chat.id, bot_messages[7], reply_markup=hide_markup)
        update_user_field(message.from_user.id, 'faculty', faculty)
        bot.set_state(message.from_user.id, States.COURSE, message.chat.id)
    else:
        bot.send_message(message.chat.id, bot_messages[6])

@bot.message_handler(state=States.COURSE)
def Course(message):
    
    tmp = message.text
    try:
        courseNum = int(tmp)
        if courseNum > 5 or courseNum < 1: raise ValueError("invalid course number")
        bot.send_message(message.chat.id, bot_messages[9])
        update_user_field(message.from_user.id, 'courseNumber', courseNum)
        bot.set_state(message.from_user.id, States.GROUP, message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, bot_messages[8])


@bot.message_handler(state=States.GROUP)
def Group(message):
    group = message.text
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton(bot_messages[11])
    btn2 = types.KeyboardButton(bot_messages[12])
    markup.row(btn1, btn2)

    bot.send_message(message.chat.id, bot_messages[10], reply_markup=markup)
    update_user_field(message.from_user.id, '"group"', group)
    bot.set_state(message.from_user.id, States.SCORETYPE, message.chat.id)


@bot.message_handler(state=States.SCORETYPE)
def ScoreType(message):
    type = message.text.strip()
    if (type == bot_messages[11].strip()):
        '''code'''
        bot.send_message(message.chat.id, bot_messages[13], reply_markup=hide_markup)
        update_user_field(message.from_user.id, 'ScoreType', 1)
        bot.set_state(message.from_user.id, States.SCORE, message.chat.id)
    elif (type == bot_messages[12].strip()):
        '''code'''
        bot.send_message(message.chat.id, bot_messages[13], reply_markup=hide_markup)
        update_user_field(message.from_user.id, 'ScoreType', 0)
        bot.set_state(message.from_user.id, States.SCORE, message.chat.id)
    else:
        bot.send_message(message.chat,id, bot_messages[6])
        bot.send_message(message.chat.id, bot_messages[10])

    
@bot.message_handler(state=States.SCORE)
def Score(message):
    score = message.text

    markup = types.ReplyKeyboardMarkup()
    for d in dirs:
        markup.add(types.KeyboardButton(d))

    bot.send_message(message.chat.id, bot_messages[14], reply_markup=markup)
    update_user_field(message.from_user.id, 'avgScore', score)
    bot.set_state(message.from_user.id, States.DIRECTION, message.chat.id)


@bot.message_handler(state=States.DIRECTION)
def Direction(message):

    direction = message.text
    if (direction in dirs) or (direction + '\n' in dirs):

        if (direction == "Другое"):
            bot.send_message(message.chat.id, bot_messages[15], reply_markup=hide_markup)
            bot.set_state(message.from_user.id, "optional", message.chat.id)
        else:
            bot.send_message(message.chat.id, bot_messages[16], reply_markup=hide_markup)
            update_user_field(message.from_user.id, 'direction', direction)
            bot.set_state(message.from_user.id, States.TOPIC, message.chat.id)
    else: 
        bot.send_message(message.chat.id, bot_messages[6])


@bot.message_handler(state="optional")
def Optional(message):
    direction = message.text

    bot.send_message(message.chat.id, bot_messages[16])
    update_user_field(message.from_user.id, 'direction', "Другое: " + direction)
    bot.set_state(message.from_user.id, States.TOPIC, message.chat.id)



@bot.message_handler(state=States.TOPIC)
def Topic(message):
    topic = message.text

    markup = types.ReplyKeyboardMarkup()
    markup.row(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
    bot.send_message(message.chat.id, bot_messages[17], reply_markup=markup)
    update_user_field(message.from_user.id, 'topic', topic)
    bot.set_state(message.from_user.id, States.EXP, message.chat.id)
    


@bot.message_handler(state=States.EXP)
def Exp(message):
    haveExp = message.text
    if (haveExp.strip() == "Да"):
        bot.send_message(message.chat.id, bot_messages[18])
        bot.set_state(message.from_user.id, States.DESCEXP, message.chat.id)
    elif (haveExp.strip() == "Нет"):
        bot.send_message(message.chat.id, bot_messages[19], reply_markup=hide_markup)
        update_user_field(message.from_user.id, 'experience', "нет")
        bot.set_state(message.from_user.id, States.ML, message.chat.id)
    else:
        bot.send_message(message.chat.id, bot_messages[6])


@bot.message_handler(state=States.DESCEXP)
def DescExp(message):
    description = message.text
    bot.send_message(message.chat.id, bot_messages[19], markup=hide_markup)
    update_user_field(message.from_user.id, 'experience', description)
    bot.set_state(message.from_user.id, States.ML, message.chat.id)

@bot.message_handler(state=States.ML)
def MotLetter(message):
    motLetter = message.text
    bot.send_message(message.chat.id, bot_messages[20])
    update_user_field(message.from_user.id, 'MotivationLetter', motLetter)
    bot.set_state(message.from_user.id, States.SKILLS, message.chat.id)

@bot.message_handler(state=States.SKILLS)
def Skills(message):
    skills = message.text
    bot.send_message(message.chat.id, bot_messages[21])
    update_user_field(message.from_user.id, 'skills', skills)
    bot.set_state(message.from_user.id, States.CONTACT, message.chat.id)

@bot.message_handler(state=States.CONTACT)
def Contact(message):
    contact = message.text
    update_user_field(message.from_user.id, 'contact', contact)
    bot.set_state(message.from_user.id, "EndState", message.chat.id)
    bot.send_message(message.chat.id, bot_messages[22])

@bot.message_handler(state="EndState")
def end(message):
    bot.send_message(message.chat.id, bot_messages[26])


################### Superuser Part #######################################################################

@bot.message_handler(state=States.AuthSU)
def superuser_auth(message):
    pswd = message.text.strip()
    if pswd == correct_pswd:
        # Состояние остаётся SU — мы уже в режиме суперпользователя
        bot.send_message(message.chat.id, "✅ Авторизация прошла успешно!")

    else:
        bot.send_message(message.chat.id, bot_messages[24])
        bot.delete_state(message.from_user.id, message.chat.id)
        start_message(message)  # Возврат к выбору роли

@bot.message_handler(state=States.SU)
def superuser(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Получить все анкеты", callback_data='get_all_data'))
    markup.add(types.InlineKeyboardButton("👤 Поиск по факультету", callback_data='search_by_name'))
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def superuser_callback(callback):
    bot.answer_callback_query(callback.id)  # Убираем "часики" в интерфейсе
    
    if callback.data == 'get_all_data':
        receive_all_data(callback.message)
    elif callback.data == 'search_by_name':
        markup = types.ReplyKeyboardMarkup()
        for fac in facs:
            markup.add(types.KeyboardButton(fac))

        bot.send_message(callback.message.chat.id, "Введите факультет для поиска:", reply_markup=markup)
        bot.register_next_step_handler(callback.message, search_by_name)

    elif callback.data == 'export_csv':
        export_to_csv(callback)


def receive_all_data(message):
    """Получает все анкеты из БД и отправляет их суперпользователю"""
    try:
        with sqlite3.connect('resumes.sql') as con:
            cur = con.cursor()
            # Получаем всех пользователей с заполненными анкетами (проверяем наличие ФИО)
            cur.execute('''
                SELECT id, fullname, faculty, courseNumber, "group", 
                       ScoreType, avgScore, direction, topic, 
                       experience, MotivationLetter, skills, contact
                FROM users 
                WHERE fullname IS NOT NULL AND fullname != ''
                ORDER BY id DESC
            ''')
            users = cur.fetchall()
        
        if not users:
            bot.send_message(message.chat.id, "📭 Нет заполненных анкет в базе данных.")
            superuser(message)
            return
        
        # Формируем сообщение со всеми анкетами
        total = len(users)
        response = f"📋 Найдено {total} анкет:\n\n"
        
        for idx, user in enumerate(users, 1):
            user_id, fullname, faculty, course, group_num, score_type, avg_score, \
            direction, topic, experience, ml, skills, contact = user
            
            # Форматируем тип оценки
            score_type_str = "Баллы ЕГЭ" if score_type == 1 else "Оценка за 2 семестра" if score_type == 0 else "Не указано"
            
            # Форматируем опыт
            exp_str = experience if experience and experience.lower() != "нет" else "❌ Нет опыта"
            
            # Формируем карточку пользователя
            user_card = ( 
                f"{'='*40}\n"
                f"№{idx}\n"
                f"👤 ФИО: {fullname}\n"
                f"🏛 Факультет: {faculty or '—'}\n"
                f"🎓 Курс: {course or '—'} | Группа: {group_num or '—'}\n"
                f"📊 Средний балл: {avg_score or '—'} ({score_type_str})\n"
                f"🧭 Направление: {direction or '—'}\n"
                f"💡 Тема: {topic or '—'}\n"
                f"💼 Опыт: {exp_str}\n"
                f"📝 Навыки: {skills or '—'}\n"
                f"📱 Контакт: {contact or '—'}\n"
                f"{'='*40}\n\n"
            )
            
            # Добавляем мотивационное письмо отдельным сообщением (если длинное)
            if ml and len(ml) > 1000:
                user_card += f"✉️ Мотивационное письмо (первые 100 символов):\n{ml[:100]}...\n\n"
            elif ml:
                user_card += f"✉️ Мотивационное письмо:\n{ml}\n\n"
            
            # Проверяем длину сообщения (лимит Telegram ~4096 символов)
            if len(response) + len(user_card) > 4000:
                bot.send_message(message.chat.id, response, parse_mode='HTML')
                response = user_card
            else:
                response += user_card
        
        # Отправляем остаток
        if response.strip():
            bot.send_message(message.chat.id, response, parse_mode='HTML')
        
        # Добавляем кнопку для экспорта
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Экспортировать в CSV", callback_data='export_csv'))
        bot.send_message(message.chat.id, f"✅ Всего анкет: {total}", reply_markup=markup)
        superuser(message)
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка при получении данных: {str(e)}")
        print(f"DB Error: {e}")


def search_by_name(message):
    """Поиск пользователя по ФИО"""
    search_term = message.text.strip()
    
    try:
        with sqlite3.connect('resumes.sql') as con:
            cur = con.cursor()
            cur.execute('''
                SELECT id, fullname, faculty, courseNumber, "group", 
                       ScoreType, avgScore, direction, topic, 
                       experience, MotivationLetter, skills, contact
                FROM users 
                WHERE (faculty) LIKE ?
            ''', (f'%{search_term}%',))
            users = cur.fetchall()
        
        if not users:
            bot.send_message(message.chat.id, f"🔍 Не найдено анкет по запросу '{search_term}'")
            superuser(message)
            return
        
        response = f"🔍 Найдено {len(users)} анкет по запросу '{search_term}':\n\n"
        for user in users:
            user_id, fullname, faculty, course, group_num, score_type, avg_score, \
            direction, topic, experience, ml, skills, contact = user
            
            score_type_str = "Баллы" if score_type == 1 else "Оценка" if score_type == 0 else "—"
            exp_str = experience if experience and experience.lower() != "нет" else "❌ Нет опыта"
            
            user_card = (
                f"🆔 ID: {user_id}\n"
                f"👤 ФИО: {fullname}\n"
                f"🏛 Факультет: {faculty or '—'}\n"
                f"🎓 Курс: {course or '—'} | Группа: {group_num or '—'}\n"
                f"📊 Средний балл: {avg_score or '—'} ({score_type_str})\n"
                f"🧭 Направление: {direction or '—'}\n"
                f"💡 Тема: {topic or '—'}\n"
                f"💼 Опыт: {exp_str}\n"
                f"📝 Навыки: {skills or '—'}\n"
                f"📱 Контакт: {contact or '—'}\n"
                f"{'─'*30}\n\n"
            )

            if ml and len(ml) > 1000:
                user_card += f"✉️ Мотивационное письмо (первые 100 символов):\n{ml[:100]}...\n\n"
            elif ml:
                user_card += f"✉️ Мотивационное письмо:\n{ml}\n\n"
            
            if len(response) + len(user_card) > 4000:
                bot.send_message(message.chat.id, response)
                response = user_card
            else:
                response += user_card
        
        if response.strip():
            bot.send_message(message.chat.id, response)

        superuser(message)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка поиска: {str(e)}")


def export_to_csv(callback):
    """Экспорт данных в CSV с поддержкой кириллицы для Excel"""
    try:
        import csv
        from io import BytesIO
        
        # Получаем данные из БД
        with sqlite3.connect('resumes.sql') as con:
            cur = con.cursor()
            cur.execute('''
                SELECT id, fullname, faculty, courseNumber, "group", 
                       ScoreType, avgScore, direction, topic, 
                       experience, MotivationLetter, skills, contact
                FROM users 
                WHERE fullname IS NOT NULL AND fullname != ''
                ORDER BY id DESC
            ''')
            users = cur.fetchall()
        
        if not users:
            bot.send_message(callback.message.chat.id, "📭 Нет данных для экспорта")
            bot.answer_callback_query(callback.id)
            superuser(callback.message)
            return
        
        # Создаём CSV в памяти с правильной кодировкой для кириллицы (UTF-8-SIG)
        import io
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)  # ; для русского Excel
        
        # Заголовки
        writer.writerow([
            'ID', 'ФИО', 'Факультет', 'Курс', 'Группа', 
            'Тип_оценки', 'Средний_балл', 'Направление', 'Тема',
            'Опыт', 'Мотивационное_письмо', 'Навыки', 'Контакт'
        ])
        
        # Данные
        for user in users:
            score_type_str = 'Баллы ЕГЭ' if user[5] == 1 else 'Оценка за 2 семестра' if user[5] == 0 else '—'
            writer.writerow([
                user[0],  # id
                user[1],  # fullname
                user[2],  # faculty
                user[3],  # courseNumber
                user[4],  # group
                score_type_str,  # ScoreType как текст
                user[6],  # avgScore
                user[7],  # direction
                user[8],  # topic
                user[9],  # experience
                user[10], # MotivationLetter
                user[11], # skills
                user[12]  # contact
            ])
        
        # КРИТИЧЕСКИ ВАЖНО: конвертируем в байты с кодировкой для Excel (UTF-8-SIG)
        csv_bytes = output.getvalue().encode('utf-8-sig')
        
        # Создаём файловый объект для отправки
        bio = BytesIO(csv_bytes)
        bio.name = 'resumes.csv'  # Имя файла для Telegram
        
        # Отправляем документ
        bot.send_document(
            callback.message.chat.id,
            document=bio,
            caption=f"✅ Экспортировано {len(users)} анкет\n\n💡 Откройте в Excel: Данные → Из текста/CSV → Кодировка UTF-8"
        )
        bot.answer_callback_query(callback.id, "✅ Файл успешно отправлен!")
        superuser(callback.message)
        
    except Exception as e:
        bot.send_message(callback.message.chat.id, f"❌ Ошибка экспорта: {str(e)}")
        bot.answer_callback_query(callback.id, "❌ Ошибка при экспорте", show_alert=True)
        import traceback
        print("Export error traceback:")
        traceback.print_exc()

bot.polling(none_stop=True)