from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_plants, get_plant_info, add_user_action, get_user_actions
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    context.user_data.clear()
    await update.message.reply_text(
        f"привет, {user_name} 🖐!",
        reply_markup=ReplyKeyboardMarkup([
            ['уход за растением 🍃'],
            ['информация о растении 📌'],
            ['календарь 📅']
        ], resize_keyboard=True)
    )

async def plant_care(update: Update, context: CallbackContext):
    plants = get_plants()
    buttons = [[plant["name"]] for plant in plants]
    buttons.append(["в начало ↩"])
    context.user_data['mode'] = 'care'
    await update.message.reply_text("выбери растение для ухода:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

async def plant_info(update: Update, context: CallbackContext):
    plants = get_plants()
    buttons = [[plant["name"]] for plant in plants]
    buttons.append(["в начало ↩"])
    context.user_data['mode'] = 'info'
    await update.message.reply_text("выбери растение для просмотра информации:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

async def handle_text(update: Update, context: CallbackContext):
    text = update.message.text.strip().lower()

    if text == "в начало ↩":
        await start(update, context)
        return

    mode = context.user_data.get('mode')
    plants = get_plants()
    plant = next((p for p in plants if text in p["name"].lower()), None)

    if not plant:
        await update.message.reply_text("🌱 Растение не найдено. Попробуй ещё раз.")
        return

    if mode == 'care':
        context.user_data['plant_id'] = plant["id"]
        print(f"Выбрано растение с ID: {plant['id']}")
        await update.message.reply_text(
            "выбери действие:",
            reply_markup=ReplyKeyboardMarkup([
                ['полить 🚿', 'опрыскать 💦', 'удобрить 💩'],
                ['в начало ↩']
            ], resize_keyboard=True)
        )
    elif mode == 'info':
        plant_details = get_plant_info(plant["id"])
        if plant_details:
            await update.message.reply_photo(plant_details["photo"], caption=plant_details["info"])
        else:
            await update.message.reply_text("❗ Информация о растении не найдена.")

async def choose_care_action(update: Update, context: CallbackContext):
    action_type = update.message.text.lower().split()[0]  # Убираем эмодзи, оставляем только первое слово
    plant_id = context.user_data.get('plant_id')
    
    print(f"Проверка действия: {action_type}, plant_id: {plant_id}")

    if plant_id and action_type in ['полить', 'опрыскать', 'удобрить']:
        print(f"Действие '{action_type}' выполняется для растения с ID: {plant_id}")
        add_user_action(update.message.from_user.id, plant_id, action_type)
        await update.message.reply_text(f"Действие '{action_type}' записано в календарь. 🌿")
    else:
        print("Ошибка: действие или растение не выбрано.")
        await update.message.reply_text("Ошибка: действие или растение не выбрано.")

async def calendar(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    actions = get_user_actions(user_id)
    
    if actions:
        for action in actions:
            plant = get_plant_info(action["plant_id"])
            if plant:
                try:
                    action_date = datetime.strptime(action["action_date"], '%Y-%m-%d %H:%M:%S')
                    next_action_date = datetime.strptime(action["next_action_date"], '%Y-%m-%d %H:%M:%S')
                    
                    await update.message.reply_text(
                        f"🌱 Растение: {plant['name']}\n"
                        f"📅 Действие: {action['action_type']}\n"
                        f"🕒 Дата последнего действия: {action_date.strftime('%d-%m-%Y')}\n"
                        f"📆 Следующее действие: {next_action_date.strftime('%d-%m-%Y')}"
                    )
                except ValueError as e:
                    logger.error(f"Ошибка преобразования даты: {e}")
                    await update.message.reply_text("❗ Ошибка отображения даты. Попробуй позже.")
            else:
                await update.message.reply_text("❗ Растение не найдено.")
    else:
        await update.message.reply_text("У тебя пока нет записей в календаре.")

async def send_reminders(context: CallbackContext):
    logger.info("Проверка напоминаний")
    current_time = datetime.now().strftime('%Y-%m-%d')
    for user_id in get_all_user_ids():
        actions = get_user_actions(user_id)
        for action in actions:
            next_action_date = datetime.strptime(action["next_action_date"], '%Y-%m-%d %H:%M:%S')
            if next_action_date.strftime('%Y-%m-%d') == current_time:
                plant = get_plant_info(action["plant_id"])
                message = f"🌱 Напоминание: сегодня нужно {action['action_type']} растение {plant['name']}!"
                await context.bot.send_message(chat_id=user_id, text=message)

def get_all_user_ids():
    # Заглушка для теста — добавь код, который извлекает все уникальные user_id из таблицы user_actions
    return [123456789, 987654321]  # Пример user_id

def start_scheduler(application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_reminders,
        trigger=CronTrigger(hour=18, minute=20),  # Напоминания каждый день в 18:20
        args=[application]
    )
    scheduler.start()

def main():
    application = Application.builder().token("7798509904:AAEbX-QgCVhjSK2Hp4KGM5sG3KAAI1J2zT0").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("уход за растением 🍃"), plant_care))
    application.add_handler(MessageHandler(filters.Text("информация о растении 📌"), plant_info))
    application.add_handler(MessageHandler(filters.Text("календарь 📅"), calendar))
    application.add_handler(MessageHandler(filters.Text(["полить 🚿", "опрыскать 💦", "удобрить 💩"]), choose_care_action))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    start_scheduler(application)  # Запуск планировщика напоминаний

    application.run_polling()

if __name__ == '__main__':
    main()
