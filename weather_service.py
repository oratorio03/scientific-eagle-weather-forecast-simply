import json
import os
import requests
import datetime
from config import OPEN_METEO_URL, CACHE_FILE

class WeatherService:
    def __init__(self):
        self.cached_data = None
        self.is_offline = False

    def fetch_weather(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,is_day,precipitation,weather_code,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,relative_humidity_2m,uv_index",
            "hourly": "temperature_2m,precipitation_probability,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }

        try:
            response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                data['timestamp'] = datetime.datetime.now().isoformat()
                self._save_cache(data)
                self.cached_data = data
                self.is_offline = False
                return data, False
            else:
                return self._load_cache(), True
        except Exception as e:
            print(f"Network error fetching weather: {e}")
            return self._load_cache(), True

    def _save_cache(self, data):
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")

    def _load_cache(self):
        self.is_offline = True
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cached_data = json.load(f)
                    return self.cached_data
            except Exception as e:
                print(f"Error loading cache: {e}")
        return None
