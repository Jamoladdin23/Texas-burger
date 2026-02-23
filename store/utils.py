import os

import requests
from dotenv import load_dotenv

load_dotenv()


def send_telegram_message(message, photo_urls=None):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    url_text = f"https://api.telegram.org/bot{token}/sendMessage"
    payload_text = {"chat_id": chat_id, "text": message}

    response_text = requests.post(url_text, json=payload_text)

    if response_text.status_code != 200:
        print(f"❌ Ошибка Telegram: {response_text.json()}")

    # 🔹 Отправляем все фото товаров (если есть)
    if photo_urls:
        for photo_url in photo_urls:
            try:
                image_response = requests.head(photo_url)
                if image_response.status_code == 200:  # Фото доступно
                    url_photo = f"https://api.telegram.org/bot{token}/sendPhoto"
                    payload_photo = {"chat_id": chat_id, "photo": photo_url}
                    response_photo = requests.post(url_photo, json=payload_photo)

                    print(f"📷 Фото отправлено: {response_photo.json()}")
                else:
                    print(f"⚠️ Фото недоступно: {photo_url}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Ошибка при проверке фото: {str(e)}")

    print(f"✅ Сообщение отправлено: {response_text.json()}")
    return response_text.json()
