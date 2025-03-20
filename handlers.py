from telebot import types
from database import save_walk, get_walks_by_city, get_user_walks, delete_walk
from utils import get_weather_data, generate_outfit_recommendation, get_city_coords, get_place_photo
from config import OPENWEATHER_API,FOURSQUARE_API,OPENTRIPMAP_API
import requests
import sqlite3
from datetime import datetime
from transformers import pipeline
from googletrans import Translator

DB_NAME = 'walks6.db'
classifier = pipeline("text-classification", model="models/unitary-toxic-bert")
translator = Translator()

def register_handlers(bot):

    @bot.message_handler(commands=['start_walk'])
    def start_walk(message):
        msg = bot.send_message(message.chat.id, "В каком городе хотите погулять?")
        bot.register_next_step_handler(msg, process_city_step)
    
    def process_city_step(message):
        city = message.text.strip()
        msg = bot.send_message(message.chat.id, "Напишите ваше пожелание к попутчику:")

        bot.register_next_step_handler(msg, process_text_step, city)

    def process_text_step(message, city):
        user_text = message.text.strip()

        translated_text = translator.translate(user_text, src='ru', dest='en').text
        toxicity_result = classifier(translated_text)[0]
        
        if toxicity_result['label'] == 'toxic' and toxicity_result['score'] > 0.8:
            bot.send_message(
                message.chat.id, 
                "⚠️ Вы признаны токсиком. Пожалуйста, повторите заявку снова"
            )
            return  
        
       
        username = message.from_user.username or "не указан"  
        save_walk(message.from_user.id, username, city, user_text)
        bot.send_message(
            message.chat.id, 
            f"✅ Заявка создана!\nГород: {city}\nВаш текст: {user_text}"
        )




    def save_walk(user_id, username, city, text):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO walks (user_id, username, city, text, timestamp) VALUES (?, ?, ?, ?, ?)",
                (user_id, username, city.lower(), text, datetime.now()))
        conn.commit()
        conn.close()

 
    def get_walks_by_city(city):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM walks WHERE city = ? ORDER BY timestamp DESC", (city,))
        result = c.fetchall()
        conn.close()
        return result

    def create_custom_keyboard():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  
        btn_help = types.KeyboardButton("/help")  
        markup.add(btn_help)  
        return markup

    
    @bot.message_handler(commands=['start'])
    def start_command(message):
        
        welcome_text = "Привет! Я бот для организации прогулок. Используй команду /help, чтобы узнать больше."
        
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=create_custom_keyboard())

    
    @bot.message_handler(commands=['help'])
    def help_command(message):
       
        help_text = """
    📋 Список доступных команд:

    /start_walk — создать заявку на прогулку.
    /show_walks — посмотреть заявки.
    /delete_walk — удалить свою заявку.
    /explore <город> — найти достопримечательности.
    /food <город> — найти рестораны.
    /outfit <город> — получить рекомендации по одежде.
        """
        
        
        bot.send_message(message.chat.id, help_text, reply_markup=create_custom_keyboard())

    @bot.message_handler(commands=['show_walks'])
    def show_walks(message):
        try:
            
            city = message.text.split(' ', 1)[1].strip().lower()
        except IndexError:
            
            bot.reply_to(message, "Пожалуйста, укажите город. Например: /show_walks Москва")
            return

        
        process_show_walks(message, city)

    def process_show_walks(message, city):
        walks = get_walks_by_city(city)
        if walks:
            response = [f"🏙️ <b>{city.capitalize()}</b> - активные заявки:\n"]
            for walk in walks:
                
                if len(walk) >= 6:
                    username = walk[2]  
                    response.append(
                        f"\n👤 Заявка #{walk[0]}\n"
                        f"📝 {walk[4]}\n"
                        f"🕒 {walk[5]}\n"
                        f"👤 Пользователь: @{username if username else 'не указан'}"
                    )
                else:
                    
                    response.append("\n⚠️ Ошибка: некорректные данные в заявке.")
            bot.send_message(message.chat.id, "\n".join(response), parse_mode='HTML')
        else:
            bot.send_message(message.chat.id, f"В городе {city} пока нет активных заявок.")


    
    @bot.message_handler(commands=['delete_walk'])
    def delete_walk_handler(message):
        user_id = message.from_user.id
        walks = get_user_walks(user_id)
        
        if walks:
            markup = types.InlineKeyboardMarkup()
            for walk in walks:
                
                btn = types.InlineKeyboardButton(f"❌ #{walk[0]} - {walk[2]}", callback_data=f"delete_{walk[0]}")
                markup.add(btn)
            
            
            bot.send_message(message.chat.id, "Выберите заявку для удаления:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет активных заявок.")

    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("delete_"))
    def handle_delete_callback(call):
        
        walk_id = int(call.data.split("_")[1])
        
        
        delete_walk(walk_id)
        
        
        bot.answer_callback_query(call.id, f"Заявка #{walk_id} удалена.")
        
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Заявка #{walk_id} удалена."
        )

    
    @bot.message_handler(commands=['explore'])
    def handle_explore(message):
        """Ищем достопримечательности в городе."""
        try:
            city = message.text.split(' ', 1)[1]
            coords = get_city_coords(city)
            if not coords:
                return bot.reply_to(message, "Город не найден 🧐")
            
            url = f"https://api.opentripmap.com/0.1/ru/places/radius?radius=10000&lon={coords[1]}&lat={coords[0]}&apikey={OPENTRIPMAP_API}&format=json"
            response = requests.get(url).json()
            
            
            if not response:
                return bot.reply_to(message, "Ничего не найдено 😔")
            
            # Топ-5 мест
            for place in response[:5]:
                name = place.get('name', 'Без названия')
                desc = place.get('kinds', 'Описание отсутствует')
                photo_url = get_place_photo(place.get('xid'))
                
                caption = f"🏛 <b>{name}</b>\n\n{desc}"
                if photo_url:
                    bot.send_photo(message.chat.id, photo_url, caption=caption, parse_mode='HTML')
                else:
                    bot.send_message(message.chat.id, caption, parse_mode='HTML')
                    
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")

    
    @bot.message_handler(commands=['food'])
    def handle_food(message):
        try:
            city = message.text.split(' ', 1)[1]
            headers = {
                "Authorization": FOURSQUARE_API,
                "accept": "application/json"
            }
            response = requests.get(
                f"https://api.foursquare.com/v3/places/search?near={city}&categories=13000&limit=5",
                headers=headers
            ).json()
            
            for place in response.get('results', [])[:5]:
                text = f"🍴 <b>{place.get('name')}</b>\n⭐ Рейтинг: {place.get('rating', '?')}\n📍 Адрес: {place['location'].get('formatted_address', 'Нет адреса')}"
                bot.send_message(message.chat.id, text, parse_mode='HTML')
                
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")

    
    @bot.message_handler(commands=['outfit'])
    def handle_outfit(message):
        """Рекомендации что надеть"""
        try:
            city = message.text.split(' ', 1)[1]
            coords = get_city_coords(city)
            if not coords:
                return bot.reply_to(message, "Город не найден 🧐")
            
            weather = get_weather_data(*coords)
            outfit = generate_outfit_recommendation(weather)
            
            response = (
                f"🌡️ Погода в {city}: {weather['temp']}°C (ощущается как {weather['feels_like']}°C)\n"
                f"☀️ UV индекс: {weather['uv']:.1f}\n\n"
                f"👗 <b>Рекомендации по одежде:</b>\n{outfit['clothes']}\n\n"
                f"🧴 <b>Защита от солнца:</b>\n{outfit['spf']}"
            )
            
            bot.reply_to(message, response, parse_mode='HTML')
            
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")
