import logging

import telebot
from django.conf import settings

logger = logging.getLogger(__name__)

token = getattr(settings, 'CHUVSUGUIDE_BOT_TOKEN', None)

if token:
    bot = telebot.TeleBot(getattr(settings, 'TELEBOT_SELLER_TOKEN', None))

    @bot.message_handler(commands=['start'])
    def start(message):
        msg = (
            'Добро пожаловать!\n'
            'Этот бот поможет вам разместить объявление в чате @insta1reklama\n'
            'Помощь по использованию бота https://t.me/c/1242266411/9\n'
        )
        bot.reply_to(message, msg)


    bot.infinity_polling()
