from telebot.types import ReplyKeyboardMarkup, KeyboardButton
'''
Функция которая продолжает диалог
'''
def continue_func():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    item = KeyboardButton('Продолжить')
    keyboard.row(item)
    return keyboard