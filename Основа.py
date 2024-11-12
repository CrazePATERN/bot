import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from database import load_tags_db, save_tags_db

# Функция для отправки инструкций по игре с кнопками
async def send_instructions(update: Update):
    user_id = update.message.from_user.id  # Извлекаем user_id из объекта update
    user_data = load_tags_db().loc[load_tags_db()['ID'] == user_id]

    # Создаем кнопки
    keyboard = [
        [InlineKeyboardButton("🎮Выберите нужный режим", callback_data="choose_mode")],
        [InlineKeyboardButton("♻️Назад", callback_data="go_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с инструкциями и кнопками
    await update.message.reply_text(
        "➡️ИНСТРУКЦИЯ⬅️\n"
        "🚀Для игры в Lucky Jet: Для более точных сигналов - пока летит ракета на сайте нажмите 'Получить сигнал', "
        "так бот проанализирует следующий шаг и даст точный сигнал. Не берите сигнал при загрузке раунда, бот не успеет проанализировать следующий шаг, и этот сигнал скорее всего приведет к проигрышу. "
        "Если бот говорит 'пропустить например 1 ход' - ждёте, пока ракета улетит 1 раз и ставите на следующий ход.\n"
        "💣Для игры в Mines: Для более точных сигналов - с начала возьмите сигнал у бота, бот выдаст проверенный и точный сигнал, ставьте точно так, как говорит бот.\n"
        "⚠️Перед каждым последующим сигналом, бот просит подождать 10 секунд, чтобы он успел проанализировать следующую ставку.\n"
        "⛔Ставьте 1-3-5% от баланса, чтобы в случае неверного сигнала у вас была возможность отыграться на следующем сигнале.\n"
        "💰Если сигнал не зашёл - увеличьте сумму ставки в 2 раза и получите новый сигнал.\n",
        reply_markup=reply_markup
    )

# Функция запуска таймера на подписку
async def start_subscription_timer(update, user_data):
    # Устанавливаем таймер на 28 дней (29-й день — это уведомление за день до окончания)
    await asyncio.sleep(28 * 24 * 60 * 60)  # 28 дней в секундах
    await update.message.reply_text("⚠️Предупреждение!😔 У вас остался 1 день (24 часа) до окончания платного периода!")

    # Ожидание последнего дня
    await asyncio.sleep(24 * 60 * 60)  # 1 день в секундах
    await update.message.reply_text("⚠️У вас кончился платный период. Пожалуйста, выберите способ оплаты для продления платного доступа!")
    
    # Обновление тегов
    tags = user_data.iloc[0]['Теги'].split(',')
    tags = [tag for tag in tags if tag not in ['Отсчёт', '1 месяц', 'Полный доступ', '1 неделя', '1 день']]
    tags.append('Пов оплата')
    tags.append('Отказался')
    user_data.at[user_data.index[0], 'Теги'] = ','.join(tags)
    save_tags_db(user_data)

# Основная функция обработки подписки с таймером
async def send_main_content(update: Update, user_data):
    user_id = update.message.from_user.id  # Извлекаем user_id из объекта update
    # Выводим текущие теги пользователя для отладки
    print("Текущие теги пользователя:", user_data.iloc[0]['Теги'])
    
    # Проверяем наличие "Полный доступ" и "1 месяц" среди тегов
    if 'Полный доступ' in user_data.iloc[0]['Теги']:
        if '1 месяц' in user_data.iloc[0]['Теги']:
            tags = user_data.iloc[0]['Теги'].split(',')
            if 'Отсчёт' not in tags:
                tags.append('Отсчёт')
            user_data.at[user_data.index[0], 'Теги'] = ','.join(tags)
            save_tags_db(user_data)

        # Запускаем таймер для подписки
        asyncio.create_task(start_subscription_timer(update, user_data))
        await send_instructions(update)
    
    # Вторая основная функция
    # Проверка на наличие тега "реферал"
    elif 'реферал' in user_data.iloc[0]['Теги'].split(','):
        print("Тег 'реферал' обнаружен, отправляем инструкцию")
        await send_instructions(update)
    else:
        # Если ни одно из условий не сработало, выводим сообщение для отладки
        print("Ни одно из условий не выполнено. Теги пользователя:", user_data.iloc[0]['Теги'])