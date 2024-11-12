import os
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from handlers import start, receive_referral_id
from database import load_tags_db, add_id_and_tags, add_referral_id

# Получение токена бота из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# Словарь для хранения ID последних сообщений каждого пользователя
last_message_ids = {}

# Функция для запуска бота
async def main():
    if not TOKEN:
        print("Ошибка: токен бота не найден. Установите TELEGRAM_BOT_TOKEN в переменных окружения.")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))  # Обработчик для /start
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_referral_id))  # Обработчик ввода ID реферала

    # Запуск бота
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Держим бот в активном состоянии
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())