from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
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

    # Проверка кнопки "в начало ↩"
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
    if context.user_data.get('mode') != 'care':
        return
    action_type = update.message.text.lower()
    plant_id = context.user_data.get('plant_id')
    if plant_id:
        add_user_action(update.message.from_user.id, plant_id, action_type)
        await update.message.reply_text(f"действие '{action_type}' записано в календарь. 🌿")
    else:
        await update.message.reply_text("ошибочка: растение не выбрано.")

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
                    await update.message.reply_text("Ошибка отображения даты. Попробуй позже.")
    else:
        await update.message.reply_text("у тебя пока нет записей в календаре.")

def main():
    application = Application.builder().token("7798509904:AAEbX-QgCVhjSK2Hp4KGM5sG3KAAI1J2zT0").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("уход за растением 🍃"), plant_care))
    application.add_handler(MessageHandler(filters.Text("информация о растении 📌"), plant_info))
    application.add_handler(MessageHandler(filters.Text("календарь 📅"), calendar))
    application.add_handler(MessageHandler(filters.Text(["полить 🚿", "опрыскать 💦", "удобрить 💩"]), choose_care_action))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()

if __name__ == '__main__':
    main()
