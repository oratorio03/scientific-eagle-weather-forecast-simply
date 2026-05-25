import json
import os
import requests
import time
from plyer import gps
from config import NOMINATIM_URL, GEOCODE_CACHE_FILE, NOMINATIM_MAP_CACHE_FILE, DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY, NOMINATIM_RATE_LIMIT

class GPSService:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.city_name = None
        self.gps_active = False
        self.last_geocode_time = 0
        self.geocode_cache = self._load_geocode_cache()
        self.map_geocode_cache = self._load_map_geocode_cache()

    def start_gps(self, on_location_update, on_status_change=None):
        try:
            gps.configure(on_location=on_location_update, on_status=on_status_change)
            gps.start(minTime=300000, minDistance=100) # 5 min or 100m
            self.gps_active = True
        except NotImplementedError:
            print("GPS not supported on this platform. Using default/fallback.")
            self.lat = DEFAULT_LAT
            self.lon = DEFAULT_LON
            self.gps_active = False
            on_location_update(lat=self.lat, lon=self.lon)

    def stop_gps(self):
        if self.gps_active:
            try:
                gps.stop()
                self.gps_active = False
            except Exception:
                pass

    def _load_geocode_cache(self):
        if os.path.exists(GEOCODE_CACHE_FILE):
            try:
                with open(GEOCODE_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_geocode_cache(self):
        try:
            with open(GEOCODE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get_city_name(self, lat, lon):
        # Round coords slightly to increase cache hit rate and avoid rate limits
        cache_key = f"{round(lat, 3)},{round(lon, 3)}"

        if cache_key in self.geocode_cache:
            return self.geocode_cache[cache_key]

        # Rate limiting Nominatim
        current_time = time.time()
        time_since_last = current_time - self.last_geocode_time
        if time_since_last < NOMINATIM_RATE_LIMIT:
            time.sleep(NOMINATIM_RATE_LIMIT - time_since_last)

        try:
            headers = {'User-Agent': 'SkyViewWeatherApp/1.0'}
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'zoom': 10, # city level
                'addressdetails': 1
            }
            response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
            self.last_geocode_time = time.time()

            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                city = address.get('city') or address.get('town') or address.get('village') or address.get('county') or DEFAULT_CITY

                self.geocode_cache[cache_key] = city
                self._save_geocode_cache()
                return city
        except Exception as e:
            print(f"Error reverse geocoding: {e}")

        return DEFAULT_CITY

    def _load_map_geocode_cache(self):
        if os.path.exists(NOMINATIM_MAP_CACHE_FILE):
            try:
                with open(NOMINATIM_MAP_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_map_geocode_cache(self):
        try:
            with open(NOMINATIM_MAP_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.map_geocode_cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def reverse_geocode(self, lat, lon):
        """Used by the map screen to get a specific point's location name."""
        cache_key = f"{round(lat, 4)},{round(lon, 4)}"

        if cache_key in self.map_geocode_cache:
            return self.map_geocode_cache[cache_key]

        current_time = time.time()
        time_since_last = current_time - self.last_geocode_time
        if time_since_last < NOMINATIM_RATE_LIMIT:
            time.sleep(NOMINATIM_RATE_LIMIT - time_since_last)

        try:
            headers = {'User-Agent': 'SkyView/1.0'}
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'zoom': 14, # more specific zoom for points
                'addressdetails': 1
            }
            response = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=5)
            self.last_geocode_time = time.time()

            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})

                # Build a more specific name for the map point
                name_parts = []
                if 'road' in address: name_parts.append(address['road'])
                elif 'neighbourhood' in address: name_parts.append(address['neighbourhood'])

                city = address.get('city') or address.get('town') or address.get('village') or address.get('county')
                if city: name_parts.append(city)

                name = ", ".join(name_parts) if name_parts else "Posizione Sconosciuta"

                self.map_geocode_cache[cache_key] = name
                self._save_map_geocode_cache()
                return name
        except Exception as e:
            print(f"Error reverse geocoding map point: {e}")

        return "Posizione Sconosciuta"
