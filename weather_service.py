import requests
import config

def get_weather(lat=None, lon=None, city=None):
    """
    Fetches the current weather using Coordinates or City name.
    """
    if lat and lon:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={config.API_KEY}&units={config.UNITS}&lang=id"
    else:
        target_city = city if city else config.CITY
        url = f"http://api.openweathermap.org/data/2.5/weather?q={target_city}&appid={config.API_KEY}&units={config.UNITS}&lang=id"
    
    try:
        response = requests.get(url, timeout=10)
        # If not found or error, fallback to Jakarta if not already there
        if response.status_code != 200:
            if not lat and city != "Jakarta,ID":
                return get_weather(city="Jakarta,ID")
            
        response.raise_for_status()
        data = response.json()
        
        weather_info = {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].title(),
            "icon_code": data["weather"][0]["icon"],
            "city": data["name"]
        }
        return weather_info
    except Exception as e:
        print(f"Error fetching weather: {e}")
        if not lat and city != "Jakarta,ID":
            return get_weather(city="Jakarta,ID")
        return None

if __name__ == "__main__":
    # Test the service
    print(get_weather(lat=config.LAT, lon=config.LON))
