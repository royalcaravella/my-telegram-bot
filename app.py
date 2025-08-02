from flask import Flask, request
import requests
import telegram
import os
import asyncio  # Добавлено для обработки async

app = Flask(__name__)

# Telegram-токен (из переменной окружения в Render)
TOKEN = os.getenv('TOKEN')
bot = telegram.Bot(token=TOKEN)

# Hugging Face настройки (из переменной окружения в Render)
HF_API_URL = "https://api-inference.huggingface.co/models/gpt2"
HF_TOKEN = os.getenv('HF_TOKEN')

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    if update.message:
        message_text = update.message.text
        chat_id = update.message.chat_id
        
        # AI-интеграция
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {"inputs": message_text}
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            ai_result = response.json()[0].get('generated_text', 'Ошибка AI')[:100]
            if "заказ" in message_text.lower() or "cruise" in message_text.lower():
                reply = f"Ваш заказ принят: {message_text}. AI-рекомендация: {ai_result} (детали по email)."
            else:
                reply = f"AI-ответ на ваш запрос: {ai_result}"
        else:
            reply = "Ошибка AI. Попробуйте позже."
        
        # Отправляем ответ пользователю (фикс async: используем asyncio.run для sync-вызова)
        try:
            asyncio.run(bot.send_message(chat_id=chat_id, text=reply, disable_notification=True))
        except Exception as e:
            print(f"Error sending message: {e}")  # Логируем ошибку для Render
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)