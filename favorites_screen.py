import json
import os
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, TwoLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import Snackbar
from config import FAVORITES_FILE

class FavoriteListItem(TwoLineAvatarIconListItem):
    def __init__(self, item_data, on_select, on_delete, **kwargs):
        super().__init__(**kwargs)
        self.item_data = item_data
        self.on_select = on_select
        self.on_delete = on_delete

        self.text = item_data['name']
        self.secondary_text = f"Lat: {item_data['lat']:.4f} | Lon: {item_data['lon']:.4f}"

        icon_left = IconLeftWidget(icon="map-marker-star")
        self.add_widget(icon_left)

        icon_right = IconRightWidget(icon="delete")
        icon_right.bind(on_release=self.delete_pressed)
        self.add_widget(icon_right)

    def on_release(self):
        self.on_select(self.item_data)

    def delete_pressed(self, instance):
        self.on_delete(self.item_data)

class FavoritesScreen(MDScreen):
    def __init__(self, app=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app

        layout = MDBoxLayout(orientation='vertical')

        header = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="60dp", padding="10dp")
        header.add_widget(MDLabel(text="Preferiti", font_style="H5", halign="center"))
        layout.add_widget(header)

        scroll = MDScrollView()
        self.list_layout = MDList()
        scroll.add_widget(self.list_layout)

        layout.add_widget(scroll)
        self.add_widget(layout)

    def on_enter(self):
        self.load_favorites()

    def load_favorites(self):
        self.list_layout.clear_widgets()
        if not os.path.exists(FAVORITES_FILE):
            self.list_layout.add_widget(MDLabel(text="Nessun preferito salvato.", halign="center", theme_text_color="Secondary"))
            return

        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                favs = json.load(f)

            if not favs:
                self.list_layout.add_widget(MDLabel(text="Nessun preferito salvato.", halign="center", theme_text_color="Secondary"))
                return

            for fav in favs:
                item = FavoriteListItem(
                    item_data=fav,
                    on_select=self.on_favorite_select,
                    on_delete=self.on_favorite_delete
                )
                self.list_layout.add_widget(item)

        except Exception as e:
            print(f"Errore caricamento preferiti: {e}")
            self.list_layout.add_widget(MDLabel(text="Errore nel caricamento.", halign="center", theme_text_color="Error"))

    def on_favorite_select(self, item_data):
        if self.app:
            self.app.current_city = item_data['name']
            self.app.update_weather(lat=item_data['lat'], lon=item_data['lon'])
            self.app.bottom_nav.switch_tab("home")

    def on_favorite_delete(self, item_data):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                favs = json.load(f)

            favs = [f for f in favs if not (f['lat'] == item_data['lat'] and f['lon'] == item_data['lon'])]

            with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
                json.dump(favs, f, ensure_ascii=False, indent=2)

            self.load_favorites()
            Snackbar(text="Preferito eliminato").open()
        except Exception as e:
            Snackbar(text="Errore eliminazione").open()
