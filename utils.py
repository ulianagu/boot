import random
import requests
from config import OPENWEATHER_API,FOURSQUARE_API,OPENTRIPMAP_API

def get_weather_data(lat, lon):
    """Получаем данные о погоде и UV-индексе"""
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API}"
    uv_url = f"http://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={OPENWEATHER_API}"
    
    weather = requests.get(weather_url).json()
    uv_index = requests.get(uv_url).json().get('value', 0)
    
    return {
        'temp': weather['main']['temp'],
        'feels_like': weather['main']['feels_like'],
        'humidity': weather['main']['humidity'],
        'wind': weather['wind']['speed'] if 'wind' in weather else 0,
        'uv': uv_index,
        'weather': weather['weather'][0]['main'].lower()
    }

def generate_outfit_recommendation(weather_data):
    """Генерируем рекомендации по одежде с детализацией"""
    temp = weather_data['temp']
    uv = weather_data['uv']
    weather = weather_data['weather']
    wind_speed = weather_data.get('wind', 0)
    humidity = weather_data['humidity']

    recommendations = []
    accessories = []
    footwear = []
    layers = []

    
    if temp < -10:
        recommendations.append(random.choice([
            "❄️ Термобельё + утепленный зимний комбинезон",
            "❄️ Пуховик с меховой отделкой + флисовая поддева"
        ]))
        footwear.append("🥾 Утепленные зимние ботинки (UGG, Sorel)")
        accessories.append("🧤 Варежки с подкладкой, балаклава")
        
    elif -10 <= temp < 0:
        recommendations.append(random.choice([
            "🧥 Теплое пальто + шерстяной свитер + термолеггинсы",
            "🧥 Пуховая куртка + кашемировый джемпер"
        ]))
        footwear.append("👢 Утепленные ботинки на толстой подошве")
        accessories.append("🧣 Шерстяной шарф и перчатки")
        
    elif 0 <= temp < 10:
        layers.append(random.choice([
            "🧥 Тренчкот + водолазка + утепленные брюки",
            "🧥 Дубленка + толстовка + джинсы"
        ]))
        footwear.append(random.choice([
            "👞 Кожаные ботинки", 
            "👢 Челси с подкладкой"
        ]))
        if wind_speed > 10:
            accessories.append("🧣 Шелковый подшлемник")
            
    elif 10 <= temp < 15:
        layers.append(random.choice([
            "🧥 Весеннее пальто + рубашка + кардиган",
            "🧥 Кожаная куртка + худи + джинсы"
        ]))
        footwear.append(random.choice([
            "👟 Кроссовки", 
            "🥾 Ботильоны"
        ]))
        if humidity > 80:
            accessories.append("🌂 Складной зонт-трость")
            
    elif 15 <= temp < 20:
        recommendations.append(random.choice([
            "👔 Рубашка/блузка + легкий жакет",
            "🧶 Джинсовая куртка + футболка + шорты"
        ]))
        footwear.append(random.choice([
            "👡 Сандалии", 
            "👞 Лоферы"
        ]))
        
    elif 20 <= temp < 25:
        recommendations.append(random.choice([
            "👕 Хлопковая рубашка с коротким рукавом + чиносы",
            "👗 Сарафан/легкое платье + джинсовка"
        ]))
        footwear.append("👟 Мокасины или эспадрильи")
        
    else:  
        recommendations.append(random.choice([
            "🩳 Шорты + майка/топ из льна",
            "👗 Легкое льняное платье"
        ]))
        footwear.append("👡 Пляжные сандалии или вьетнамки")

    
    if 'rain' in weather:
        recommendations.append("☔ Непромокаемая ветровка с капюшоном")
        footwear.append("🌧️ Резиновые сапоги/водонепроницаемые кроссовки")
        accessories.append("Зонт-автомат компактного размера")
        
    elif 'snow' in weather:
        recommendations.append("⛄ Пуховые штаны поверх термобелья")
        footwear.append("❄️ Сноубутсы с шипами")
        accessories.append("Снегоступы для прогулок")
        
    if wind_speed > 15:
        accessories.append(random.choice([
            "🎀 Ветрозащитная маска", 
            "🪁 Плотно прилегающая шапка"
        ]))
        
    if uv > 5:
        accessories.append(random.choice([
            "🧢 Кепка с UV-защитой", 
            "👒 Соломенная шляпа с широкими полями"
        ]))

   
    if 5 <= temp <= 18:
        layers.append("🧥 Многослойность: футболка + рубашка + легкая куртка")

    
    spf_advice = []
    if uv >= 1:
        spf_level = min(50, 10 + uv*5)
        spf_text = {
            1: f"SPF 15+ (легкий дневной крем)",
            3: f"SPF {spf_level}+ каждые 2 часа",
            6: f"SPF {spf_level}+ водостойкий + шлята",
            8: f"SPF {spf_level}+ полный UV-блок"
        }.get(uv // 1, f"SPF {spf_level}+")
        
        spf_advice.append(f"🧴 {spf_text}")
        if uv > 3:
            spf_advice.append("🕶️ UV400 защитные очки")

    
    full_advice = []
    if recommendations: full_advice.append("• " + "\n• ".join(recommendations))
    if layers: full_advice.append("\n🔸 Слои:\n• " + "\n• ".join(layers))
    if footwear: full_advice.append("\n👟 Обувь:\n• " + "\n• ".join(footwear))
    if accessories: full_advice.append("\n🧣 Аксессуары:\n• " + "\n• ".join(accessories))

    return {
        'clothes': "\n".join(full_advice) if any(full_advice) else "👕 Стандартный комплект",
        'spf': "\n".join(spf_advice) if spf_advice else "SPF не требуется 🌥️"
    }

def get_city_coords(city):
    """Получаем координаты города"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API}"
    response = requests.get(url).json()
    return response[0]['lat'], response[0]['lon'] if response else None

def get_place_photo(xid):
    """Получаем фото места"""
    response = requests.get(f"https://api.opentripmap.com/0.1/ru/places/xid/{xid}?apikey={OPENTRIPMAP_API}").json()
    return response.get('preview', {}).get('source')
