import pandas as pd
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import load_tags_db, add_id_and_tags, add_referral_id
from Основа import send_main_content

# Глобальная переменная для хранения ID последних сообщений каждого пользователя
last_message_ids = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = f"@{update.message.from_user.username}"  # Имя пользователя
    user_id = update.message.from_user.id  # ID пользователя

    print(f"Start function called for user {user_id}")  # Отладка начала функции

    # Загружаем данные о пользователе
    user_data = load_tags_db().loc[load_tags_db()['ID'] == user_id]

    # Если пользователь уже взаимодействовал с ботом
    if user_data.empty:
        # Попробуем удалить старые сообщения (если они существуют)
        if user_id in last_message_ids:
            print(f"Удаление старых сообщений для пользователя {user_id}...")  # Отладка

            # Проверяем, есть ли у пользователя сообщения для удаления
            for msg_id in last_message_ids[user_id]:
                try:
                    print(f"Попытка удалить сообщение с message_id: {msg_id}")
                    await context.bot.delete_message(chat_id=update.message.chat_id, message_id=msg_id)
                    print(f"Удалено сообщение с message_id: {msg_id}")
                except Exception as e:
                    print(f"Ошибка при удалении сообщения с ID {msg_id}: {e}")
            # Очищаем список после удаления
            last_message_ids[user_id] = []

        # Отправляем картинку
        photo_path = r"C:\Users\User\Pictures\photo_5289552512413722406_y.jpg"
        sent_message = await update.message.reply_photo(photo=open(photo_path, 'rb'))
        print(f"Фото отправлено, message_id: {sent_message.message_id}")

        # Сохраняем ID отправленного фото
        last_message_ids.setdefault(user_id, []).append(sent_message.message_id)

        # Приветствие
        sent_message = await update.message.reply_text(
            "🙋‍♂️ Приветствую! Я - бот для сигналов [🚀Lucky Jet и 💣Mines]🌐 Я даю сигналы с невероятным винрейтом 90%+ ‼️ "
            "Наш бот основан на ChatGPT и ещё более 100 нейросетей."
        )
        print(f"Приветствие отправлено, message_id: {sent_message.message_id}")

        # Сохраняем ID приветственного сообщения
        last_message_ids[user_id].append(sent_message.message_id)

        # Добавляем пользователя в базу данных
        add_id_and_tags(user_id, user_name)

    # Дополнительная проверка для отладки
    print(f"Текущие last_message_ids для пользователя {user_id}: {last_message_ids[user_id]}")

    # Повторно загружаем данные о пользователе после добавления
    user_data = load_tags_db().loc[load_tags_db()['ID'] == user_id]

    # Проверка на наличие тега "реферал"
    if 'реферал' in user_data.iloc[0]['Теги'].split(','):
        await send_main_content(update, user_data)  # Переход к основному контенту
        return

    # Проверка, есть ли ID реферала
    if user_data.empty or pd.isna(user_data.iloc[0]['ID реферала']):
        # Если ID реферала нет, отправляем инструкции
        keyboard = [
            [InlineKeyboardButton("🌐РЕГИСТРАЦИЯ", url="https://1warlo.top/?open=register&p=mr6e")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_message = await update.message.reply_text(
            "👁️Для начала проведите регистрацию на 1win. Чтобы бот успешно проверил регистрацию, нужно соблюсти важные условия.‼️"
            "Аккаунт обязательно должен быть НОВЫМ! Если у вас уже есть аккаунт и при нажатии на кнопку 'РЕГИСТРАЦИЯ' вы попадаете на старый, "
            "необходимо выйти с него и заново нажать на кнопку 'РЕГИСТРАЦИЯ' после чего заново зарегистрироваться!⚠️ "
            "Чтобы бот смог проверить вашу регистрацию, обязательно нужно ввести промокод 'GUBA100' при регистрации! "
            "После РЕГИСТРАЦИИ бот автоматически переведёт вас к следующему шагу✔️", reply_markup=reply_markup
        )

        # Сохраняем ID инструкции
        last_message_ids[user_id].append(sent_message.message_id)

        await asyncio.sleep(5)  # Увеличенное ожидание
        return

    # Проверка корректности введенного ID
    if pd.isna(user_data.iloc[0]['ID реферала']):
        sent_message = await update.message.reply_text("✔️Введите ID только цифры!")
        last_message_ids[user_id].append(sent_message.message_id)

        # Устанавливаем флаг в контексте, что мы ожидаем ID
        context.user_data['waiting_for_referral_id'] = True
        return


# Обработчик для получения ID реферала
async def receive_referral_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    referral_id = update.message.text

    # Проверка, ожидаем ли мы ID
    if not context.user_data.get('waiting_for_referral_id', False):
        return

    # Загружаем данные о пользователе
    user_data = load_tags_db().loc[load_tags_db()['ID'] == user_id]

    # Проверка на корректность ID
    if not referral_id.isdigit():
        sent_message = await update.message.reply_text("❌ ID должен содержать только цифры!")
        last_message_ids[user_id].append(sent_message.message_id)
        return

    add_referral_id(user_id, referral_id)
    await update.message.reply_text(f"✅ Ваш реферал: {referral_id}")

    # Завершаем ожидание ID
    context.user_data['waiting_for_referral_id'] = False