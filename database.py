import pandas as pd
import os

EXCEL_FILE = r"C:\Users\User\Documents\Base_bot.xlsx"

# Функция для загрузки базы данных
def load_tags_db():
    try:
        df = pd.read_excel(EXCEL_FILE)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Название', 'Теги', 'ID', 'ID реферала', 'Дата окончания подписки'])
        try:
            df.to_excel(EXCEL_FILE, index=False)
        except Exception as e:
            print(f"Ошибка при создании файла базы данных: {e}")
    return df

# Функция для сохранения базы данных
def save_tags_db(df):
    try:
        df.to_excel(EXCEL_FILE, index=False)
    except Exception as e:
        print(f"Ошибка при сохранении базы данных: {e}")

# Функция для добавления ID и тегов
def add_id_and_tags(user_id, user_name):
    df = load_tags_db()
    if user_id not in df['ID'].values:
        new_record = pd.DataFrame({'Название': [user_name], 'Теги': ['новый пользователь'], 'ID': [user_id], 'ID реферала': [None], 'Дата окончания подписки': [None]})
        df = pd.concat([df, new_record], ignore_index=True)
        save_tags_db(df)  # Сохраняем изменения в базу данных

# Функция для добавления ID реферала и обновления тега
def add_referral_id(user_id, referral_id):
    df = load_tags_db()
    if user_id in df['ID'].values:
        # Приводим referral_id к целочисленному типу, если это необходимо
        df.loc[df['ID'] == user_id, ['ID реферала', 'Теги']] = [int(referral_id), 'реферал']
        save_tags_db(df)  # Сохраняем изменения в базу данных

# Функция для обновления тега и даты окончания подписки
def update_subscription_info(user_id, new_tag, end_date):
    df = load_tags_db()
    if user_id in df['ID'].values:
        df.loc[df['ID'] == user_id, ['Теги', 'Дата окончания подписки']] = [new_tag, end_date]
        save_tags_db(df)  # Сохраняем изменения в базу данных