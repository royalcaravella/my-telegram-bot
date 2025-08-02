from flask import Flask, request
import telegram
import os
from datetime import datetime
import asyncio
import threading

app = Flask(__name__)

TOKEN = os.getenv('TOKEN')

def send_message_thread(chat_id, text):
    """Отправка сообщения в отдельном потоке"""
    try:
        async def send_async():
            bot = telegram.Bot(token=TOKEN)
            await bot.send_message(chat_id=chat_id, text=text, disable_notification=True)
        
        # Создаем новый event loop для потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_async())
        loop.close()
    except Exception as e:
        print(f"Error sending message: {e}")

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        # Создаем временный бот для парсинга
        temp_bot = telegram.Bot(token=TOKEN)
        update = telegram.Update.de_json(request.get_json(force=True), temp_bot)
        
        if update.message:
            message_text = update.message.text.lower()
            chat_id = update.message.chat_id
            user_name = update.message.from_user.first_name or "Клиент"
            original_text = update.message.text
            
            # Логика ответов
            if any(word in message_text for word in ['/start', 'привет', 'здравствуйте', 'добрый']):
                reply = f"Здравствуйте, {user_name}! 👋\n\nЯ бот RCC Lines для бронирования круизов.\n\n📋 Команды:\n• 'заказ' - забронировать круиз\n• 'цены' - узнать стоимость\n• 'круизы' - посмотреть маршруты\n• 'контакты' - связь с менеджером"
            
            elif any(word in message_text for word in ['заказ', 'забронировать', 'cruise', 'бронь']):
                order_id = f"#{chat_id}{datetime.now().strftime('%H%M')}"
                reply = f"✅ Заказ принят, {user_name}!\n\n📋 Ваш запрос: '{original_text}'\n🎫 Номер заявки: {order_id}\n\n📞 Менеджер свяжется с вами в течение 30 минут.\n\nДля срочных вопросов: +7 (800) 555-35-35"
            
            elif any(word in message_text for word in ['круиз', 'маршрут', 'направления']):
                reply = "🚢 Популярные круизы RCC Lines:\n\n1️⃣ Средиземноморье (7 дней) - от 890€\n2️⃣ Карибы (10 дней) - от 1200$\n3️⃣ Норвежские фьорды (5 дней) - от 750€\n4️⃣ Волга (3 дня) - от 15000₽\n\n💡 Для заказа напишите 'заказ' + номер круиза"
            
            elif any(word in message_text for word in ['цен', 'стоимость', 'сколько', 'прайс']):
                reply = "💰 Актуальные цены:\n\n🌊 Средиземноморье: 890-2500€\n🏝️ Карибы: 1200-3500$\n🏔️ Норвегия: 750-2200€\n🛥️ Волга: 15000-45000₽\n\n📝 Точная стоимость зависит от:\n• Категории каюты\n• Сезона\n• Количества человек\n\nДля расчета напишите 'заказ'"
            
            elif any(word in message_text for word in ['контакт', 'телефон', 'менеджер', 'связь']):
                reply = "📞 Контакты RCC Lines:\n\n☎️ Телефон: +7 (800) 555-35-35\n📧 Email: info@rcclines.com\n🕘 Часы работы: 9:00-21:00 МСК\n🌐 Сайт: rcclines.com\n\n💬 Или оставьте заявку здесь!"
            
            elif any(word in message_text for word in ['помощь', 'help', '?', 'команды']):
                reply = "ℹ️ Доступные команды:\n\n🎫 'заказ' - забронировать круиз\n💰 'цены' - узнать стоимость\n🚢 'круизы' - посмотреть маршруты\n📞 'контакты' - связаться с нами\n👋 'привет' - приветствие\n\n💡 Просто напишите ключевое слово!"
            
            else:
                reply = f"Спасибо за сообщение, {user_name}! 📨\n\nВаш запрос: '{original_text}'\n\n🤖 Я обработал ваше сообщение. Для быстрой помощи используйте команды:\n• 'заказ' - оформить бронирование\n• 'цены' - узнать стоимость\n• 'круизы' - посмотреть маршруты\n\n📞 Срочные вопросы: +7 (800) 555-35-35"
            
            # Отправка в отдельном потоке
            thread = threading.Thread(target=send_message_thread, args=(chat_id, reply))
            thread.daemon = True
            thread.start()
            
    except Exception as e:
        print(f"Webhook error: {e}")
    
    return 'ok', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)