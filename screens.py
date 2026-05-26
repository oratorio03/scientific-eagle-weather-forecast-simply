from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import MDList
from kivymd.uix.textfield import MDTextField
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.toolbar import MDTopAppBar
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

        # Header (Offline Banner + Timestamp)
        self.header_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="10dp")
        self.offline_banner = MDLabel(
            text="Dati in cache - non aggiornati",
            theme_text_color="Error",
            halign="center",
            bold=True,
            adaptive_height=True
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
        self.offline_banner.opacity = 0

        # Location Info
        self.location_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="10dp")
        self.city_label = MDLabel(text="Cerco posizione...", font_style="H4", halign="center", bold=True)
        self.coords_label = MDLabel(text="Lat: -- | Lon: --", font_style="Caption", halign="center")
        self.location_layout.add_widget(self.city_label)
        self.location_layout.add_widget(self.coords_label)

        # Current Weather
        self.current_weather_layout = MDBoxLayout(orientation='vertical', adaptive_height=True, padding="20dp", spacing="10dp")
        self.temp_label = MDLabel(text="--°C", font_style="H1", halign="center")
        self.desc_label = MDLabel(text="--", font_style="H6", halign="center")
        self.feels_like_label = MDLabel(text="Percepita: --°C", font_style="Subtitle1", halign="center", theme_text_color="Secondary")
        self.current_weather_layout.add_widget(self.temp_label)
        self.current_weather_layout.add_widget(self.desc_label)
        self.current_weather_layout.add_widget(self.feels_like_label)

        # Loading Spinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': .5},
            active=False,
            opacity=0
        )
        self.location_layout.add_widget(self.spinner)

        # Weather Grid Data
        scroll_grid = MDScrollView()
        self.grid_layout = MDGridLayout(cols=3, adaptive_height=True, padding="10dp", spacing="10dp")

        self.grid_items = {
            'umidita': WeatherGridItem(title="Umidità"),
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

        # Manual refresh
        refresh_layout = MDBoxLayout(adaptive_height=True, padding="10dp")
        refresh_btn = MDRaisedButton(text="Aggiorna Ora", pos_hint={"center_x": .5}, on_release=self.force_refresh)
        refresh_layout.add_widget(MDLabel()) # Spacer
        refresh_layout.add_widget(refresh_btn)
        refresh_layout.add_widget(MDLabel()) # Spacer

        # GPS Error Fallback Input
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

        # Assemble Main Layout
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
        self.offline_banner.opacity = 1 if is_offline else 0
        self.timestamp_label.text = f"Ultimo aggiornamento: {format_timestamp(data.get('timestamp', ''))}"
        self.city_label.text = city_name
        acc_text = f" (±{int(accuracy)}m)" if accuracy else ""
        self.coords_label.text = f"Lat: {lat:.6f} | Lon: {lon:.6f}{acc_text}"

        current = data.get("current", {})
        temp = current.get("temperature_2m", "--")
        self.temp_label.text = f"{temp}°C"

        feels = current.get("apparent_temperature", "--")
        self.feels_like_label.text = f"Percepita: {feels}°C"

        wcode = current.get("weather_code", -1)
        desc, icon = wmo_code_to_italian(wcode)
        self.desc_label.text = desc

        # Grid
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
            text="SkyView v1.0\nApp Meteo Iper-Locale basata sulle coordinate GPS esatte.\n\nSorgenti Dati:\n- Previsioni: Open-Meteo\n- Reverse Geocoding: Nominatim OpenStreetMap\n\nNessuna API Key richiesta.",
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

        now = datetime.datetime.now()

        count = 0
        for i in range(len(times)):
            dt = datetime.datetime.fromisoformat(times[i])
            if dt > now and count < 24:
                desc, icon = wmo_code_to_italian(wcodes[i])
                card = HourlyForecastCard(
                    hour=format_hour(times[i]),
                    temp=f"{temps[i]}°C",
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

        for i in range(len(times)):
            item = DailyForecastItem(
                day=times[i],
                min_temp=min_temps[i],
                max_temp=max_temps[i],
                weather_code=wcodes[i]
            )
            self.list_layout.add_widget(item)
