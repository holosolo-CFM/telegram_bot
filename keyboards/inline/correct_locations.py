from loader import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.custom_handlers import commands

'''
Функции которые создают кнопки для городов, а также обработка функций в кнопках которых хранится айди городов
'''
def get_correct_location(list_of_cities):
    keyboard = InlineKeyboardMarkup()
    for num, item in enumerate(list_of_cities):
        keyboard.add(InlineKeyboardButton(item, callback_data='question_{}'.format(num)))
    return keyboard

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    with bot.retrieve_data(call.from_user.id,call.message.chat.id) as data:
        for i in range(5):
            if call.data == 'question_{}'.format(i):
                data['city_correct'] = data['city_correct'][i]
                bot.send_message(call.from_user.id,'Вы выбрали {}'.format(data['city_name'][i]))
                data['city_name'] = data['city_name'][i]
                commands.get_city_correct(call)