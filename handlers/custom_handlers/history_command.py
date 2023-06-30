from loader import bot
import sqlite3

@bot.message_handler(commands=['history'])
def get_history(message):
    conn = sqlite3.connect('C:\\Skillbox\\python_project\\venv\\structure_example\\database\\database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT command, city, hotels_name FROM users_info WHERE user_id = {}".format(message.from_user.id))
    rows = cursor.fetchall()
    for row in rows:
        total_info = []
        for info in row:
            total_info.append(info)
        bot.send_message(message.from_user.id, 'Введенная команда: {}\nЗапрошенный город: {}\nОтели в городе {}'.format(total_info[0],
                                                                                                                      total_info[1],
                                                                                                                      total_info[2]))
    conn.close()