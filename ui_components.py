from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.label import MDIcon
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp
from utils import wmo_code_to_italian, get_day_name, format_hour

class WeatherGridItem(MDBoxLayout):
    title = StringProperty("")
    value = StringProperty("")

    def __init__(self, **kwargs):
        self.title_label = MDLabel(
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary"
        )
        self.value_label = MDLabel(
            font_style="Body1",
            halign="center",
            bold=True
        )
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.adaptive_height = True
        self.padding = "8dp"

        self.title_label.text = self.title
        self.value_label.text = self.value

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
        self.hour_label = MDLabel(
            font_style="Caption",
            halign="center"
        )
        self.icon_widget = MDIcon(
            halign="center",
            font_size="32sp",
            theme_text_color="Primary"
        )
        self.temp_label = MDLabel(
            font_style="Body1",
            halign="center",
            bold=True
        )
        self.pop_label = MDLabel(
            font_style="Caption",
            halign="center",
            theme_text_color="Secondary"
        )
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = ("80dp", "120dp")
        self.padding = "8dp"
        self.radius = 12

        self.hour_label.text = self.hour
        self.icon_widget.icon = self.icon
        self.temp_label.text = self.temp
        self.pop_label.text = self.pop

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
        self.secondary_text = f"Min: {min_temp}°C | Max: {max_temp}°C"

        icon_widget = IconLeftWidget(icon=icon)
        self.add_widget(icon_widget)

class MapWeatherSheet(MDCard):
    location_name = StringProperty("Caricamento...")
    coords_text = StringProperty("")
    temp_text = StringProperty("--°C")
    desc_text = StringProperty("...")
    pop_text = StringProperty("")
    icon_name = StringProperty("cloud-question")
    lat = NumericProperty(0)
    lon = NumericProperty(0)
    on_details_callback = ObjectProperty(None)
    on_save_callback = ObjectProperty(None)
    on_close_callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (1, None)
        self.height = dp(220)
        self.padding = dp(16)
        self.spacing = dp(8)
        self.radius = [dp(20), dp(20), 0, 0]
        self.md_bg_color = self.theme_cls.bg_dark if self.theme_cls.theme_style == "Dark" else self.theme_cls.bg_light

        # Header with location and close button
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(30))
        self.loc_label = MDLabel(text=self.location_name, font_style="H6", bold=True)
        close_btn = MDIcon(icon="close", on_release=self.close_sheet, size_hint_x=None, width=dp(30))
        header.add_widget(self.loc_label)
        header.add_widget(close_btn)

        self.coords_label = MDLabel(text=self.coords_text, font_style="Caption", theme_text_color="Secondary", size_hint_y=None, height=dp(20))

        # Weather row
        weather_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(60))
        self.w_icon = MDIcon(icon=self.icon_name, font_size="48sp", size_hint_x=None, width=dp(50), halign="center")

        temp_col = MDBoxLayout(orientation="vertical")
        self.t_label = MDLabel(text=self.temp_text, font_style="H5")
        self.d_label = MDLabel(text=self.desc_text, font_style="Body2", theme_text_color="Secondary")
        temp_col.add_widget(self.t_label)
        temp_col.add_widget(self.d_label)

        pop_col = MDBoxLayout(orientation="vertical", size_hint_x=None, width=dp(80))
        pop_title = MDLabel(text="Pioggia", font_style="Caption", halign="center")
        self.p_label = MDLabel(text=self.pop_text, font_style="Body2", halign="center", bold=True)
        pop_col.add_widget(pop_title)
        pop_col.add_widget(self.p_label)

        weather_row.add_widget(self.w_icon)
        weather_row.add_widget(temp_col)
        weather_row.add_widget(pop_col)

        # Buttons row
        buttons_row = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        details_btn = MDRaisedButton(text="Vedi dettagli", on_release=self.view_details, size_hint_x=1)
        save_btn = MDFlatButton(text="Salva nei preferiti", on_release=self.save_favorite, size_hint_x=1)

        buttons_row.add_widget(save_btn)
        buttons_row.add_widget(details_btn)

        self.add_widget(header)
        self.add_widget(self.coords_label)
        self.add_widget(weather_row)
        self.add_widget(MDLabel()) # spacer
        self.add_widget(buttons_row)

    def on_location_name(self, instance, value):
        if hasattr(self, 'loc_label'): self.loc_label.text = value
    def on_coords_text(self, instance, value):
        if hasattr(self, 'coords_label'): self.coords_label.text = value
    def on_temp_text(self, instance, value):
        if hasattr(self, 't_label'): self.t_label.text = value
    def on_desc_text(self, instance, value):
        if hasattr(self, 'd_label'): self.d_label.text = value
    def on_pop_text(self, instance, value):
        if hasattr(self, 'p_label'): self.p_label.text = value
    def on_icon_name(self, instance, value):
        if hasattr(self, 'w_icon'): self.w_icon.icon = value

    def close_sheet(self, *args):
        if self.on_close_callback:
            self.on_close_callback()

    def view_details(self, *args):
        if self.on_details_callback:
            self.on_details_callback(self.lat, self.lon, self.location_name)

    def save_favorite(self, *args):
        if self.on_save_callback:
            self.on_save_callback(self.lat, self.lon, self.location_name)
