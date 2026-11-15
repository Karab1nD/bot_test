# import telebot
import os
import telebot
from telebot import types


from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise RuntimeError("Не найден токен")

bot = telebot.TeleBot(TOKEN)

users = {}  # {123456789: {'question': 0, 'score': 0}}
questions = [
    {
        'code': 'x = 10\ny = 3\nprint(x // y)',
        'answers': ['3', '3.33', '1'],
        'correct': '3',
        'hint': '+'
    },
    {
        'code': 'print(len("Python"))',
        'answers': ['6', '5', 'Python'],
        'correct': '6'
    },
    {
        'code': 'x = 7\nif x > 5:\n    print("YES")\nelse:\n    print("NO")',
        'answers': ['NO', 'YES', 'NONE'],
        'correct': 'YES'
    },
    {
        'code': 'numbers = [1, 2, 3]\nprint(numbers[-1])',
        'answers': ['1', '3', '2'],
        'correct': '3',
        'hint': '+++++'
    },
]


@bot.message_handler(commands=["start"])
def start(message):
    users[message.from_user.id] = {'question': 0, 'score': 0}
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('python-квиз')
    bot.send_message(message.from_user.id, f"Привет! {message.from_user.first_name}", reply_markup=kb)

@bot.message_handler(func=lambda mess: mess.text.stip() == "Python-квиз")
def quiz(mess):
    userID = mess.from_user.id
    users[userID]['question'] = 0
    users[userID]['score'] = 0

    send_question(userID)


def finish(userID):
    text = ("Квиз завершен"
            f"\nВопросы: {users[userID]['question']}\nБаллы: {users[userID]['score']}")
    bot.send_message(userID, text, reply_markup=None)

def send_question(userID):
    number = users[userID]['question']
    question = questions[number]

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(*question['answers'])

    text = (
        f'*Вопрос {number + 1} из {len(questions)}*\n\n'
        'Что выведет код:\n\n'
        f'```python\n{question['code']}\n```\n\n'
        'Выберите правильный ответ:'
    )

    bot.send_message(userID, text, reply_markup=kb, parse_mode='Markdown')

@bot.message_handler(func=lambda mess: mess.from_user.id in users)
def check_answer(mess):
    chat_id = mess.from_user.id
    number = users[chat_id]['question']
    correct = questions[number]['correct']
    answer = mess.text.strip()

    if answer not in questions[number]['answers']:
        bot.send_message(chat_id, "Выберите из предложеных вариантов ответ ")
        return

    if answer == correct:
        users[chat_id]['score'] += 1
        users[chat_id]['question'] += 1
        bot.send_message(chat_id, f'Правильно!\nТвои баллы: {users[chat_id]["score"]}')

        if users[chat_id]['questions'] < len(questions):
            send_question(chat_id)
        else:
            finish(chat_id)
    else:
        kb = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Показать ответ', callback_data=f'show_{number}')
        button2 = types.InlineKeyboardButton('Показать ответ', callback_data=f'next_{number}')
        bot.send_message(chat_id, "Не правильно!")
        kb.add(button1)
        kb.add(button2)

        bot.send_message(chat_id, f'Неправильно!\nПодсказка {questions[number]['hint']}', reply_markup=kb)


    # if users[chat_id]['questions'] == len(questions):
    #     bot.send_message(chat_id, "Квиз завершен!\n\n"
    #                      f'Результат: \n{users[chat_id]['score']} верных ответов ')
    #     start(mess)
    # else:

@bot.callback_query_handler(func=lambda mess: mess.data.startswith('show') or mess.data.startswith('next'))
def inline_handler(mess):
    chat_id = mess.from_user.id
    if chat_id not in users:
        bot.answer_callback_query(mess.id)
        return

    action, number = mess.data.split('_')
    number = int(number)

    if action == 'show':
        correct = questions[number]['correct']
        bot.answer_callback_query(mess.id, f'Правильный ответ: {correct}', show_alert=True)
    elif action == 'next':
        users[chat_id]['questions'] += 1
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=mess.message.message_id, reply_markup=None)

        if users[chat_id]['questions'] < len(questions):
            send_question(chat_id)

print("Бот запущен")
bot.infinity_polling(skip_pending=True)