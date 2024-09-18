package com.example.previsioni_meteo

import android.content.Context
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {
    private lateinit var cityNameTextView: TextView
    private lateinit var temperatureTextView: TextView
    private lateinit var descriptionTextView: TextView
    private lateinit var refreshButton: Button
    private lateinit var searchButton: Button
    private lateinit var cityInputEditText: TextInputEditText
    private lateinit var sharedPreferences: SharedPreferences

    companion object {
        private const val PREFS_NAME = "WeatherPrefs"
        private const val LAST_CITY_KEY = "LastCity"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inizializzazione delle SharedPreferences
        sharedPreferences = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

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
            // Se non c'è una città salvata, mostra un messaggio all'utente
            Toast.makeText(this, "Nessuna città cercata in precedenza", Toast.LENGTH_SHORT).show()
        }
    }

    private fun searchWeatherData(cityName: String) {
        // Salva la città cercata
        saveLastSearchedCity(cityName)

        // Qui implementeremo la logica per recuperare i dati meteo per la città specificata
        // Per ora, mostriamo solo un messaggio di caricamento
        showLoadingState()

        // Simuliamo un'operazione di rete con un ritardo
        cityNameTextView.postDelayed({
            // Qui aggiorneremo i dati con quelli reali quando implementeremo la chiamata di rete
            updateUI(cityName, "20°C", "Nuvoloso")
        }, 2000) // Ritardo di 2 secondi
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