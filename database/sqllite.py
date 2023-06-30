import sqlite3
# Устанавливаем соединение с базой данных
def start_db():
    conn = sqlite3.connect('your_path_to_db')
    cursor = conn.cursor()
    # Создаем таблицу "users"
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY AUTOINCREMENT,
                       userid TEXT)''')
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()