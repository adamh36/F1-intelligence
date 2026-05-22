import os
import requests
from dotenv import load_dotenv

load_dotenv('.env.local')

API_KEY = os.getenv('OPENWEATHER_API_KEY')

# circuit coordinates keyed by circuit name (lowercase)
CIRCUITS = {
    'montreal': (45.5017, -73.5673),
    'silverstone': (52.0786, -1.0169),
    'monaco': (43.7347, 7.4206),
    'monza': (45.6156, 9.2811),
    'spa': (50.4372, 5.9714),
    'bahrain': (26.0325, 50.5106),
    'jeddah': (21.6319, 39.1044),
    'melbourne': (-37.8497, 144.9680),
    'baku': (40.3725, 49.8533),
    'miami': (25.9581, -80.2389),
    'barcelona': (41.5700, 2.2611),
    'spielberg': (47.2197, 14.7647),
    'budapest': (47.5789, 19.2486),
    'zandvoort': (52.3888, 4.5409),
    'singapore': (1.2914, 103.8640),
    'suzuka': (34.8431, 136.5407),
    'austin': (30.1328, -97.6411),
    'mexico city': (19.4042, -99.0907),
    'sao paulo': (-23.7036, -46.6997),
    'las vegas': (36.1147, -115.1728),
    'abu dhabi': (24.4672, 54.6031),
    'shanghai': (31.3389, 121.2197),
    'imola': (44.3439, 11.7167),
}


def get_weather(circuit_name: str) -> str:
    """Fetch current weather and 5-day forecast for a given F1 circuit."""

    key = circuit_name.lower()
    if key not in CIRCUITS:
        return f"Circuit '{circuit_name}' not found. Available: {', '.join(CIRCUITS.keys())}"

    lat, lon = CIRCUITS[key]

    # current weather
    current_url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )
    current = requests.get(current_url).json()

    temp = current['main']['temp']
    feels_like = current['main']['feels_like']
    humidity = current['main']['humidity']
    description = current['weather'][0]['description'].capitalize()
    wind_speed = current['wind']['speed']
    rain = current.get('rain', {}).get('1h', 0)

    # 5-day forecast (3-hour intervals)
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&cnt=8"
    )
    forecast_data = requests.get(forecast_url).json()

    forecast_lines = []
    for entry in forecast_data['list']:
        time = entry['dt_txt']
        t = entry['main']['temp']
        desc = entry['weather'][0]['description'].capitalize()
        rain_chance = entry.get('pop', 0) * 100
        forecast_lines.append(f"  {time} | {t}°C | {desc} | Rain: {rain_chance:.0f}%")

    forecast_str = "\n".join(forecast_lines)

    return (
        f"Weather at {circuit_name.title()} Circuit\n\n"
        f"Current: {description} | {temp}°C (feels like {feels_like}°C)\n"
        f"Humidity: {humidity}% | Wind: {wind_speed} m/s | Rain (last 1h): {rain}mm\n\n"
        f"Forecast (next 24h):\n{forecast_str}"
    )
