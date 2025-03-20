import telebot
import nest_asyncio
from config import TELEGRAM_TOKEN
from database import init_db
from handlers import register_handlers  


bot = telebot.TeleBot(TELEGRAM_TOKEN)


init_db()


register_handlers(bot)  


if __name__ == "__main__":
    nest_asyncio.apply()
    print("Бот запущен!")
    bot.infinity_polling()
