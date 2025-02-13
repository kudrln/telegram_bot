import telebot
from telebot import types

bot = telebot.TeleBot('7798509904:AAEbX-QgCVhjSK2Hp4KGM5sG3KAAI1J2zT0')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '<b>привет 🖐🌿</b>', parse_mode='html')

bot.polling(none_stop=True)