from telebot.handler_backends import State, StatesGroup
'''
Временное хранение данных о пользователе
'''
class UserHistoryInfo(StatesGroup):
    command = State()
    city = State()
    city_name = State()
    city_correct = State()
    keyboard_city = State()
    date_of_entry = State()
    date_of_departure = State()
    total_days = State()
    hotels_number = State()
    hotels_list = State()
    hotels_id = State()
    custom_price_low = State()
    custom_price_high = State()
    hotels_price = State()
    images_number = State()
    hotels_images = State()
    hotels_addresses = State()
