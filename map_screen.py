import threading
import json
import os
from datetime import date
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.snackbar import Snackbar
from ui_components import MapWeatherSheet
from utils import wmo_code_to_italian
from config import FAVORITES_FILE, MAX_FAVORITES

try:
    from kivy_garden.mapview import MapView, MapMarker
    HAS_MAPVIEW = True
except ImportError:
    HAS_MAPVIEW = False

class BaseScreen(MDScreen):
    pass

class MapScreen(BaseScreen):
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app
        self.current_marker = None
        self.tap_marker = None
        self.sheet = None

        layout = MDFloatLayout()

        if not HAS_MAPVIEW:
            layout.add_widget(MDLabel(
                text="Errore: kivy_garden.mapview non installato.\nEsegui 'garden install mapview'",
                halign="center",
                theme_text_color="Error"
            ))
            self.add_widget(layout)
            return

        # Main MapView
        self.map_view = MapView(zoom=13, lat=41.9028, lon=12.4964)
        self.map_view.bind(on_touch_down=self.on_map_touch)
        layout.add_widget(self.map_view)

        # Floating Action Button to re-center
        self.fab = MDFloatingActionButton(
            icon="crosshairs-gps",
            pos_hint={"right": 0.95, "top": 0.95},
            on_release=self.center_on_gps
        )
        layout.add_widget(self.fab)

        # Loading Spinner
        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': .5, 'center_y': .5},
            active=False,
            opacity=0
        )
        layout.add_widget(self.spinner)

        # Bottom Sheet Container (starts off-screen)
        self.sheet_container = MDBoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(220),
            pos_hint={"y": -1} # hidden
        )

        self.sheet = MapWeatherSheet(
            on_details_callback=self.go_to_details,
            on_save_callback=self.save_to_favorites,
            on_close_callback=self.hide_sheet
        )
        self.sheet_container.add_widget(self.sheet)
        layout.add_widget(self.sheet_container)

        self.add_widget(layout)

    def center_on_gps(self, *args):
        if self.app and hasattr(self.app, 'current_lat') and self.app.current_lat:
            self.map_view.center_on(self.app.current_lat, self.app.current_lon)
            self.update_gps_marker(self.app.current_lat, self.app.current_lon)

    def update_gps_marker(self, lat, lon):
        if not HAS_MAPVIEW: return

        if self.current_marker:
            self.map_view.remove_marker(self.current_marker)

        # Add blue marker for current location
        self.current_marker = MapMarker(lat=lat, lon=lon, source="marker_blue.png" if os.path.exists("marker_blue.png") else "")
        self.map_view.add_marker(self.current_marker)

    def on_map_touch(self, instance, touch):
        # Only handle if touch is on the map and sheet is not catching it
        if self.sheet_container.collide_point(*touch.pos) and self.sheet_container.pos_hint.get("y", -1) == 0:
            return False

        if self.map_view.collide_point(*touch.pos):
            # Give map view chance to handle drag
            if touch.is_double_tap:
                return False

            # Wait briefly to see if it's a drag
            def check_tap(dt):
                if not touch.is_mouse_scrolling and abs(touch.dx) < 5 and abs(touch.dy) < 5:
                    self.handle_tap(touch)
            Clock.schedule_once(check_tap, 0.2)
        return False

    def handle_tap(self, touch):
        lat, lon = self.map_view.get_latlon_at(touch.x, touch.y)
        self.add_tap_marker(lat, lon)
        self.fetch_point_data(lat, lon)

    def add_tap_marker(self, lat, lon):
        if self.tap_marker:
            self.map_view.remove_marker(self.tap_marker)

        # Red marker for tapped location
        self.tap_marker = MapMarker(lat=lat, lon=lon)
        self.map_view.add_marker(self.tap_marker)

    def fetch_point_data(self, lat, lon):
        self.spinner.active = True
        self.spinner.opacity = 1
        self.sheet.lat = lat
        self.sheet.lon = lon
        self.sheet.location_name = "Ricerca..."
        self.sheet.coords_text = f"Lat: {lat:.6f} | Lon: {lon:.6f}"
        self.sheet.temp_text = "--°C"
        self.sheet.desc_text = "..."
        self.sheet.pop_text = "--%"
        self.show_sheet()

        threading.Thread(target=self._bg_fetch_point_data, args=(lat, lon), daemon=True).start()

    def _bg_fetch_point_data(self, lat, lon):
        if not self.app: return

        # Reverse geocode
        city_name = self.app.gps_service.reverse_geocode(lat, lon)

        # Fetch weather
        weather_data = self.app.weather_service.fetch_weather_for_point(lat, lon)

        Clock.schedule_once(lambda dt: self._update_sheet_ui(city_name, weather_data))

    def _update_sheet_ui(self, city_name, weather_data):
        self.spinner.active = False
        self.spinner.opacity = 0
        self.sheet.location_name = city_name

        if weather_data:
            current = weather_data.get("current", {})
            hourly = weather_data.get("hourly", {})

            temp = current.get("temperature_2m", "--")
            wcode = current.get("weather_code", -1)
            desc, icon = wmo_code_to_italian(wcode)

            pops = hourly.get("precipitation_probability", [])
            max_pop = max(pops[:2]) if len(pops) >= 2 else (pops[0] if pops else "--")

            self.sheet.temp_text = f"{temp}°C"
            self.sheet.desc_text = desc
            self.sheet.icon_name = icon
            self.sheet.pop_text = f"{max_pop}%"

            if isinstance(max_pop, (int, float)) and max_pop > 60:
                Snackbar(text="Attenzione: Pioggia imminente in questa zona!").open()
        else:
            Snackbar(text="Connessione necessaria per i dati meteo di questo punto.").open()

    def show_sheet(self):
        self.sheet_container.pos_hint = {"y": 0}

    def hide_sheet(self, *args):
        self.sheet_container.pos_hint = {"y": -1}
        if self.tap_marker:
            self.map_view.remove_marker(self.tap_marker)
            self.tap_marker = None

    def go_to_details(self, lat, lon, name):
        if self.app:
            # Tell app to update weather with new coords, but don't force GPS override
            self.app.current_city = name
            self.app.update_weather(lat=lat, lon=lon)
            self.app.bottom_nav.switch_tab("home")
            self.hide_sheet()

    def save_to_favorites(self, lat, lon, name):
        favs = []
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                    favs = json.load(f)
            except:
                pass

        # Check if already exists (by rough coords)
        for f in favs:
            if abs(f['lat'] - lat) < 0.01 and abs(f['lon'] - lon) < 0.01:
                Snackbar(text="Posizione già nei preferiti").open()
                return

        if len(favs) >= MAX_FAVORITES:
            Snackbar(text=f"Limite di {MAX_FAVORITES} preferiti raggiunto.").open()
            return

        favs.append({
            "name": name,
            "lat": lat,
            "lon": lon,
            "added": date.today().isoformat()
        })

        try:
            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(favs, f, ensure_ascii=False, indent=2)
            Snackbar(text="Salvato nei preferiti").open()
            # Notify app to refresh favorites list if needed
            if hasattr(self.app, 'favorites_screen'):
                self.app.favorites_screen.load_favorites()
        except Exception as e:
            Snackbar(text="Errore nel salvataggio").open()
