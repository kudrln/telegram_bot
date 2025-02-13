import sqlite3
from datetime import datetime, timedelta

def get_db_connection():
    conn = sqlite3.connect('plants.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        photo TEXT,
        info TEXT,
        watering_interval INTEGER,
        spraying_interval INTEGER,
        fertilizing_interval INTEGER
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        plant_id INTEGER,
        action_type TEXT,
        action_date TEXT,
        next_action_date TEXT
    )
    ''')
    conn.commit()
    conn.close()

def get_plants():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM plants')
    plants = cursor.fetchall()
    conn.close()
    return plants

def get_plant_info(plant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
    plant = cursor.fetchone()
    conn.close()
    if plant:
        return {
            "id": plant["id"],
            "name": plant["name"],
            "photo": plant["photo"],
            "info": plant["info"],
            "watering_interval": plant["watering_interval"],
            "spraying_interval": plant["spraying_interval"],
            "fertilizing_interval": plant["fertilizing_interval"]
        }
    return None

def add_user_action(user_id, plant_id, action_type):
    plant = get_plant_info(plant_id)
    if not plant:
        print("Ошибка: растение не найдено.")
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    action_date = datetime.now()

    interval = 0
    if action_type == 'полить':
        interval = plant["watering_interval"]
    elif action_type == 'опрыскать':
        interval = plant["spraying_interval"]
    elif action_type == 'удобрить':
        interval = plant["fertilizing_interval"]

    next_action_date = action_date + timedelta(days=interval) if interval > 0 else action_date

    print(f"Запись действия: user_id={user_id}, plant_id={plant_id}, action_type={action_type}, action_date={action_date}, next_action_date={next_action_date}")

    cursor.execute('''
    INSERT INTO user_actions (user_id, plant_id, action_type, action_date, next_action_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, plant_id, action_type, action_date.strftime('%Y-%m-%d %H:%M:%S'), next_action_date.strftime('%Y-%m-%d %H:%M:%S')))

    conn.commit()
    conn.close()

def get_user_actions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_actions WHERE user_id = ?', (user_id,))
    actions = cursor.fetchall()
    conn.close()
    return actions

init_db()
