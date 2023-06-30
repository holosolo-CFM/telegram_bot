import sqlite3
from . import API
from loader import bot
from telebot.types import Message, CallbackQuery
from states.history import UserHistoryInfo
from keyboards.inline import correct_locations
from keyboards.inline.calendar_bot.detailed import DetailedTelegramCalendar, LSTEP
from keyboards.reply import stop_func
from keyboards.reply import continue_func
from database.sqllite import start_db

'''
Здесь хранятся команды lowprice, highprice, custom которые выводят отели в зависимости от команды
lowprice = Дешевые отели
highprice = Дорогие отели
custom = Пользователь сам вводит бюджет
'''

@bot.message_handler(commands=['lowprice','highprice','custom'])
def commands(message: Message)-> None:
	bot.set_state(message.from_user.id, UserHistoryInfo.command, message.chat.id)
	get_command(message)

@bot.message_handler(state=UserHistoryInfo.command)
def get_command(message:Message)->None:
	'''
	Здесь в состояние пользователя записывается команда, для дальнейшей обработки
	:param message:
	:return:
	'''
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		data['command'] = message.text
	keyboard_stop = stop_func.stop()
	start_db()
	bot.send_message(message.from_user.id, 'Для начала мне нужно узнать, в каком городе вы ищете отель?', reply_markup=keyboard_stop)
	bot.set_state(message.from_user.id,UserHistoryInfo.city,message.chat.id)

@bot.message_handler(state=UserHistoryInfo.city)
def get_city(message:Message)->None:
	'''
	Здесь у пользователя уточняется какой город он хочет выбрать и все города которые нашлись передаются названиями в виде кнопок
	:param message:
	:return:
	'''
	keyboard_stop = stop_func.stop()
	city_list = []
	city_list_id = []
	city = API.api_request(method_endswith='locations/v3/search',
						   params={"q": message.text, "locale": "en_US", "langid": "1033", "siteid": "300000001"},
						   method_type='GET')
	if city['sr'] != []:
		for i in range(len(city['sr'][:5])):
			if 'gaiaId' in city['sr'][i]:
				city_list.append(city['sr'][i]['regionNames']['fullName'])
				city_list_id.append(city['sr'][i]['gaiaId'])
			else:
				i += 1
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['city'] = message.text
			data['city_correct'] = city_list_id
			data['city_name'] = city_list
			data['keyboard_city'] = correct_locations.get_correct_location(city_list)
			bot.send_message(message.from_user.id, 'Давайте уточним город', reply_markup=data['keyboard_city'])
		bot.send_message(message.from_user.id, 'Кликните на наиболее подходящий вариант', reply_markup=keyboard_stop)
		bot.set_state(message.from_user.id, UserHistoryInfo.city_correct, message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Попробуйте другой город, также попробуйте написать город на латинице', reply_markup=keyboard_stop)

@bot.message_handler(state=UserHistoryInfo.city_correct)
def get_city_correct(message):
	'''
	После выбора точного города из кнопок вызывается удобный календарь
	:param message:
	:return:
	'''
	keyboard_stop = stop_func.stop()
	if isinstance(message, CallbackQuery):
		bot.send_message(message.from_user.id,'Выберите дату заезда')
		calendar, step = DetailedTelegramCalendar().build()
		bot.send_message(message.from_user.id,'Снизу календарь:',reply_markup=keyboard_stop)
		bot.send_message(message.message.chat.id,
						 f"Select {LSTEP[step]}",
						 reply_markup=calendar)
		bot.set_state(message.from_user.id, UserHistoryInfo.date_of_entry, message.message.chat.id)
	else:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			bot.send_message(message.from_user.id, 'Кажется вы не нажали на кнопку, нажмите на 1 из них', reply_markup=data['keyboard_city'])

@bot.message_handler(state=UserHistoryInfo.date_of_entry)
def get_date_of_entry(message):
	'''
	После выбора точного города из кнопок вызывается удобный календарь
	:param message:
	:return:
	'''
	if isinstance(message, CallbackQuery):
		keyboard_stop = stop_func.stop()
		bot.send_message(message.from_user.id,'Выберите дату выезда')
		calendar, step = DetailedTelegramCalendar().build()
		bot.send_message(message.from_user.id, 'Снизу календарь:', reply_markup=keyboard_stop)
		bot.send_message(message.message.chat.id,
						 f"Select {LSTEP[step]}",
						 reply_markup=calendar)
		bot.set_state(message.from_user.id, UserHistoryInfo.date_of_departure, message.message.chat.id)
	else:
		calendar, step = DetailedTelegramCalendar().build()
		bot.send_message(message.from_user.id, 'Выберите что-то из календаря', reply_markup=calendar)


@bot.message_handler(state=UserHistoryInfo.date_of_departure)
def get_date_of_departure(message):
	if isinstance(message, CallbackQuery):
		keyboard_stop = stop_func.stop()
		bot.send_message(message.from_user.id, 'Сколько отелей вывести? От 1 до 10', reply_markup=keyboard_stop)
		bot.set_state(message.from_user.id, UserHistoryInfo.hotels_number, message.message.chat.id)
	else:
		calendar, step = DetailedTelegramCalendar().build()
		bot.send_message(message.from_user.id, 'Выберите что-то из календаря', reply_markup=calendar)

@bot.message_handler(state=UserHistoryInfo.hotels_number)
def get_hotels_number(message:Message)->None:
	'''
	Здесь в состояние пользователя записываются цены, названия отелей на основе выбранной команды
	:param message:
	:return:
	'''
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if (message.text.isdigit() and 0 < int(message.text) < 11) or 'custom_price_high' in data:
			if 'custom_price_high' not in data:
				data['hotels_number'] = message.text
			data['hotels_list'] = []
			data['hotels_id'] = []
			data['hotels_price'] = []
			delta = abs(data['date_of_entry'] - data['date_of_departure'])
			data['total_days'] = delta.days
			date_check_in = str(data['date_of_entry']).split('-')
			date_check_out = str(data['date_of_departure']).split('-')
			sort_value = 'PRICE_LOW_TO_HIGH'

			if data['command'] == '/lowprice':
				price_down = 10
				price_up = 500
			elif data['command'] == '/highprice':
				price_down = 500
				price_up = 10000
				sort_value = 'PRICE_HIGH_TO_LOW'
			elif data['command'] == '/custom' and 'custom_price_high' not in data:
				bot.send_message(message.from_user.id,'Введите минимальную цену')
				bot.set_state(message.from_user.id, UserHistoryInfo.custom_price_low)

			if 'custom_price_high' in data:
				price_down = int(data['custom_price_low'])
				price_up = int(data['custom_price_high'])

			if data['command'] != '/custom' or 'custom_price_high' in data:
				keyboard_stop = stop_func.stop()
				payload = {
					"currency": "USD",
					"eapid": 1,
					"locale": "en_US",
					"siteId": 300000001,
					"destination": {"regionId": data['city_correct']},
					"checkInDate": {
						"day": int(date_check_in[2]),
						"month": int(date_check_in[1]),
						"year": int(date_check_in[0])
					},
					"checkOutDate": {
						"day": int(date_check_out[2]),
						"month": int(date_check_out[1]),
						"year": int(date_check_out[0])
					},
					"rooms": [
						{
							"adults": 2,
							"children": [{"age": 5}, {"age": 7}]
						}
					],
					"resultsStartingIndex": 0,
					"resultsSize": 200,
					"sort": sort_value,
					"filters": {"price": {
						"max": price_up,
						"min": price_down
					}}
				}
				hotels = API.api_request(method_endswith='properties/v2/list', params=payload,method_type='POST')
				if hotels['data'] != None:
					target = int(data['hotels_number'])
					limit = len(hotels['data']['propertySearch']['properties'])
					if int(data['hotels_number']) > limit:
						target = limit
					for i in range(target):
						data['hotels_list'].append(hotels['data']['propertySearch']['properties'][i]['name'])
						data['hotels_id'].append(hotels['data']['propertySearch']['properties'][i]['id'])
						if hotels['data']['propertySearch']['properties'][i]['price']['options'][0]['strikeOut'] == None:
							data['hotels_price'].append('Цена не указана')
						else:
							data['hotels_price'].append(hotels['data']['propertySearch']['properties'][i]['price']['options'][0]['strikeOut']['amount'])
					bot.send_message(message.from_user.id, 'Сколько фоток вывести от 0 до 6',
									 reply_markup=keyboard_stop)
					bot.set_state(message.from_user.id, UserHistoryInfo.images_number, message.chat.id)
				else:
					bot.send_message(message.from_user.id, 'К сожалению для вашего города не нашлось отелей')
					bot.delete_state(message.from_user.id, message.chat.id)
		else:
			bot.send_message(message.from_user.id, 'Число должно быть в промежутке от 1 до 10\nСколько отелей вывести? От 1 до 10')


@bot.message_handler(state=UserHistoryInfo.custom_price_low)
def get_custom_price(message: Message)->None:
	'''
	Если выбрана команда /custom то у пользователя запрашивается минимальная цена
	:param message:
	:return:
	'''
	if message.text.isdigit() and int(message.text) > 0:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			data['custom_price_low'] = int(message.text)
		keyboard_stop = stop_func.stop()
		bot.send_message(message.from_user.id,'Введите максимальную цену', reply_markup=keyboard_stop)
		bot.set_state(message.from_user.id, UserHistoryInfo.custom_price_high,message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Цена должна быть больше 0')

@bot.message_handler(state=UserHistoryInfo.custom_price_high)
def get_custom_price(message: Message)->None:
	'''
    Если выбрана команда /custom то у пользователя запрашивается максимальная цена
    :param message:
    :return:
    '''
	with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
		if message.text.isdigit() and data['custom_price_low'] < int(message.text):
			keyboard = continue_func.continue_func()
			data['custom_price_high'] = message.text
			bot.set_state(message.from_user.id, UserHistoryInfo.hotels_number, message.chat.id)
			bot.send_message(message.from_user.id, 'Нажмите продолжить', reply_markup=keyboard)
		else:
			bot.send_message(message.from_user.id, 'Число должно быть больше предыдущего')

@bot.message_handler(state=UserHistoryInfo.images_number)
def get_hotels_images(message: Message)->None:
	'''
	Здесь выводится конечный результат с фотографиями и отелями
	:param message:
	:return:
	'''
	if message.text.isdigit() and 0 < int(message.text) < 7:
		with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
			bot.send_message(message.from_user.id, 'Это может занять некоторое время, пожалуйста подождите')
			data['images_number'] = message.text
			data['hotels_images'] = []
			data['hotels_addresses'] = []
			some_list = []
			for id in data['hotels_id']:
				payload = {
					"currency": "USD",
					"eapid": 1,
					"locale": "en_US",
					"siteId": 300000001,
					"propertyId": id
				}
				images = API.api_request(method_endswith='properties/v2/detail', params=payload,method_type='POST')
				data['hotels_addresses'].append(images['data']['propertyInfo']['summary']['location']['address']['addressLine'])
				for num in range(int(data['images_number'])):
					some_list.append(images['data']['propertyInfo']['propertyGallery']['images'][num]['image']['url'])
				data['hotels_images'].append(some_list)
				some_list = []
			for num, image_list in enumerate(data['hotels_images']):
				if data['hotels_price'][num] == 'Цена не указана':
					tot_price = 'Цена не указана'
				else:
					tot_price = round((data['total_days'] * data['hotels_price'][num]),2)
				bot.send_message(message.from_user.id, 'Отель: {}\nНаходится по адресу: {}\nЦена за 1 ночь: {}$\nЦена за все время проживание: {}$'.format(data['hotels_list'][num],
																														 data['hotels_addresses'][num],
																														 data['hotels_price'][num],
																												         tot_price))

				for image in image_list:
					bot.send_photo(message.chat.id, image)
			conn = sqlite3.connect('C:\\Skillbox\\python_project\\venv\\structure_example\\database\\database.db')
			cursor = conn.cursor()
			cursor.execute("INSERT INTO users (userid) VALUES ('{}')".format(message.from_user.id))
			cursor.execute('''CREATE TABLE IF NOT EXISTS users_info
							  (id INTEGER PRIMARY KEY AUTOINCREMENT,
							   user_id TEXT,
							   command TEXT,
							   city TEXT,
							   hotels_name TEXT)''')

			cursor.execute('''
			    INSERT INTO users_info (user_id, command, city, hotels_name)
			    VALUES (?, ?, ?, ?)
			''', (
				message.from_user.id,
				data['command'],
				data['city_name'],
				data['hotels_list'][0]
			))
			conn.commit()
			conn.close()
		bot.delete_state(message.from_user.id,message.chat.id)
	else:
		bot.send_message(message.from_user.id, 'Кол-во фото должно быть в пределах от 1 до 6')