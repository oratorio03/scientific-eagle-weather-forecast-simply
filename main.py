from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout, MDNavigationDrawerMenu, MDNavigationDrawerItem, MDNavigationDrawerLabel
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivy.clock import Clock
from kivy.core.window import Window
from screens import HomeScreen, HourlyScreen, DailyScreen, InfoScreen
from gps_service import GPSService
from weather_service import WeatherService
from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_CITY
import threading

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

        # Main Layout
        self.nav_layout = MDNavigationLayout()

        from kivymd.uix.screen import MDScreen

        # Screen Manager
        self.sm = MDScreenManager()

        main_screen_wrapper = MDScreen(name="main_wrapper")
        main_layout = MDBoxLayout(orientation='vertical')

        # Top App Bar
        self.top_bar = MDTopAppBar(
            title="SkyView",
            elevation=4,
            pos_hint={"top": 1},
            md_bg_color=self.theme_cls.primary_color,
            specific_text_color=self.theme_cls.primary_light,
            left_action_items=[["menu", lambda x: self.nav_drawer.set_state("open")]]
        )
        main_layout.add_widget(self.top_bar)

        # Bottom Navigation
        self.bottom_nav = MDBottomNavigation(
            selected_color_background="eeeaea",
            text_color_active="lightgrey"
        )

        # Home Item
        home_item = MDBottomNavigationItem(name="home", text="Oggi", icon="calendar-today")
        self.home_screen = HomeScreen(name="home_content")
        self.home_screen.app = self
        home_item.add_widget(self.home_screen)

        # Hourly Item
        hourly_item = MDBottomNavigationItem(name="hourly", text="24 Ore", icon="clock-outline")
        self.hourly_screen = HourlyScreen(name="hourly_content")
        self.hourly_screen.app = self
        hourly_item.add_widget(self.hourly_screen)

        # Daily Item
        daily_item = MDBottomNavigationItem(name="daily", text="7 Giorni", icon="calendar-week")
        self.daily_screen = DailyScreen(name="daily_content")
        self.daily_screen.app = self
        daily_item.add_widget(self.daily_screen)

        # Info Item (accessible only via drawer, but we need it in sm or bottom_nav. Let's add it as a hidden bottom nav item or a separate screen in sm)
        # To keep it simple, we add it to the bottom nav but rely on the drawer to switch to it
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

        # Add to Navigation Layout
        self.sm.add_widget(main_screen_wrapper)
        self.nav_layout.add_widget(self.sm)

        # Navigation Drawer
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
        # Start GPS and attempt initial fetch
        self.top_bar.title = "SkyView - Aggiornamento..."
        self.home_screen.show_loading(True)
        self.gps_service.start_gps(self.on_location_update, self.on_gps_status)

        # Attempt to load cache immediately for fast startup (non-blocking)
        cached = self.weather_service._load_cache()
        if cached:
            threading.Thread(target=self._load_cache_thread, args=(cached,), daemon=True).start()

    def _load_cache_thread(self, cached):
        city = self.gps_service.get_city_name(DEFAULT_LAT, DEFAULT_LON)
        self.current_city = city
        Clock.schedule_once(lambda dt: self._apply_cache(cached))

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
        # Kivy Plyer might provide accuracy, but kwargs structure is platform dependent.
        # We attempt to fetch it or default to None
        self.current_accuracy = kwargs.get('accuracy', None)
        if lat and lon:
            self.update_weather(lat=lat, lon=lon)

    def on_gps_status(self, stype, status):
        if stype == 'provider-disabled':
            self.home_screen.show_gps_error()

    def update_weather(self, force=False, lat=None, lon=None):
        if lat is not None and lon is not None:
            self.current_lat = lat
            self.current_lon = lon

        self.top_bar.title = "SkyView - Aggiornamento..."
        self.home_screen.show_loading(True)
        threading.Thread(target=self._fetch_weather_thread, daemon=True).start()

    def _fetch_weather_thread(self):
        # Heavy work in thread: reverse geocoding & open-meteo API
        city = self.gps_service.get_city_name(self.current_lat, self.current_lon)
        self.current_city = city
        data, is_offline = self.weather_service.fetch_weather(self.current_lat, self.current_lon)

        # Update UI on Main Thread
        Clock.schedule_once(lambda dt: self._update_all_screens(data, is_offline))

    def _update_all_screens(self, data, is_offline):
        if data:
            acc = getattr(self, 'current_accuracy', None)
            self.home_screen.update_ui(data, is_offline, self.current_city, self.current_lat, self.current_lon, accuracy=acc)
            self.hourly_screen.update_ui(data)
            self.daily_screen.update_ui(data)
            self.top_bar.title = "SkyView"
        else:
            self.top_bar.title = "SkyView - Errore Rete"

    def on_stop(self):
        self.gps_service.stop_gps()

if __name__ == "__main__":
    SkyViewApp().run()
