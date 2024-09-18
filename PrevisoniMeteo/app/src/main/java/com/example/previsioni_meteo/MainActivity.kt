package com.example.previsioni_meteo

import android.content.Context
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.lifecycle.lifecycleScope
import com.google.android.material.textfield.TextInputEditText
import kotlinx.coroutines.launch
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class MainActivity : AppCompatActivity() {
    private lateinit var cityNameTextView: TextView
    private lateinit var temperatureTextView: TextView
    private lateinit var descriptionTextView: TextView
    private lateinit var refreshButton: Button
    private lateinit var searchButton: Button
    private lateinit var cityInputEditText: TextInputEditText
    private lateinit var sharedPreferences: SharedPreferences
    private lateinit var weatherApi: WeatherApi

    companion object {
        private const val PREFS_NAME = "WeatherPrefs"
        private const val LAST_CITY_KEY = "LastCity"
        private const val API_KEY = "YOUR_API_KEY_HERE" // Sostituisci con la tua chiave API di OpenWeatherMap
        private const val BASE_URL = "https://api.openweathermap.org/data/2.5/"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inizializzazione delle SharedPreferences
        sharedPreferences = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        // Inizializzazione di Retrofit e WeatherApi
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        weatherApi = retrofit.create(WeatherApi::class.java)

        // Inizializzazione delle view
        cityNameTextView = findViewById(R.id.cityNameTextView)
        temperatureTextView = findViewById(R.id.temperatureTextView)
        descriptionTextView = findViewById(R.id.descriptionTextView)
        refreshButton = findViewById(R.id.refreshButton)
        searchButton = findViewById(R.id.searchButton)
        cityInputEditText = findViewById(R.id.cityInputEditText)

        // Impostazione del listener per il pulsante di aggiornamento
        refreshButton.setOnClickListener {
            refreshWeatherData()
        }

        // Impostazione del listener per il pulsante di ricerca
        searchButton.setOnClickListener {
            val cityName = cityInputEditText.text.toString()
            if (cityName.isNotEmpty()) {
                searchWeatherData(cityName)
            } else {
                Toast.makeText(this, "Inserisci il nome di una città", Toast.LENGTH_SHORT).show()
            }
        }

        // Caricamento dei dati dell'ultima città cercata
        loadLastSearchedCity()
    }

    private fun refreshWeatherData() {
        val lastCity = getLastSearchedCity()
        if (lastCity.isNotEmpty()) {
            searchWeatherData(lastCity)
        } else {
            Toast.makeText(this, "Nessuna città cercata in precedenza", Toast.LENGTH_SHORT).show()
        }
    }

    private fun searchWeatherData(cityName: String) {
        saveLastSearchedCity(cityName)
        showLoadingState()

        lifecycleScope.launch {
            try {
                val response = weatherApi.getWeatherData(cityName, apiKey = API_KEY)
                updateUI(response.name, "${response.main.temp}°C", response.weather.firstOrNull()?.description ?: "")
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Errore nel recupero dei dati meteo", Toast.LENGTH_SHORT).show()
                e.printStackTrace()
            }
        }
    }

    private fun showLoadingState() {
        cityNameTextView.text = getString(R.string.loading)
        temperatureTextView.text = getString(R.string.loading)
        descriptionTextView.text = getString(R.string.loading)
    }

    private fun updateUI(cityName: String, temperature: String, description: String) {
        cityNameTextView.text = cityName
        temperatureTextView.text = temperature
        descriptionTextView.text = description
    }

    private fun saveLastSearchedCity(cityName: String) {
        sharedPreferences.edit().putString(LAST_CITY_KEY, cityName).apply()
    }

    private fun getLastSearchedCity(): String {
        return sharedPreferences.getString(LAST_CITY_KEY, "") ?: ""
    }

    private fun loadLastSearchedCity() {
        val lastCity = getLastSearchedCity()
        if (lastCity.isNotEmpty()) {
            searchWeatherData(lastCity)
        }
    }
}
    private fun showLoadingState() {
        cityNameTextView.text = getString(R.string.loading)
        temperatureTextView.text = getString(R.string.loading)
        descriptionTextView.text = getString(R.string.loading)
    }

    private fun updateUI(cityName: String, temperature: String, description: String) {
        cityNameTextView.text = cityName
        temperatureTextView.text = temperature
        descriptionTextView.text = description
    }

    private fun saveLastSearchedCity(cityName: String) {
        sharedPreferences.edit().putString(LAST_CITY_KEY, cityName).apply()
    }

    private fun getLastSearchedCity(): String {
        return sharedPreferences.getString(LAST_CITY_KEY, "") ?: ""
    }

    private fun loadLastSearchedCity() {
        val lastCity = getLastSearchedCity()
        if (lastCity.isNotEmpty()) {
            searchWeatherData(lastCity)
        }
    }
}