from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_user_actions, get_plant_info
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

async def send_reminders(context: CallbackContext):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f"Проверка напоминаний на {current_time}")

    for user_id in get_all_user_ids():  # Предполагается, что у тебя есть функция для получения всех user_id
        actions = get_user_actions(user_id)
        for action in actions:
            next_action_date = datetime.strptime(action["next_action_date"], '%Y-%m-%d %H:%M:%S')
            if next_action_date.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
                plant = get_plant_info(action["plant_id"])
                message = f"🌱 Напоминание: сегодня нужно {action['action_type']} растение {plant['name']}!"
                await context.bot.send_message(chat_id=user_id, text=message)

def start_scheduler(application):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        send_reminders,
        trigger=CronTrigger(hour=18, minute=20),  # Напоминания в 18:20 каждый день
        args=[application]
    )
    scheduler.start()

def main():
    application = Application.builder().token("7798509904:AAEbX-QgCVhjSK2Hp4KGM5sG3KAAI1J2zT0").build()
    application.add_handler(CommandHandler("start", start))
    
    # Запуск планировщика напоминаний
    start_scheduler(application)
    
    application.run_polling()

if __name__ == '__main__':
    main()
