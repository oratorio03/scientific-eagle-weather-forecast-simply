import urllib.request
import urllib.parse
import json
import tkinter as tk
from tkinter import messagebox
import os

API_KEY = "YOUR_API_KEY_HERE"
PREFS_FILE = "WeatherPrefs.json"
LAST_CITY_KEY = "LastCity"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city_name):
    url = f"{BASE_URL}?q={urllib.parse.quote(city_name)}&units=metric&appid={API_KEY}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                raise Exception("Errore nel recupero dei dati meteo")
    except Exception as e:
        raise Exception(f"Errore nel recupero dei dati meteo: {e}")

def get_weather_data_by_coordinates(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&units=metric&appid={API_KEY}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                raise Exception("Errore nel recupero dei dati meteo")
    except Exception as e:
        raise Exception(f"Errore nel recupero dei dati meteo: {e}")

def get_location_by_ip():
    try:
        with urllib.request.urlopen("http://ip-api.com/json/") as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                return data.get("lat"), data.get("lon")
    except Exception as e:
        raise Exception(f"Impossibile ottenere la posizione: {e}")
    return None, None

def save_last_searched_city(city_name):
    prefs = {}
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, 'r') as f:
                prefs = json.load(f)
        except Exception:
            pass
    prefs[LAST_CITY_KEY] = city_name
    try:
        with open(PREFS_FILE, 'w') as f:
            json.dump(prefs, f)
    except Exception:
        pass

def get_last_searched_city():
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, 'r') as f:
                prefs = json.load(f)
                return prefs.get(LAST_CITY_KEY, "")
        except Exception:
            pass
    return ""

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Previsioni Meteo")

        self.city_input = tk.Entry(root, width=30)
        self.city_input.pack(pady=10)

        self.search_button = tk.Button(root, text="Cerca", command=self.on_search)
        self.search_button.pack(pady=5)

        self.refresh_button = tk.Button(root, text="Aggiorna Posizione", command=self.on_refresh)
        self.refresh_button.pack(pady=5)

        self.city_name_label = tk.Label(root, text="-", font=("Arial", 16))
        self.city_name_label.pack(pady=5)

        self.temperature_label = tk.Label(root, text="-", font=("Arial", 24))
        self.temperature_label.pack(pady=5)

        self.description_label = tk.Label(root, text="-", font=("Arial", 14))
        self.description_label.pack(pady=5)

        self.on_refresh()

    def show_loading(self):
        self.city_name_label.config(text="Caricamento...")
        self.temperature_label.config(text="Caricamento...")
        self.description_label.config(text="Caricamento...")

    def update_ui(self, city_name, temperature, description):
        self.city_name_label.config(text=city_name)
        self.temperature_label.config(text=f"{temperature}°C")
        self.description_label.config(text=description)

    def on_search(self):
        city_name = self.city_input.get()
        if city_name:
            self.search_weather_data(city_name)
        else:
            messagebox.showwarning("Attenzione", "Inserisci il nome di una città")

    def search_weather_data(self, city_name):
        self.show_loading()
        try:
            data = get_weather_data(city_name)
            name = data.get("name", "")
            temp = data.get("main", {}).get("temp", "")
            desc = data.get("weather", [{}])[0].get("description", "")
            self.update_ui(name, temp, desc)
            save_last_searched_city(name)
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.update_ui("-", "-", "-")

    def search_weather_data_by_location(self, lat, lon):
        self.show_loading()
        try:
            data = get_weather_data_by_coordinates(lat, lon)
            name = data.get("name", "")
            temp = data.get("main", {}).get("temp", "")
            desc = data.get("weather", [{}])[0].get("description", "")
            self.update_ui(name, temp, desc)
            save_last_searched_city(name)
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            self.update_ui("-", "-", "-")

    def on_refresh(self):
        try:
            lat, lon = get_location_by_ip()
            if lat and lon:
                self.search_weather_data_by_location(lat, lon)
            else:
                last_city = get_last_searched_city()
                if last_city:
                    self.search_weather_data(last_city)
                else:
                    messagebox.showinfo("Info", "Nessuna città cercata in precedenza e posizione non disponibile")
        except Exception as e:
            messagebox.showerror("Errore", str(e))
            last_city = get_last_searched_city()
            if last_city:
                self.search_weather_data(last_city)

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
