import os
import sys
from datetime import datetime, date

import django
import requests
from django.core.mail import send_mail
from dotenv import load_dotenv


# Добавляем путь к директории проекта в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'breakfast_lecture_planner'))

# Указываем путь к настройкам
os.environ['DJANGO_SETTINGS_MODULE'] = 'breakfast_lecture_planner.settings'

# Инициализируем Django
django.setup()

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
API_TOKEN = os.getenv("API_TOKEN")
API_URL = "https://malone.guru/api"

# Получаем список чатов из переменной окружения TELEGRAM_CHAT_IDS
TELEGRAM_CHAT_IDS = os.getenv("TELEGRAM_CHAT_IDS", "").split(',')

def send_email_task(subject, message, from_email, users):
    send_mail(subject, message, from_email, users)

def send_telegram_task(message, bot_token, chat_ids):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    for chat_id in chat_ids:
        data = {"chat_id": chat_id, "text": message}
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send message to chat {chat_id}. Error: {response.text}")

def get_users():
    """Получает список email пользователей через API"""
    headers = {"Authorization": f"Token {API_TOKEN}"}
    response = requests.get(f"{API_URL}/users/", headers=headers)

    if response.status_code == 200:
        users = response.json()
        return [user["email"] for user in users if "email" in user]
    else:
        print(f"Failed to fetch users. Error: {response.text}")
        return []

def send_participants_notification():
    headers = {"Authorization": f"Token {API_TOKEN}"}
    if not date.today().weekday() in (3, 4):
        print('Сегодня не четверг и не пятница')
        return
    users = get_users()
    message = ""
    response = requests.get(f"{API_URL}/lunch/participants/", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            # Формируем сообщение
            participants_list = "\n\n".join(
                [
                    f"{p['id']}: {p['name']}\nemail: {p['email']}\nКоличество порций: {p['portions']}\n"
                    + (f"Комментарий: {p['comment']}\n" if p['comment'] else "")
                    + f"Дата: {datetime.fromisoformat(p['registration_date']).strftime('%Y-%m-%d %H:%M')}"
                    for p in data
                ]
                )
            message += (f"Всего зарегистрированных участников обеда: {len(data)}\n\n"
                        f"Список участников ближайшего субботнего обеда:\n\n{participants_list}")

        else:
            print("Участников пока нет.")
    else:
        print(f"Ошибка при получении данных участников. Error: {response.text}")

    response = requests.get(f"{API_URL}/feedback/", headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data:
            # Сортировка по дате и выбор последних трех фидбеков
            data_sorted = sorted(data, key=lambda x: datetime.fromisoformat(x['date']), reverse=True)[:3]
            feedbacks_list = "\n\n".join(
                [
                    f"{f['id']}: {f['name']}\nemail: {f['email']}\n"
                    + f"Текст фидбека:\n{f['text']}\n"
                    + f"Дата и время отправки:\n{datetime.fromisoformat(f['date']).strftime('%Y-%m-%d %H:%M')}"
                    for f in data_sorted
                ]
            )
            if message:
                message += "\n\n=============\n\n"
            message += f"Последние фидбеки:\n\n{feedbacks_list}"
        else:
            print("Фидбеков пока нет.")
    else:
        print(f"Ошибка при получении фидбеков. Error: {response.text}")

    # Отправляем сообщение в Telegram
    send_telegram_task(message, BOT_TOKEN, TELEGRAM_CHAT_IDS)

    # Отправляем сообщение на почту
    send_email_task(
        "Список участника обеда и последние фидбеки",
        message,
        ADMIN_EMAIL,
        users,
    )


if __name__ == "__main__":
    send_participants_notification()
