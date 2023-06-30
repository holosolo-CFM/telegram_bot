from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from loader import bot
'''
Функция которая останавливает диалог с ботом
'''
def stop():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    item = KeyboardButton('/stop')
    keyboard.row(item)
    return keyboard

@bot.message_handler(commands=['stop'])
def stopped(message):
    if message.text == '/stop':
        bot.send_message(message.from_user.id, 'Сработала команда стоп, возвращаемся на главную страницу')
        bot.delete_state(message.from_user.id, message.chat.id)