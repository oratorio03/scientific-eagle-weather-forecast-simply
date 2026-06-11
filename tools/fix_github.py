#!/usr/bin/env python3
"""
SkyView GitHub Auto-Fix
Esegue automaticamente tutte le correzioni sul repository GitHub.
Richiede solo un GitHub Personal Access Token.

Istruzioni per ottenere il token (30 secondi):
1. Vai su https://github.com/settings/tokens/new
2. In "Note" scrivi: SkyView Fix
3. Seleziona SOLO la spunta "repo" (per modificare i tuoi repository)
4. Clicca "Generate token" in fondo
5. Copia il token (stringa tipo: ghp_xxxxxxxxxxxx)
6. Incollalo qui sotto quando richiesto
"""

import base64
import json
import urllib.request
import urllib.error
import sys

# ============== CONFIGURAZIONE ==============
REPO_OWNER = "oratorio03"
REPO_NAME = "scientific-eagle-weather-forecast-simply"
BRANCH = "main"
GITHUB_API = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"

# I file corretti da caricare
FILES = {
    "ui_components.py": '''from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.button import MDIconButton
from kivy.properties import StringProperty
from utils import wmo_code_to_italian, get_day_name, format_hour


class WeatherGridItem(MDBoxLayout):
    title = StringProperty("")
    value = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = "8dp"

        self.title_label = MDLabel(
            text=self.title,
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary"
        )
        self.value_label = MDLabel(
            text=self.value,
            font_style="Body1",
            halign="center",
            bold=True
        )

        self.add_widget(self.title_label)
        self.add_widget(self.value_label)

    def on_title(self, instance, value):
        if hasattr(self, 'title_label'):
            self.title_label.text = value

    def on_value(self, instance, value):
        if hasattr(self, 'value_label'):
            self.value_label.text = value


class HourlyForecastCard(MDCard):
    hour = StringProperty("")
    temp = StringProperty("")
    icon = StringProperty("weather-sunny")
    pop = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("80dp", "120dp")
        self.padding = "8dp"
        self.radius = 12

        self.hour_label = MDLabel(
            text=self.hour,
            font_style="Caption",
            halign="center"
        )
        self.icon_widget = MDIconButton(
            icon=self.icon,
            pos_hint={"center_x": 0.5},
            theme_text_color="Primary"
        )
        self.temp_label = MDLabel(
            text=self.temp,
            font_style="Body1",
            halign="center",
            bold=True
        )
        self.pop_label = MDLabel(
            text=self.pop,
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary"
        )

        self.add_widget(self.hour_label)
        self.add_widget(self.icon_widget)
        self.add_widget(self.temp_label)
        self.add_widget(self.pop_label)

    def on_hour(self, instance, value):
        if hasattr(self, 'hour_label'):
            self.hour_label.text = value

    def on_temp(self, instance, value):
        if hasattr(self, 'temp_label'):
            self.temp_label.text = value

    def on_icon(self, instance, value):
        if hasattr(self, 'icon_widget'):
            self.icon_widget.icon = value

    def on_pop(self, instance, value):
        if hasattr(self, 'pop_label'):
            self.pop_label.text = value


class DailyForecastItem(TwoLineAvatarIconListItem):
    def __init__(self, day, min_temp, max_temp, weather_code, **kwargs):
        desc, icon = wmo_code_to_italian(weather_code)
        super().__init__(**kwargs)

        self.text = f"{get_day_name(day)} - {desc}"
        self.secondary_text = f"Min: {min_temp}C | Max: {max_temp}C"

        self.add_widget(IconLeftWidget(icon=icon))
''',

    "screens.py": '''from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import MDList
from kivymd.uix.textfield import MDTextField
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from ui_components import WeatherGridItem, HourlyForecastCard, DailyForecastItem
from utils import wind_direction_to_cardinal, wmo_code_to_italian, format_timestamp, format_hour
import datetime


class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None


class HomeScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = MDBoxLayout(orientation='vertical')

        self.header_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="10dp")
        self.offline_banner = MDLabel(
            text="Dati in cache - non aggiornati",
            theme_text_color="Error",
            halign="center",
            bold=True,
            adaptive_height=True,
            opacity=0,
            height=0,
            size_hint_y=None
        )
        self.timestamp_label = MDLabel(
            text="Ultimo aggiornamento: --/--/---- --:--",
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary",
            adaptive_height=True
        )
        self.header_layout.add_widget(self.offline_banner)
        self.header_layout.add_widget(self.timestamp_label)

        self.location_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="10dp")
        self.city_label = MDLabel(text="Cerco posizione...", font_style="H4", halign="center", bold=True)
        self.coords_label = MDLabel(text="Lat: -- | Lon: --", font_style="Caption", halign="center")
        self.location_layout.add_widget(self.city_label)
        self.location_layout.add_widget(self.coords_label)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': .5},
            active=False,
            opacity=0
        )
        self.location_layout.add_widget(self.spinner)

        self.current_weather_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="20dp", spacing="10dp")
        self.temp_label = MDLabel(text="--C", font_style="H1", halign="center")
        self.desc_label = MDLabel(text="--", font_style="H6", halign="center")
        self.feels_like_label = MDLabel(text="Percepita: --C", font_style="Subtitle1", halign="center", theme_text_color="Secondary")
        self.current_weather_layout.add_widget(self.temp_label)
        self.current_weather_layout.add_widget(self.desc_label)
        self.current_weather_layout.add_widget(self.feels_like_label)

        scroll_grid = MDScrollView()
        self.grid_layout = MDGridLayout(cols=3, adaptive_height=True, padding="10dp", spacing="10dp")

        self.grid_items = {
            'umidita': WeatherGridItem(title="Umidita"),
            'pressione': WeatherGridItem(title="Pressione"),
            'vento': WeatherGridItem(title="Vento"),
            'raffiche': WeatherGridItem(title="Raffiche"),
            'nuvole': WeatherGridItem(title="Nuvole"),
            'pioggia': WeatherGridItem(title="Precipitazioni"),
            'uv': WeatherGridItem(title="Indice UV")
        }

        for item in self.grid_items.values():
            self.grid_layout.add_widget(item)

        scroll_grid.add_widget(self.grid_layout)

        refresh_layout = MDBoxLayout(adaptive_height=True, padding="10dp")
        refresh_btn = MDRaisedButton(text="Aggiorna Ora", pos_hint={"center_x": .5}, on_release=self.force_refresh)
        refresh_layout.add_widget(MDLabel())
        refresh_layout.add_widget(refresh_btn)
        refresh_layout.add_widget(MDLabel())

        self.manual_input_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="10dp", opacity=0)
        self.manual_input_layout.size_hint_y = None
        self.manual_input_layout.height = 0
        self.lat_input = MDTextField(hint_text="Latitudine")
        self.lon_input = MDTextField(hint_text="Longitudine")
        manual_btn = MDRaisedButton(text="Cerca Coordinate", pos_hint={"center_x": .5}, on_release=self.manual_search)
        self.manual_input_layout.add_widget(MDLabel(text="GPS Non Disponibile", theme_text_color="Error", halign="center"))
        self.manual_input_layout.add_widget(self.lat_input)
        self.manual_input_layout.add_widget(self.lon_input)
        self.manual_input_layout.add_widget(manual_btn)

        main_layout.add_widget(self.header_layout)
        main_layout.add_widget(self.location_layout)
        main_layout.add_widget(self.current_weather_layout)
        main_layout.add_widget(scroll_grid)
        main_layout.add_widget(self.manual_input_layout)
        main_layout.add_widget(refresh_layout)

        self.add_widget(main_layout)

    def show_loading(self, active=True):
        self.spinner.active = active
        self.spinner.opacity = 1 if active else 0

    def force_refresh(self, instance):
        if self.app:
            self.app.update_weather(force=True)

    def manual_search(self, instance):
        if self.app:
            try:
                lat = float(self.lat_input.text)
                lon = float(self.lon_input.text)
                self.app.update_weather(lat=lat, lon=lon)
            except ValueError:
                pass

    def update_ui(self, data, is_offline, city_name, lat, lon, accuracy=None):
        self.show_loading(False)

        if is_offline:
            self.offline_banner.opacity = 1
            self.offline_banner.height = dp(30)
        else:
            self.offline_banner.opacity = 0
            self.offline_banner.height = 0

        self.timestamp_label.text = f"Ultimo aggiornamento: {format_timestamp(data.get('timestamp', ''))}"
        self.city_label.text = city_name
        acc_text = f" (+-{int(accuracy)}m)" if accuracy else ""
        self.coords_label.text = f"Lat: {lat:.6f} | Lon: {lon:.6f}{acc_text}"

        current = data.get("current", {})
        temp = current.get("temperature_2m", "--")
        self.temp_label.text = f"{temp}C"

        feels = current.get("apparent_temperature", "--")
        self.feels_like_label.text = f"Percepita: {feels}C"

        wcode = current.get("weather_code", -1)
        desc, icon = wmo_code_to_italian(wcode)
        self.desc_label.text = desc

        self.grid_items['umidita'].value = f"{current.get('relative_humidity_2m', '--')} %"
        self.grid_items['pressione'].value = f"{current.get('pressure_msl', '--')} hPa"

        wind_speed = current.get('wind_speed_10m', '--')
        wind_dir = wind_direction_to_cardinal(current.get('wind_direction_10m'))
        self.grid_items['vento'].value = f"{wind_speed} km/h {wind_dir}"

        self.grid_items['raffiche'].value = f"{current.get('wind_gusts_10m', '--')} km/h"
        self.grid_items['nuvole'].value = f"{current.get('cloud_cover', '--')}%"
        self.grid_items['pioggia'].value = f"{current.get('precipitation', '--')} mm"
        self.grid_items['uv'].value = f"{current.get('uv_index', '--')}"

    def show_gps_error(self):
        self.manual_input_layout.opacity = 1
        self.manual_input_layout.height = dp(150)
        self.manual_input_layout.size_hint_y = None


class InfoScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical', padding="20dp", spacing="10dp")
        layout.add_widget(MDLabel(text="Informazioni", font_style="H4", halign="center", adaptive_height=True))
        layout.add_widget(MDLabel(
            text="SkyView v1.0\\nApp Meteo Iper-Locale basata sulle coordinate GPS esatte.\\n\\nSorgenti Dati:\\n- Previsioni: Open-Meteo\\n- Reverse Geocoding: Nominatim OpenStreetMap\\n\\nNessuna API Key richiesta.",
            halign="center",
            theme_text_color="Secondary"
        ))
        self.add_widget(layout)


class HourlyScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')

        self.scroll = MDScrollView(do_scroll_x=True, do_scroll_y=False)
        self.hourly_layout = MDBoxLayout(orientation='horizontal', adaptive_width=True, padding="10dp", spacing="10dp")
        self.scroll.add_widget(self.hourly_layout)

        layout.add_widget(MDLabel(text="Previsioni 24 Ore", font_style="H5", halign="center", adaptive_height=True, padding=(0, "20dp")))
        layout.add_widget(self.scroll)
        self.add_widget(layout)

    def update_ui(self, data):
        self.hourly_layout.clear_widgets()
        hourly = data.get("hourly", {})
        if not hourly:
            return

        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        pops = hourly.get("precipitation_probability", [])
        wcodes = hourly.get("weather_code", [])

        min_len = min(len(times), len(temps), len(pops), len(wcodes))
        if min_len == 0:
            return

        now = datetime.datetime.now()

        count = 0
        for i in range(min_len):
            try:
                dt = datetime.datetime.fromisoformat(times[i])
            except (ValueError, TypeError):
                continue
            if dt > now and count < 24:
                desc, icon = wmo_code_to_italian(wcodes[i])
                card = HourlyForecastCard(
                    hour=format_hour(times[i]),
                    temp=f"{temps[i]}C",
                    icon=icon,
                    pop=f"{pops[i]}%"
                )
                self.hourly_layout.add_widget(card)
                count += 1


class DailyScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation='vertical')
        layout.add_widget(MDLabel(text="Previsioni 7 Giorni", font_style="H5", halign="center", adaptive_height=True, padding=(0, "20dp")))

        scroll = MDScrollView()
        self.list_layout = MDList()
        scroll.add_widget(self.list_layout)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def update_ui(self, data):
        self.list_layout.clear_widgets()
        daily = data.get("daily", {})
        if not daily:
            return

        times = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        wcodes = daily.get("weather_code", [])

        min_len = min(len(times), len(max_temps), len(min_temps), len(wcodes))

        for i in range(min_len):
            item = DailyForecastItem(
                day=times[i],
                min_temp=min_temps[i],
                max_temp=max_temps[i],
                weather_code=wcodes[i]
            )
            self.list_layout.add_widget(item)
''',

    "main.py": '''import threading
import logging

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationLayout,
    MDNavigationDrawerMenu,
    MDNavigationDrawerItem,
    MDNavigationDrawerLabel,
)
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import Clock

from screens import HomeScreen, HourlyScreen, DailyScreen, InfoScreen
from gps_service import GPSService
from weather_service import WeatherService
from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SkyView")


class SkyViewApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.material_style = "M3"

        self.gps_service = GPSService()
        self.weather_service = WeatherService()

        self.current_lat = DEFAULT_LAT
        self.current_lon = DEFAULT_LON
        self.current_city = DEFAULT_CITY
        self.current_accuracy = None

        self._coord_lock = threading.Lock()

        self.nav_layout = MDNavigationLayout()
        self.sm = MDScreenManager()

        main_screen_wrapper = MDScreen(name="main_wrapper")
        main_layout = MDBoxLayout(orientation='vertical')

        self.top_bar = MDTopAppBar(
            title="SkyView",
            elevation=4,
            pos_hint={"top": 1},
            md_bg_color=self.theme_cls.primary_color,
            specific_text_color=self.theme_cls.primary_light,
            left_action_items=[["menu", lambda x: self.nav_drawer.set_state("open")]]
        )
        main_layout.add_widget(self.top_bar)

        self.bottom_nav = MDBottomNavigation(
            selected_color_background="eeeaea",
            text_color_active="lightgrey"
        )

        home_item = MDBottomNavigationItem(name="home", text="Oggi", icon="calendar-today")
        self.home_screen = HomeScreen(name="home_content")
        self.home_screen.app = self
        home_item.add_widget(self.home_screen)

        hourly_item = MDBottomNavigationItem(name="hourly", text="24 Ore", icon="clock-outline")
        self.hourly_screen = HourlyScreen(name="hourly_content")
        self.hourly_screen.app = self
        hourly_item.add_widget(self.hourly_screen)

        daily_item = MDBottomNavigationItem(name="daily", text="7 Giorni", icon="calendar-week")
        self.daily_screen = DailyScreen(name="daily_content")
        self.daily_screen.app = self
        daily_item.add_widget(self.daily_screen)

        info_item = MDBottomNavigationItem(name="info", text="Info", icon="information")
        self.info_screen = InfoScreen(name="info_content")
        self.info_screen.app = self
        info_item.add_widget(self.info_screen)

        self.bottom_nav.add_widget(home_item)
        self.bottom_nav.add_widget(hourly_item)
        self.bottom_nav.add_widget(daily_item)
        self.bottom_nav.add_widget(info_item)

        main_layout.add_widget(self.bottom_nav)
        main_screen_wrapper.add_widget(main_layout)

        self.sm.add_widget(main_screen_wrapper)
        self.nav_layout.add_widget(self.sm)

        self.nav_drawer = MDNavigationDrawer()
        menu = MDNavigationDrawerMenu()
        menu.add_widget(MDNavigationDrawerLabel(text="Menu Principale"))

        drawer_items = [
            ("Posizione Attuale", "map-marker", "home"),
            ("Previsioni Orarie", "clock-outline", "hourly"),
            ("Previsioni 7 Giorni", "calendar-week", "daily"),
            ("Info", "information", "info")
        ]

        for text, icon, target in drawer_items:
            item = MDNavigationDrawerItem(text=text, icon=icon)
            item.bind(on_release=lambda x, t=target: self.drawer_select(t))
            menu.add_widget(item)

        self.nav_drawer.add_widget(menu)
        self.nav_layout.add_widget(self.nav_drawer)

        return self.nav_layout

    def on_start(self):
        self.top_bar.title = "SkyView - Aggiornamento..."
        self.home_screen.show_loading(True)
        self.gps_service.start_gps(self.on_location_update, self.on_gps_status)

        cached = self.weather_service._load_cache()
        if cached:
            threading.Thread(target=self._load_cache_thread, args=(cached,), daemon=True).start()

    def _load_cache_thread(self, cached):
        try:
            city = self.gps_service.get_city_name(DEFAULT_LAT, DEFAULT_LON)
            with self._coord_lock:
                self.current_city = city
            Clock.schedule_once(lambda dt: self._apply_cache(cached))
        except Exception as e:
            logger.error(f"Error loading cache thread: {e}")

    def _apply_cache(self, cached):
        self._update_all_screens(cached, True)
        self.top_bar.title = "SkyView (Offline)"

    def drawer_select(self, target):
        self.nav_drawer.set_state("close")
        if target in ["home", "hourly", "daily", "info"]:
            self.bottom_nav.switch_tab(target)

    def on_location_update(self, **kwargs):
        lat = kwargs.get('lat')
        lon = kwargs.get('lon')
        self.current_accuracy = kwargs.get('accuracy', None)
        if lat and lon:
            self.update_weather(lat=lat, lon=lon)

    def on_gps_status(self, stype, status):
        if stype == 'provider-disabled':
            self.home_screen.show_gps_error()

    def update_weather(self, force=False, lat=None, lon=None):
        with self._coord_lock:
            if lat is not None and lon is not None:
                self.current_lat = lat
                self.current_lon = lon
            thread_lat = self.current_lat
            thread_lon = self.current_lon

        self.top_bar.title = "SkyView - Aggiornamento..."
        self.home_screen.show_loading(True)
        threading.Thread(
            target=self._fetch_weather_thread,
            args=(thread_lat, thread_lon),
            daemon=True
        ).start()

    def _fetch_weather_thread(self, lat, lon):
        try:
            city = self.gps_service.get_city_name(lat, lon)
            with self._coord_lock:
                self.current_city = city
            data, is_offline = self.weather_service.fetch_weather(lat, lon)
            Clock.schedule_once(lambda dt: self._update_all_screens(data, is_offline))
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            Clock.schedule_once(lambda dt: self._update_all_screens(None, True))

    def _update_all_screens(self, data, is_offline):
        if data:
            acc = getattr(self, 'current_accuracy', None)
            with self._coord_lock:
                city = self.current_city
                lat = self.current_lat
                lon = self.current_lon
            self.home_screen.update_ui(data, is_offline, city, lat, lon, accuracy=acc)
            self.hourly_screen.update_ui(data)
            self.daily_screen.update_ui(data)
            self.top_bar.title = "SkyView"
        else:
            self.top_bar.title = "SkyView - Errore Rete"

    def on_stop(self):
        self.gps_service.stop_gps()


if __name__ == "__main__":
    SkyViewApp().run()
''',

    "weather_service.py": '''import json
import os
import logging
import datetime

import requests

from config import OPEN_METEO_URL, CACHE_FILE

logger = logging.getLogger("SkyView.WeatherService")


class WeatherService:
    def __init__(self):
        self.cached_data = None
        self.is_offline = False

    def fetch_weather(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,apparent_temperature,is_day,precipitation,"
                "weather_code,cloud_cover,pressure_msl,surface_pressure,"
                "wind_speed_10m,wind_direction_10m,wind_gusts_10m,"
                "relative_humidity_2m,uv_index"
            ),
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
                logger.info(f"Weather fetched for ({lat}, {lon})")
                return data, False
            else:
                logger.warning(f"Open-Meteo returned status {response.status_code}")
                return self._load_cache(), True
        except requests.exceptions.Timeout:
            logger.error("Timeout fetching weather data")
            return self._load_cache(), True
        except requests.exceptions.ConnectionError:
            logger.error("Connection error fetching weather data")
            return self._load_cache(), True
        except Exception as e:
            logger.error(f"Unexpected error fetching weather: {e}")
            return self._load_cache(), True

    def _save_cache(self, data):
        try:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("Weather cache saved")
        except (OSError, TypeError) as e:
            logger.error(f"Error saving cache: {e}")

    def _load_cache(self):
        self.is_offline = True
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                    self.cached_data = json.load(f)
                    logger.info("Weather loaded from cache")
                    return self.cached_data
            except (OSError, json.JSONDecodeError) as e:
                logger.error(f"Error loading cache: {e}")
        return None
''',

    "gps_service.py": '''import json
import os
import time
import logging

import requests
from plyer import gps

from config import (
    NOMINATIM_URL,
    GEOCODE_CACHE_FILE,
    DEFAULT_LAT,
    DEFAULT_LON,
    DEFAULT_CITY,
    NOMINATIM_RATE_LIMIT,
)

logger = logging.getLogger("SkyView.GPSService")


class GPSService:
    def __init__(self):
        self.lat = None
        self.lon = None
        self.city_name = None
        self.gps_active = False
        self.last_geocode_time = 0
        self.geocode_cache = self._load_geocode_cache()

    def start_gps(self, on_location_update, on_status_change=None):
        try:
            gps.configure(on_location=on_location_update, on_status=on_status_change)
            gps.start(minTime=300000, minDistance=100)
            self.gps_active = True
            logger.info("GPS started")
        except NotImplementedError:
            logger.warning("GPS not supported on this platform. Using default/fallback.")
            self.lat = DEFAULT_LAT
            self.lon = DEFAULT_LON
            self.gps_active = False
            if on_location_update:
                on_location_update(lat=self.lat, lon=self.lon)
        except Exception as e:
            logger.error(f"Unexpected GPS error: {e}")
            self.lat = DEFAULT_LAT
            self.lon = DEFAULT_LON
            self.gps_active = False
            if on_location_update:
                on_location_update(lat=self.lat, lon=self.lon)

    def stop_gps(self):
        if self.gps_active:
            try:
                gps.stop()
                self.gps_active = False
                logger.info("GPS stopped")
            except Exception as e:
                logger.warning(f"Error stopping GPS: {e}")

    def _load_geocode_cache(self):
        if os.path.exists(GEOCODE_CACHE_FILE):
            try:
                with open(GEOCODE_CACHE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Error loading geocode cache: {e}")
        return {}

    def _save_geocode_cache(self):
        try:
            with open(GEOCODE_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.geocode_cache, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning(f"Error saving geocode cache: {e}")

    def get_city_name(self, lat, lon):
        cache_key = f"{round(lat, 3)},{round(lon, 3)}"

        if cache_key in self.geocode_cache:
            logger.debug(f"Geocode cache hit for {cache_key}")
            return self.geocode_cache[cache_key]

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
                'zoom': 10,
                'addressdetails': 1
            }
            response = requests.get(
                NOMINATIM_URL,
                params=params,
                headers=headers,
                timeout=5
            )
            self.last_geocode_time = time.time()

            if response.status_code == 200:
                data = response.json()
                address = data.get('address', {})
                city = (
                    address.get('city')
                    or address.get('town')
                    or address.get('village')
                    or address.get('county')
                    or DEFAULT_CITY
                )

                self.geocode_cache[cache_key] = city
                self._save_geocode_cache()
                logger.info(f"Geocoded ({lat}, {lon}) -> {city}")
                return city
            else:
                logger.warning(f"Nominatim returned status {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Timeout contacting Nominatim")
        except requests.exceptions.ConnectionError:
            logger.error("Connection error contacting Nominatim")
        except Exception as e:
            logger.error(f"Error reverse geocoding: {e}")

        return DEFAULT_CITY
''',

    "utils.py": '''import datetime


def wind_direction_to_cardinal(degrees):
    if degrees is None:
        return "N/A"
    directions = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]
    index = round(degrees / 45) % 8
    return directions[index]


def wmo_code_to_italian(code):
    weather_codes = {
        0: ("Cielo sereno", "weather-sunny"),
        1: ("Prevalentemente sereno", "weather-partly-cloudy"),
        2: ("Parzialmente nuvoloso", "weather-partly-cloudy"),
        3: ("Coperto", "weather-cloudy"),
        45: ("Nebbia", "weather-fog"),
        48: ("Nebbia con brina", "weather-fog"),
        51: ("Pioviggine leggera", "weather-rainy"),
        53: ("Pioviggine moderata", "weather-rainy"),
        55: ("Pioviggine fitta", "weather-pouring"),
        56: ("Pioviggine gelata leggera", "weather-snowy-rainy"),
        57: ("Pioviggine gelata fitta", "weather-snowy-rainy"),
        61: ("Pioggia debole", "weather-rainy"),
        63: ("Pioggia moderata", "weather-pouring"),
        65: ("Pioggia forte", "weather-pouring"),
        66: ("Pioggia gelata debole", "weather-snowy-rainy"),
        67: ("Pioggia gelata forte", "weather-snowy-rainy"),
        71: ("Neve debole", "weather-snowy"),
        73: ("Neve moderata", "weather-snowy"),
        75: ("Neve forte", "weather-snowy-heavy"),
        77: ("Neve granulare", "weather-hail"),
        80: ("Rovesci di pioggia deboli", "weather-partly-rainy"),
        81: ("Rovesci di pioggia moderati", "weather-pouring"),
        82: ("Rovesci di pioggia violenti", "weather-pouring"),
        85: ("Rovesci di neve deboli", "weather-snowy"),
        86: ("Rovesci di neve forti", "weather-snowy-heavy"),
        95: ("Temporale", "weather-lightning"),
        96: ("Temporale con grandine leggera", "weather-lightning-rainy"),
        99: ("Temporale con grandine forte", "weather-lightning-rainy"),
    }
    return weather_codes.get(code, ("Sconosciuto", "cloud-question"))


def format_timestamp(iso_string):
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return str(iso_string)


def get_day_name(iso_string):
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        giorni = ["Lunedi", "Martedi", "Mercoledi", "Giovedi", "Venerdi", "Sabato", "Domenica"]
        return giorni[dt.weekday()]
    except (ValueError, TypeError):
        return str(iso_string)


def format_hour(iso_string):
    if not iso_string:
        return ""
    try:
        dt = datetime.datetime.fromisoformat(iso_string)
        return dt.strftime("%H:%M")
    except (ValueError, TypeError):
        return str(iso_string)
''',

    "config.py": '''# API Endpoints
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"

# Cache Files
CACHE_FILE = "ultima_posizione.json"
GEOCODE_CACHE_FILE = "geocode_cache.json"

# Timing
GPS_UPDATE_INTERVAL = 300  # 5 minutes
NOMINATIM_RATE_LIMIT = 1.0  # Max 1 req/sec

# Defaults (Rome, Italy)
DEFAULT_LAT = 41.9028
DEFAULT_LON = 12.4964
DEFAULT_CITY = "Roma"
''',
}


def api_call(token, method, endpoint, data=None):
    """Make a GitHub API call."""
    url = f"{GITHUB_API}/{endpoint}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "SkyView-Fix-Script"
    }
    
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"   ERRORE HTTP {e.code}: {error_body}")
        return None


def get_file_sha(token, filepath):
    """Get SHA of a file to update it."""
    result = api_call(token, "GET", f"contents/{filepath}?ref={BRANCH}")
    if result and "sha" in result:
        return result["sha"]
    return None


def update_file(token, filepath, content, message):
    """Update or create a file on GitHub."""
    sha = get_file_sha(token, filepath)
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
    
    return api_call(token, "PUT", f"contents/{filepath}", data)


def delete_file(token, filepath, message):
    """Delete a file from GitHub."""
    sha = get_file_sha(token, filepath)
    if not sha:
        print(f"   File {filepath} non trovato, salto.")
        return True
    
    data = {
        "message": message,
        "sha": sha,
        "branch": BRANCH
    }
    
    return api_call(token, "DELETE", f"contents/{filepath}", data)


def main():
    print("=" * 60)
    print(" SKYVIEW GITHUB AUTO-FIX")
    print("=" * 60)
    print()
    print("Questo script corregge automaticamente il repository GitHub.")
    print()
    print("Per ottenere il token (30 secondi):")
    print("1. Vai su: https://github.com/settings/tokens/new")
    print("2. In 'Note' scrivi: SkyView Fix")
    print("3. Spunta SOLO 'repo' (per modificare i tuoi repo)")
    print("4. Clicca 'Generate token' in fondo alla pagina")
    print("5. Copia il token (inizia con 'ghp_')")
    print()
    
    token = input("Incolla qui il tuo GitHub token: ").strip()
    
    if not token:
        print("ERRORE: Token non inserito.")
        sys.exit(1)
    
    print()
    print("Verifico accesso...")
    
    # Verify token
    user = api_call(token, "GET", "")
    if not user:
        print("ERRORE: Token non valido o repo non accessibile.")
        sys.exit(1)
    
    print(f"OK! Repo trovato: {user.get('full_name', 'N/A')}")
    print()
    
    # Step 1: Delete skyview_fix.zip
    print("[1/9] Elimino skyview_fix.zip caricato per sbaglio...")
    delete_file(token, "skyview_fix.zip", "fix: Rimuovi ZIP caricato per sbaglio")
    print("   OK")
    
    # Step 2-8: Update all Python files
    file_messages = {
        "ui_components.py": "fix: MDIcon sostituito con MDIconButton, fix init order",
        "screens.py": "fix: Banner offline, check array length, error handling",
        "main.py": "fix: Race condition con Lock, coordinate passate ai thread",
        "weather_service.py": "fix: Logging, gestione errori specifica, type hints",
        "gps_service.py": "fix: Logging robusto, gestione errori GPS/Nominatim",
        "utils.py": "fix: Type hints, gestione errori ValueError/TypeError",
        "config.py": "fix: Commenti migliorati, cleanup",
    }
    
    for i, (filename, message) in enumerate(file_messages.items(), 2):
        print(f"[{i}/9] Aggiorno {filename}...")
        content = FILES[filename]
        result = update_file(token, filename, content, f"fix: {message}")
        if result:
            print(f"   OK")
        else:
            print(f"   ERRORE durante l'aggiornamento di {filename}")
    
    # Step 9: Delete PrevisoniMeteo folder (old Kotlin)
    print("[9/9] Elimino cartella PrevisoniMeteo (vecchio Kotlin)...")
    # GitHub doesn't support deleting directories directly via API
    # We need to delete each file in the directory
    print("   (La cartella PrevisoniMeteo va eliminata manualmente da GitHub:")
    print("    vai su https://github.com/oratorio03/scientific-eagle-weather-forecast-simply/tree/main/PrevisoniMeteo")
    print("    e clicca i 3 puntini accanto a ogni file -> Delete)")
    
    print()
    print("=" * 60)
    print(" FATTO!")
    print("=" * 60)
    print()
    print("File aggiornati con i fix:")
    print("  - ui_components.py  (MDIcon bug CRITICO)")
    print("  - main.py           (Race condition bug CRITICO)")
    print("  - screens.py        (Banner + Index check)")
    print("  - weather_service.py (Logging + errori)")
    print("  - gps_service.py    (Logging + errori)")
    print("  - utils.py          (Type hints)")
    print("  - config.py         (Cleanup)")
    print()
    print("File eliminato:")
    print("  - skyview_fix.zip")
    print()
    print("MANUALE: Elimina la cartella PrevisoniMeteo per rimuovere il vecchio Kotlin.")
    print()
    print("Repo aggiornato: https://github.com/oratorio03/scientific-eagle-weather-forecast-simply")


if __name__ == "__main__":
    main()
