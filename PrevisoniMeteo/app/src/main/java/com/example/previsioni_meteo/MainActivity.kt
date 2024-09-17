package com.example.previsioni_meteo

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

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

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

        // Caricamento iniziale dei dati meteo
        refreshWeatherData()
    }

    private fun refreshWeatherData() {
        // Qui implementeremo la logica per recuperare i dati meteo
        // Per ora, mostriamo solo un messaggio di caricamento
        showLoadingState()

        // Simuliamo un'operazione di rete con un ritardo
        cityNameTextView.postDelayed({
            // Qui aggiorneremo i dati con quelli reali quando implementeremo la chiamata di rete
            updateUI("Roma", "25°C", "Soleggiato")
        }, 2000) // Ritardo di 2 secondi
    }

    private fun searchWeatherData(cityName: String) {
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
}