import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
import time
import psycopg2

bot = telebot.TeleBot('6271639185:AAF3QLrqJ7IDerIjzyu-NiajhYk5NjVhG6Q')

conn = psycopg2.connect(host='127.0.0.1', user='hse', password='hse', database='forum')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    userid BIGINT PRIMARY KEY,
    username VARCHAR,
    name VARCHAR,
    social_media VARCHAR,
    activity VARCHAR, 
    interests VARCHAR,
    dates VARCHAR,
    mailing INT,
    finished INT,
    network INT
)""")
conn.commit()


@bot.message_handler(commands=['start'])
def start(message):
    cur.execute(f'SELECT * FROM users WHERE userid={message.from_user.id}')
    info = cur.fetchone()

    if info is None:
        cur.execute(f"INSERT INTO users VALUES('{message.from_user.id}', '{message.from_user.username}',"
                    f" '{0}', '{0}', '{0}', '{0}', '{0}', {0}, {0}, {0})")
        conn.commit()

    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Нетворкинг', callback_data='network')
    btn2 = types.InlineKeyboardButton('Программа форума', callback_data='mailing')
    btn3 = types.InlineKeyboardButton('Q&A', callback_data='questions')
    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)

    bot.send_message(message.chat.id, 'Выбери интересующий раздел:\n<b>Нетворкинг</b> - поиск партнеров для общения в'
                                      ' сообществе Бизнес-клуба.\n<b>Программа форума</b> - актуальная программа форума '
                                      'со временем выступления спикеров и активностями от партнеров.\n<b>Вопросы</b>'
                                      ' - здесь ты найдёшь ответы на распространенные вопросы '
                                      'о мероприятиях.', reply_markup=kb, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'mailing')
def mailing(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

    bot.send_photo(call.message.chat.id, open('program.jpg', 'rb'))


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Нетворкинг', callback_data='network')
    btn2 = types.InlineKeyboardButton('Программа форума', callback_data='mailing')
    btn3 = types.InlineKeyboardButton('Q&A', callback_data='questions')
    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)

    bot.send_message(call.message.chat.id, 'Выбери интересующий раздел:\n<b>Нетворкинг</b> - поиск партнеров для общения в'
                                      ' сообществе Бизнес-клуба.\n<b>Программа форума</b> - актуальная программа форума '
                                           'со временем выступления спикеров и активностями от партнеров.\n<b>Вопросы</b>'
                                           ' - здесь ты найдёшь ответы на распространенные вопросы о мероприятиях.',
                                            reply_markup=kb, parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_mailing')
def cancel_mailing(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cur.execute(f"""UPDATE users SET mailing=0 WHERE userid={call.message.chat.id}""")
    conn.commit()

    bot.send_message(call.message.chat.id, 'Отписали Вас от рассылки!')


@bot.callback_query_handler(func=lambda call: call.data == 'network')
def network(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cur.execute(f'SELECT * FROM users WHERE userid={call.message.chat.id}')
    info = cur.fetchone()

    if info[8] == 1:
        sshow(call)
    else:
        bot.send_message(call.message.chat.id, '☕️ Напиши Имя и Фамилию')
        bot.register_next_step_handler(call.message, save_name_and_turn_to_social_media)


def save_name_and_turn_to_social_media(message):
    cur.execute(f"""UPDATE users SET name='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()

    bot.send_message(message.chat.id, '🤳 Пришли ссылку на свой профиль в любой соц. сети, где есть наиболее подробная'
                                      ' информация о тебе')
    bot.register_next_step_handler(message, save_social_media_and_turn_to_activity)


def save_social_media_and_turn_to_activity(message):
    cur.execute(f"""UPDATE users SET social_media='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()

    bot.send_message(message.chat.id, '👨‍🔬 Кем ты работаешь и чем занимаешься?')
    bot.register_next_step_handler(message, save_activity_and_save)


def save_activity_and_save(message):
    cur.execute(f"""UPDATE users SET activity='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()

    bot.send_message(message.chat.id, '👀 Какие у тебя есть рабочие и нерабочие интересы?\n\n💡 Напиши через запятую'
                                      ' слова, за которые можно зацепиться и развернуть из этого интересный разговор!'
                                      ' Например, увлечения, названия книг, любимый вид спорта')
    bot.register_next_step_handler(message, save)


def save(message):
    cur.execute(f"""UPDATE users SET interests='{message.text}' WHERE userid={message.chat.id}""")
    cur.execute(f"""UPDATE users SET finished=1 WHERE userid={message.chat.id}""")
    cur.execute(f"""UPDATE users SET network=1 WHERE userid={message.chat.id}""")

    conn.commit()

    bot.send_message(chat_id=message.chat.id, text="Получилось! 🙌\n\nТеперь ты можешь найти своего первого"
                                                   " собеседника!\n\nВот так будет выглядеть твой профиль в сообщении,"
                                                   " которое мы пришлем твоему собеседнику:\n⏬")
    show(message)


@bot.callback_query_handler(func=lambda call: call.data == 'show')
def sshow(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cur.execute(f'SELECT * FROM users WHERE userid={call.message.chat.id}')
    info = cur.fetchone()

    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Найти собеседника!🚀', callback_data='find')
    btn2 = types.InlineKeyboardButton('Поменять данные профиля', callback_data='change')
    btn3 = types.InlineKeyboardButton('Приостановить участие❌', callback_data='stop')
    btn4 = types.InlineKeyboardButton('<<Вернуться назад', callback_data='back')

    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)
    kb.add(btn4)

    bot.send_message(chat_id=call.message.chat.id, text=f"{info[2]}\nПрофиль: {info[3]}\n\n◽ Чем занимается:"
                                                   f" {info[4]}\n◽ Зацепки для начала разговора: {info[5]}", reply_markup=kb)


def show(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    cur.execute(f'SELECT * FROM users WHERE userid={message.chat.id}')
    info = cur.fetchone()

    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Найти собеседника!🚀', callback_data='find')
    btn2 = types.InlineKeyboardButton('Поменять данные профиля', callback_data='change')
    btn3 = types.InlineKeyboardButton('Приостановить участие❌', callback_data='stop')
    btn4 = types.InlineKeyboardButton('<<Вернуться назад', callback_data='back')

    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)
    kb.add(btn4)

    bot.send_message(chat_id=message.chat.id, text=f"{info[2]}\nПрофиль: {info[3]}\n\n◽ Чем занимается:"
                                                   f" {info[4]}\n◽ Зацепки для начала разговора: {info[5]}", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'change')
def change(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Своё имя', callback_data='name')
    btn2 = types.InlineKeyboardButton('Ссылка на соц. сеть', callback_data='social')
    btn3 = types.InlineKeyboardButton('Кем работаю', callback_data='work')
    btn4 = types.InlineKeyboardButton('О себе', callback_data='about')
    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)
    kb.add(btn4)

    bot.send_message(call.message.chat.id, 'Ок, выбери что хочешь сменить', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data in ['name', 'social', 'work', 'about'])
def change_raspr(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    if call.data == 'name':
        bot.send_message(chat_id=call.message.chat.id, text='Напиши на что хочешь заменить')
        bot.register_next_step_handler(call.message, change_name)
    elif call.data == 'social':
        bot.send_message(chat_id=call.message.chat.id, text='Напиши на что хочешь заменить')
        bot.register_next_step_handler(call.message, change_social)
    elif call.data == 'work':
        bot.send_message(chat_id=call.message.chat.id, text='Напиши на что хочешь заменить')
        bot.register_next_step_handler(call.message, change_work)
    elif call.data == 'about':
        bot.send_message(chat_id=call.message.chat.id, text='Напиши на что хочешь заменить')
        bot.register_next_step_handler(call.message, change_about)


def change_name(message):
    cur.execute(f"""UPDATE users SET name='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()
    bot.send_message(chat_id=message.chat.id, text="Данные изменены!\n\nВот так теперь выглядит твоя анкета⏬")
    show(message)


def change_social(message):
    cur.execute(f"""UPDATE users SET social_media='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()
    bot.send_message(chat_id=message.chat.id, text="Данные изменены!\n\nВот так теперь выглядит твоя анкета⏬")
    show(message)


def change_work(message):
    cur.execute(f"""UPDATE users SET activity='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()
    bot.send_message(chat_id=message.chat.id, text="Данные изменены!\n\nВот так теперь выглядит твоя анкета⏬")
    show(message)


def change_about(message):
    cur.execute(f"""UPDATE users SET interests='{message.text}' WHERE userid={message.chat.id}""")
    conn.commit()
    bot.send_message(chat_id=message.chat.id, text="Данные изменены!\n\nВот так теперь выглядит твоя анкета⏬")
    show(message)


@bot.callback_query_handler(func=lambda call: call.data == 'find')
def find(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

    cur.execute(f"""SELECT * FROM users WHERE network=1 AND userid<>{call.message.chat.id} ORDER BY random() LIMIT 1;""")
    info = cur.fetchone()

    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Написать собеседнику', url=f'https://t.me/{info[1]}')
    btn2 = types.InlineKeyboardButton('Следующий собеседник', callback_data='find')
    btn3 = types.InlineKeyboardButton('Поменять данные профиля', callback_data='change')
    btn4 = types.InlineKeyboardButton('Приостановить участие❌', callback_data='stop')
    kb.add(btn1)
    kb.add(btn2)
    kb.add(btn3)
    kb.add(btn4)

    bot.send_message(chat_id=call.message.chat.id, text=f"{info[2]}\nПрофиль: {info[3]}\n\n◽ Чем занимается:"
                                                   f" {info[4]}\n◽ Зацепки для начала разговора: {info[5]}", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cur.execute(f"""UPDATE users SET network=0 WHERE userid={call.message.chat.id}""")
    conn.commit()

    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Возобновить участие', callback_data='continue')
    kb.add(btn1)

    bot.send_message(chat_id=call.message.chat.id, text='Участие приостановлено', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'continue')
def cont(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cur.execute(f"""UPDATE users SET network=1 WHERE userid={call.message.chat.id}""")
    conn.commit()
    bot.send_message(chat_id=call.message.chat.id, text='Участие возобновлено!')
    sshow(call)


@bot.callback_query_handler(func=lambda call: call.data == 'questions')
def questions(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Спикеры форума', callback_data='speakers')
    #btn2 = types.InlineKeyboardButton('О клубе', callback_data='about_club')
    btn3 = types.InlineKeyboardButton('FAQ', callback_data='faq')
    btn4 = types.InlineKeyboardButton('Партнёры форума', callback_data='partners')
    btn5 = types.InlineKeyboardButton('<<Вернуться назад', callback_data='back')
    kb.add(btn1)
    #kb.add(btn2)
    kb.add(btn3)
    kb.add(btn4)
    kb.add(btn5)

    bot.send_message(call.message.chat.id, 'Этот раздел отвечает на часто задаваемые вопросы и предоставляет'
                                           ' общую информацию о Бизнес-клубе.', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data in ['speakers', 'about_club', 'faq', 'partners'])
def questions_raspr(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    btn = types.InlineKeyboardButton('<<Вернуться назад', callback_data='questions')

    if call.data == 'speakers':
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Татьяна Бакальчук', callback_data='speaker1')
        btn2 = types.InlineKeyboardButton('Сергей Иванов', callback_data='speaker2')
        btn3 = types.InlineKeyboardButton('Оскар Хартман', callback_data='speaker3')
        btn4 = types.InlineKeyboardButton('Эдуард Гуринович', callback_data='speaker4')
        btn5 = types.InlineKeyboardButton('Дмитрий Кибкало', callback_data='speaker5')
        btn6 = types.InlineKeyboardButton('Роман Маресов', callback_data='speaker6')
        btn7 = types.InlineKeyboardButton('Максим Ноготков', callback_data='speaker7')
        btn8 = types.InlineKeyboardButton('Анна Рудакова', callback_data='speaker8')
        #kb.add(btn1)
        kb.add(btn2)
        kb.add(btn3)
        kb.add(btn4)
        kb.add(btn5)
        kb.add(btn6)
        kb.add(btn7)
        kb.add(btn8)
        kb.add(btn)

        bot.send_message(call.message.chat.id, '🎙Наши спикеры:', reply_markup=kb)
    elif call.data == 'about_club':
        '''чето о клубе'''
        pass
    elif call.data == 'faq':
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Когда и где состоится Форум?', callback_data='when')
        btn2 = types.InlineKeyboardButton('Кто может посетить Форум?', callback_data='who')
        btn3 = types.InlineKeyboardButton('Можно ли посетить мероприятие онлайн?', callback_data='online')
        btn4 = types.InlineKeyboardButton('Какие правила участия в Форуме?', callback_data='rules')
        btn5 = types.InlineKeyboardButton('Сколько всего может быть участников?', callback_data='parts')
        btn6 = types.InlineKeyboardButton('Сколько стоит посещение мероприятия?', callback_data='cost')
        kb.add(btn1)
        kb.add(btn2)
        kb.add(btn3)
        kb.add(btn4)
        kb.add(btn5)
        kb.add(btn6)
        kb.add(btn)

        bot.send_message(call.message.chat.id, '🤔Здесь ты можешь найти ответы на часто задаваемые вопросы.', reply_markup=kb)

    elif call.data == 'partners':
        kb = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton('Kept', callback_data='partner1')
        btn2 = types.InlineKeyboardButton('КРОК', callback_data='partner2')
        btn3 = types.InlineKeyboardButton('Московский аэропорт Домодедово', callback_data='partner3')
        btn4 = types.InlineKeyboardButton('Нетология', callback_data='partner4')
        btn5 = types.InlineKeyboardButton('Альфа-Банк', callback_data='partner5')
        btn6 = types.InlineKeyboardButton('SBS Consulting', callback_data='partner6')
        btn7 = types.InlineKeyboardButton('ВсеИнструменты.ру', callback_data='partner7')
        btn8 = types.InlineKeyboardButton('SF Education', callback_data='partner8')
        btn9 = types.InlineKeyboardButton('Додо Пицца', callback_data='partner9')
        btn10 = types.InlineKeyboardButton('ДОМ.РФ', callback_data='partner10')
        btn11 = types.InlineKeyboardButton('Груша', callback_data='partner11')
        btn12 = types.InlineKeyboardButton('Российская федерация Го', callback_data='partner12')
        btn13 = types.InlineKeyboardButton('ВкусВилл', callback_data='partner13')
        btn14 = types.InlineKeyboardButton('Level Group', callback_data='partner14')
        btn15 = types.InlineKeyboardButton('Petroglyph', callback_data='partner15')

        kb.add(btn1)
        kb.add(btn2)
        kb.add(btn3)
        kb.add(btn4)
        kb.add(btn5)
        kb.add(btn6)
        kb.add(btn7)
        kb.add(btn8)
        kb.add(btn9)
        kb.add(btn10)
        kb.add(btn11)
        kb.add(btn12)
        kb.add(btn13)
        kb.add(btn14)
        kb.add(btn15)
        kb.add(btn)

        bot.send_message(call.message.chat.id, 'Наши партнеры:', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == 'when')
def when(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('map.png', 'rb'), 'Форум HSE Business Club состоится 27 мая 2023 года с'
                                                        ' 10:00 до 19:00 в Культурном Центре НИУ ВШЭ по адресу: г.'
                                                        ' Москва, Покровский бульвар 11 стр. 6.')


@bot.callback_query_handler(func=lambda call: call.data == 'who')
def who(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.message.chat.id, text='Участниками Форума могут стать все желающие. Необходима'
                                                        ' регистрация.')


@bot.callback_query_handler(func=lambda call: call.data == 'rules')
def rules(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.message.chat.id, text='Правила посещения форума стандартны для любого массового'
                                                        ' мероприятия. Подробнее Вы можете ознакомиться по этой'
                                                        ' ссылке: https://docs.google.com/document/d/13AmVpabDCXD6SDExlDUgyB-1aoEIT9xRJUVv7_mKUpA/edit')


@bot.callback_query_handler(func=lambda call: call.data == 'online')
def online(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.message.chat.id, text='Да, можно. И даже задать свой вопрос. Ссылка на онлайн-площадку'
                                                        ' Форума появится на сайте в день мероприятия.')


@bot.callback_query_handler(func=lambda call: call.data == 'parts')
def perts(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.message.chat.id, text='В онлайн-формате количество участников Форума не ограничено.'
                                                        '\nВ связи с ограниченной вместимостью площадки в офлайн-формате'
                                                        ' максимальное количество участников'
                                                        ' Форума составляет 500 человек.')


@bot.callback_query_handler(func=lambda call: call.data == 'cost')
def cost(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(chat_id=call.message.chat.id, text='Посещение Форума бесплатно, однако требуется обязательная'
                                                        ' предварительная регистрация.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker1')
def speaker1(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker1.jpg', 'rb'), 'Татьяна Бакальчук — российская предпринимательница,'
                                                        ' основательница и генеральный директор компании Wildberries'
                                                        ' — российского международного интернет-магазина одежды,'
                                                        ' обуви, товаров для дома и других товаров. По данным Forbes,'
                                                        ' на август 2021 года Татьяна Бакальчук была самой богатой'
                                                        ' женщиной России с состоянием в 13 млрд $. В 2022 году'
                                                        ' состояние оценивалось в 2,1 млрд$.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker2')
def speaker1(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker2.png', 'rb'), '27 мая на Форуме HSE Business Club 2023 выступит'
                                                                     ' исполнительный директор ГК «Эфко» Сергей Иванов'
                                                                     ' с темой «Куда приводят мечты».\n\nВ 1997 году'
                                                                     ' Сергей Иванов окончил Новосибирский '
                                                                     'государственный университет по специальности'
                                                                     ' «экономист-математик». Сразу после окончания'
                                                                     ' университета начал работать в Новосибирском'
                                                                     ' жировом комбинате, а с 2001 по 2005 год стал '
                                                                     'генеральным директором.\n\nС 2005 по 2010 год '
                                                                     'был генеральным директором УК «Солнечные'
                                                                     ' продукты», а в 2011 году — генеральным'
                                                                     ' директором компании «Дымов». С 2012 по 2018 год'
                                                                     ' — генеральный директор и со-основатель компании'
                                                                     ' «Даурия аэроспейс», основатель «Экзектфарминг».'
                                                                     '\n\nС 2018 года Сергей Иванов — совладелец группы '
                                                                     '«Эфко», исполнительный директор и член совета '
                                                                     'директоров.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker3')
def speaker3(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker3.png', 'rb'), 'Оскар Хартманн — серийный предприниматель, '
                                                                     'международный инвестор и бизнес-ангел!\n\n'
                                                                     'В 2023 году Оскар занял 18 место среди лучших '
                                                                     'бизнес-ангелов мира по версии CB Insights. За '
                                                                     'прошедшее десятилетие Хартманн проинвестировал '
                                                                     'в более 100 компаний, 14 из которых '
                                                                     'стали единорогами.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker4')
def speaker4(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker4.png', 'rb'), 'Эдуард Гуринович - сооснователь сервиса '
                                                                     'CarPrice, предприниматель и инвестор. В юности он'
                                                                     ' заработал свой первый миллион рублей, продавая '
                                                                     'футбольную атрибутику через группу в "ВКонтакте".'
                                                                     '\n\nВ 2012 году он победил в конкурсе для молодых'
                                                                     ' предпринимателей и совместно с Оскаром '
                                                                     'Хартманном запустил компанию CarPrice в 2014 '
                                                                     'году. Компания привлекла инвестиции на сумму '
                                                                     'около $42 млн из Восточной Европы и Азии и стала '
                                                                     'одним из самых обсуждаемых стартапов Европы.'
                                                                     '\n\nСейчас CarPrice занимает 13 место в списке '
                                                                     'Forbes самых дорогих компаний Рунета, стоимость '
                                                                     'компании превышает $540 млн.\n\nЭдуард также '
                                                                     'инвестирует в технологичные стартапы, включая '
                                                                     'Dbrain, R-Set, "Близкие.ру" и свой собственный '
                                                                     'проект Expload - блокчейн-платформу для '
                                                                     'децентрализованных игр. В 2019 году его включили '
                                                                     'в список Forbes "30 under 30" в категории '
                                                                     '"Инвестиции".')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker5')
def speaker5(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker5.png', 'rb'), 'Дмитрий Кибкало – серийный предприниматель, '
                                                                     'инвестор, основатель венчурной студии «Орбита». '
                                                                     'Также является основателем и экс-владельцем сети'
                                                                     ' магазинов «Мосигра».\n\nВ 2013 году Дмитрий '
                                                                     'Кибкало вошел в список молодых предпринимателей'
                                                                     ' издания Forbes, создавших серьезный бизнес до '
                                                                     '33 лет. В 2019 продал «Мосигру» и в рамках '
                                                                     'венчурной студии «Орбита» запустил более 10 '
                                                                     'стартапов, в том числе: \n\nBigbro.ai'
                                                                     ' – CV-решение для аналитики футбольных матчей,'
                                                                     ' Vox – дейтинг на голосовых сообщениях,\n\nCabinet.fm'
                                                                     ' – сервис для консультантов, Partystation – '
                                                                     'платформа для пати-игр, «Метеор» – сеть '
                                                                     'футбольных школ, «Звезда» – сеть танцевальных '
                                                                     'школ и другие. Кроме того, Дмитрий — автор '
                                                                     'книг «Бизнес как игра» (обладатель премии '
                                                                     '«Деловая книга года») и «Бизнес на свои».')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker6')
def speaker6(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker6.jpg', 'rb'), 'Роман Маресов — CEO «Яндекс Еда», победитель '
                                                                     'рейтинга Forbes «30 under 30» в номинации '
                                                                     '«Управление» в 2021 году.\n\nВ 15 лет Роман '
                                                                     'поступил на факультет вычислительной математики '
                                                                     'и кибернетики МГУ. Свою карьеру начал со '
                                                                     'стажировки в Ernst&Young, продолжил в McKinsey '
                                                                     'в роли консультанта. \n\nВ 2017 году Роман '
                                                                     'перешел работать в «Яндекс», где отвечал за '
                                                                     'качество сервиса «Яндекс Такси» во всех странах '
                                                                     'присутствия, вместе с командой строил вертикаль '
                                                                     'безопасности сервиса и запустил проект по '
                                                                     'сотрудничеству с самозанятыми таксистами. В 2020'
                                                                     ' году Роман занял должность директора по продукту'
                                                                     ' (CPO) «Яндекс Go», а уже в октябре 2021 был '
                                                                     'назначен на позицию CEO сервиса «Яндекс Еда».'
                                                                     '\n\nНа Форуме HSE Business Club 2023, 27 мая, '
                                                                     'Роман расскажет о командообразовании и поделится'
                                                                     ' экспертизой в управлении людьми в одном из '
                                                                     'крупнейших фудтех-сервисов России.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker7')
def speaker7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker7.jpg', 'rb'), 'Максим Ноготков начал свой предпринимательский '
                                                                     'путь ещё в школьные годы, занимаясь торговлей '
                                                                     'программами и определителями номеров для '
                                                                     'телефонов. В 18 лет, после окончания МГТУ им. '
                                                                     'Баумана, он открыл свою первую компанию под '
                                                                     'названием "Максус", занимавшуюся оптовой '
                                                                     'торговлей телефонами и аудиотехникой. Всего за '
                                                                     'два года он заработал свой первый миллион '
                                                                     'долларов.\n\nСпустя 7 лет после запуска "Максуса"'
                                                                     ' были открыты первые магазины под брендом '
                                                                     '"Связной". Вскоре "Связной" стал динамично '
                                                                     'развивающейся группой компаний, в состав которой'
                                                                     ' вошёл "Промторгбанк", переименованный в "Связной'
                                                                     ' Банк" в 2010 году. Благодаря успехам группы, в '
                                                                     '2012 году, в возрасте 35 лет, Максим Ноготков '
                                                                     'стал самым молодым российским миллиардером в '
                                                                     'истории и был включен в список Forbes.')


@bot.callback_query_handler(func=lambda call: call.data == 'speaker8')
def speaker7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('speaker8.png', 'rb'), 'Анна Рудакова — создатель образовательной '
                                                                     'платформы WE University, основатель крупнейшего '
                                                                     'в России бизнес-форума для женщин Woman Who '
                                                                     'Matters, а также одноименной премии. Спикер '
                                                                     'международного форума Forbes Woman Day о '
                                                                     'гендерном равенстве в бизнесе, политике, '
                                                                     'обществе, мире. Автор трансформационной '
                                                                     'программы «Стратегия жизни». До этого несколько'
                                                                     ' лет занималась развитием социальных программ'
                                                                     ' в крупных компаниях.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner1')
def partner1(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Kept — аудиторско-консалтинговая фирма, ранее являвшаяся частью'
                                           ' международной сети KPMG. Компания с 2009 года является крупнейшей '
                                           'аудиторской фирмой в стране. Kept специализируется на проведении аудита '
                                           'финансовой отчетности, предоставлении услуг по улучшению показателей '
                                           'эффективности и управлению рисками.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner2')
def partner2(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'КРОК — технологический партнер с комплексной экспертизой в области '
                                           'построения и развития инфраструктуры, внедрения информационных систем и '
                                           'разработки программных решений.\n«КРОК» проведет игру «ИТ в глазах '
                                           'смотрящего», между участниками которой будут разыграны суперпаки с '
                                           'кастомными носками, патчами, шоколадом и тайм-ботом! У участников Форума '
                                           'будет возможность пройти тест «Кто ты из сотрудников КРОК», который '
                                           'расскажет, кем бы вы могли работать в компании.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner3')
def partner3(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Московский аэропорт Домодедово — одна из крупнейших воздушных гаваней '
                                           'России с многолетней историей. В 2021 году аэропорт обслужил 25,1 млн '
                                           'человек. Создание высококвалифицированной рабочей силы и системы инвестиций '
                                           'в обучение — основные принципы, которыми руководствуется аэропорт. На '
                                           'Форуме узнаете больше об успешной кадровой политике компании!')


@bot.callback_query_handler(func=lambda call: call.data == 'partner4')
def partner4(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('partner4.png', 'rb'), 'Воркшоп от Нетологии на Форуме HSE Business Club'
                                                                     ' 2023\n\n27 мая Оксана Озерная, продюсер '
                                                                     'направления «Высшее образование» Нетологии, '
                                                                     'проведет воркшоп на тему «Как ставить долгосрочные'
                                                                     ' цели: отслеживание прогресса и достижение '
                                                                     'результата».\n\nНетология — это образовательная '
                                                                     'платформа с 12-летним опытом на EdTech-рынке. '
                                                                     'Компания реализует 11 направлений обучения, среди'
                                                                     ' которых программы высшего образования в '
                                                                     'партнерстве с ведущими вузами страны. Нетология '
                                                                     '4 раза получала «Премию Рунета», вошла в рейтинг '
                                                                     'Forbes «20 самых дорогих компаний Рунета» с '
                                                                     'оценкой $90+ млн и рейтинг РБК «35 крупнейших '
                                                                     'EdTech-компаний России».\n\n27 мая у вас будет '
                                                                     'возможность узнать:\n\n- что такое цель с точки '
                                                                     'зрения личностных изменений;\n- какие методики '
                                                                     'постановки целей существуют и как отслеживать '
                                                                     'прогресс достижения цели;\n- в чем польза '
                                                                     'маленьких шагов в процессе достижения результата.'
                                                                     '\n- На воркшопе вы также выполните практические '
                                                                     'упражнения по целеполаганию и получите ответы '
                                                                     'на интересующие вопросы.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner5')
def partner5(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Альфа-Банк — крупнейший частный банк России, основанный в 1990 году. В 2022'
                                           ' году Альфа-Банк стал обладателем золотого статуса в рейтинге лучших '
                                           'работодателей России по версии Forbes. На Форуме HSE Business Club 2023 вы '
                                           'сможете лично узнать о карьерных возможностях в Альфа-Банке!')


@bot.callback_query_handler(func=lambda call: call.data == 'partner6')
def partner6(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_photo(call.message.chat.id, open('partner6.png', 'rb'), 'SBS Consulting – это компания, занимающаяся '
                                                                     'стратегическим консалтингом в различных областях'
                                                                     ' экономики. Организация на рынке уже 15 лет, в '
                                                                     'её портфеле более 500 проектов. Среди крупнейших'
                                                                     ' клиентов компании: Роснефть, Газпромбанк, '
                                                                     'Фосагро и другие. В 2019-2020 организация входила'
                                                                     ' в топ-50 всех работодателей России по версии '
                                                                     'HeadHunter.\n\nСпикер, обладающий 18-летним '
                                                                     'опытом управленческого консультирования, на '
                                                                     'воркшопе расскажет:\n\n- что ждёт рынок '
                                                                     'консалтинга в ближайшие годы;\n- как сейчас '
                                                                     'повышать операционную эффективность;\n- какие из '
                                                                     'нынешних трендов наиболее перспективны;\n- какие '
                                                                     'новые возможности открылись сейчас перед '
                                                                     'российскими компаниями.\n\nНа воркшопе вы также'
                                                                     ' сможете попрактиковаться в аналитике и получите'
                                                                     ' ответы на интересующие вопросы.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner7')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'ВсеИнструменты.ру — крупнейший маркетплейс по продаже товаров для дома,'
                                           ' дачи, строительства и ремонта. Компания входит в ТОП-10 крупнейших '
                                           'интернет-магазинов России и TOП-20 рейтинга «Лучших работодателей России» '
                                           '(крупнейшие компании).\nВы сможете узнать о Лидерской программе '
                                           'ВсеИнструменты.ру, направленной на реализацию лидерского потенциала и '
                                           'обучение выстраивания и оптимизации процессов!')


@bot.callback_query_handler(func=lambda call: call.data == 'partner8')
def partner9(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Бизнес-стратегия — это не просто план действий, а важный инструмент для'
                                           ' достижения успеха в современном бизнесе. Она помогает определить цели, '
                                           'установить приоритеты и создать устойчивую конкурентную позицию на рынке.'
                                           '\n\nСовместно с нашим партнером, SF Education, мы подготовили пост о том, '
                                           'зачем нужна бизнес-стратегия, какие ее основные преимущества и по каким '
                                           'принципам можно ее разработать.\n\nSF Education (https://vk.com/sfeducation)'
                                           ' — это онлайн-университет с 140+ образовательными продуктами по финансам, '
                                           'аналитике и бизнесу и топ-10 компаний по качеству обучения по версии РБК. '
                                           'Его преподаватели — действующие профессионалы из известнейших российских и '
                                           'международных компаний, таких как Goldman Sachs, Wells Fargo, J.P. Morgan, '
                                           'EY, ВТБ, Сбербанк, Открытие, МАRS и т.п.\n\nОнлайн-университет дарит '
                                           'промокод BUSINESSHSE на скидку 50% на все продукты для наших подписчиков.'
                                           '\n\nНа обучении в SF Education вы сможете получить:\n\n— бесплатный '
                                           'трехдневный доступ к любому курсу;\n— бесконечный доступ к программам и ко'
                                           ' всем обновлениям;\n— ответ от преподавателей в течение 15 минут;\n—сильное'
                                           ' комьюнити;\n— бесплатные карьерные консультации;\n— решение реальных '
                                           'кейсов в процессе обучения.\n\nПереходите на страницу SF Education, чтобы '
                                           'узнать о всех программах: https://clck.ru/34Luds')


@bot.callback_query_handler(func=lambda call: call.data == 'partner9')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Додо Пицца — международная сеть пиццерий, которая началась в Сыктывкаре в '
                                           '2011 году, а сейчас работает уже в 16 странах. Пиццерия создает '
                                           'инновационную компанию из России на основе принципа полной открытости и '
                                           'делится успехами.\n\nПодписывайтесь на группу VK:\nhttps://vk.com/dodomsk'
                                           '\n\nВ группе также можно подписаться на рассылку с классными промокодами:'
                                           '\nhttp://vk.cc/cjzNoX\n\nА чтобы получить промокод на скидку 15% прямо '
                                           'сейчас, пройдите небольшой тест:\nhttps://madte.st/VucEg9Fx')


@bot.callback_query_handler(func=lambda call: call.data == 'partner10')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'ДОМ.РФ — экосистема, которая активно развивает жилищную сферу в России. '
                                           'Крупнейший финансовый институт меняет рынок ипотеки, разрабатывает '
                                           'мастер-планы городов, двигает цифровизацию стройки и любит приглашать в '
                                           'команды молодых специалистов! На Форуме вы сможете познакомиться с '
                                           'карьерными предложениями и поучаствовать в розыгрыше корпоративных призов.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner11')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Груша — сеть с 12 кафе в Москве и 3 в Дмитрове, производством сладостей, '
                                           'напитков, еды и обжаркой фермерского кофе. Главная ценность — создать место,'
                                           ' в котором можно отвлечься от ежедневных забот и получить удовольствие. '
                                           'Команда поддерживает экоинициативы, ценит своих сотрудников, а также '
                                           'категорична в вопросах качества и скорости.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner12')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Российская федерация Го — всероссийская общественная спортивная федерация. '
                                           'РФГ аккредитована Минспортом РФ, отвечает за проведение Чемпионатов России '
                                           'по го и других крупных соревнований. На Форуме представители РФГ научат вас'
                                           ' этой стратегической игре. Можно будет сыграть не одну партию!')


@bot.callback_query_handler(func=lambda call: call.data == 'partner13')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'ВкусВилл — сеть супермаркетов и собственная торговая марка продуктов. '
                                           'Компания в хорошем смысле слова нарушает привычные каноны продуктового '
                                           'бизнеса, за счет чего уже совершила революцию в ритейле. На март 2023 года'
                                           ' «ВкусВилл» имеет более 1350 магазинов в 72 городах России. На Форуме '
                                           'представители компании расскажут об ее особенностях, а также '
                                           'бесплатно угостят вкусной едой.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner14')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Level Group — один из лидеров рынка московского девелопмента. Для молодых '
                                           'талантов у компании есть программа стажировок, в этом году также анонсируют'
                                           ' старт первой лидерской программы Level Up. В компании можно развиваться в'
                                           ' направлениях маркетинга и рекламы, аналитики, экономики, продаж, '
                                           'юриспруденции, девелопмента, влиять на историю развития компании '
                                           'и всей индустрии.')


@bot.callback_query_handler(func=lambda call: call.data == 'partner15')
def partner7(call: types.CallbackQuery):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Petroglyph — компания , которая поставляет воду из самого центра Алтая. '
                                           'Вода содержит кальций, магний и другие полезные вещества. «Петроглиф» '
                                           'добывают из недр предгорий Чергинского хребта. Это место с чистейшей '
                                           'окружающей средой — все крупные производства находятся в '
                                           'сотнях километров от него.')


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(5)