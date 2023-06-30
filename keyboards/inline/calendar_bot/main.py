from loader import bot
from keyboards.inline.calendar_bot.detailed import DetailedTelegramCalendar, LSTEP
from handlers.custom_handlers import commands

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              c.message.chat.id,
                              c.message.message_id)
        if bot.get_state(c.from_user.id) == 'UserHistoryInfo:date_of_entry':
            with bot.retrieve_data(c.from_user.id,c.message.chat.id) as data:
                data['date_of_entry'] = result
                commands.get_date_of_entry(c)
        elif bot.get_state(c.from_user.id) == 'UserHistoryInfo:date_of_departure':
            with bot.retrieve_data(c.from_user.id,c.message.chat.id) as data:
                data['date_of_departure'] = result
                commands.get_date_of_departure(c)
