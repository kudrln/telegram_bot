from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime, timedelta

# Функция для получения информации о растении
def get_plant_info(plant_id):
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
    plant = cursor.fetchone()
    conn.close()
    return plant

# Функция для добавления действия пользователя
def add_user_action(user_id, plant_id, action_type):
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    action_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    plant = get_plant_info(plant_id)
    if action_type == 'watering':
        next_action_date = (datetime.now() + timedelta(days=plant[4])).strftime('%Y-%m-%d %H:%M:%S')
    elif action_type == 'spraying':
        next_action_date = (datetime.now() + timedelta(days=plant[5])).strftime('%Y-%m-%d %H:%M:%S')
    elif action_type == 'fertilizing':
        next_action_date = (datetime.now() + timedelta(days=plant[6])).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('INSERT INTO user_actions (user_id, plant_id, action_type, action_date, next_action_date) VALUES (?, ?, ?, ?, ?)',
                   (user_id, plant_id, action_type, action_date, next_action_date))
    conn.commit()
    conn.close()

# Функция для получения списка растений
def get_plants():
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM plants')
    plants = cursor.fetchall()
    conn.close()
    return plants

# Обработчик команды /start
def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    update.message.reply_text(f"привет, {user_name}🖐!", reply_markup=ReplyKeyboardMarkup([
        ['уход за растением 🍃'],
        ['информация о растении 📌'],
        ['календарь 📅']
    ], resize_keyboard=True))

# Обработчик кнопки "Уход за растением"
def plant_care(update: Update, context: CallbackContext):
    plants = get_plants()
    buttons = [[plant[1]] for plant in plants]
    update.message.reply_text("выбери растение:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

# Обработчик выбора растения для ухода
def choose_plant_care(update: Update, context: CallbackContext):
    plant_name = update.message.text
    plants = get_plants()
    plant_id = next((plant[0] for plant in plants if plant[1] == plant_name), None)
    if plant_id:
        update.message.reply_text("выбери действие:", reply_markup=ReplyKeyboardMarkup([
            ['полив 🚿', 'опрыскивание 💦', 'удобрение 💩']
        ], resize_keyboard=True))
        context.user_data['plant_id'] = plant_id

# Обработчик выбора действия для ухода
def choose_care_action(update: Update, context: CallbackContext):
    action_type = update.message.text.lower()
    plant_id = context.user_data.get('plant_id')
    if plant_id:
        add_user_action(update.message.from_user.id, plant_id, action_type)
        update.message.reply_text(f"действие '{action_type}' записано в календарь (˶˃ ᵕ ˂˶)")

# Обработчик кнопки "Информация о растении"
def plant_info(update: Update, context: CallbackContext):
    plants = get_plants()
    buttons = [[plant[1]] for plant in plants]
    update.message.reply_text("выбери растение:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

# Обработчик выбора растения для информации
def choose_plant_info(update: Update, context: CallbackContext):
    plant_name = update.message.text
    plants = get_plants()
    plant = next((plant for plant in plants if plant[1] == plant_name), None)
    if plant:
        update.message.reply_photo(plant[2], caption=plant[3])

# Обработчик кнопки "Календарь"
def calendar(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    conn = sqlite3.connect('plants.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_actions WHERE user_id = ?', (user_id,))
    actions = cursor.fetchall()
    conn.close()
    if actions:
        for action in actions:
            update.message.reply_text(f"растение: {get_plant_info(action[2])[1]}, Действие: {action[3]}, Дата: {action[4]}, Следующее действие: {action[5]}")
    else:
        update.message.reply_text("у тебя пока нет записей в календаре.")

# Основная функция
def main():
    updater = Updater("YOUR_BOT_TOKEN", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text("уход за растением 🍃"), plant_care))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, choose_plant_care))
    dp.add_handler(MessageHandler(Filters.text("полив 🚿") | Filters.text("опрыскивание 💦") | Filters.text("удобрение 💩"), choose_care_action))
    dp.add_handler(MessageHandler(Filters.text("информация о растении 📌"), plant_info))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, choose_plant_info))
    dp.add_handler(MessageHandler(Filters.text("календарь 📅"), calendar))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()