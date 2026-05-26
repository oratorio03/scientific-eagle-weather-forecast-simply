from kivymd.uix.card import MDCard
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
        self.secondary_text = f"Min: {min_temp}°C | Max: {max_temp}°C"

        self.add_widget(IconLeftWidget(icon=icon))
