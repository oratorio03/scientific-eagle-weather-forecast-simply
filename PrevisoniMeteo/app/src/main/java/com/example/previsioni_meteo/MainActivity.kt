package com.example.previsioni_meteo

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    private lateinit var cityNameTextView: TextView
    private lateinit var temperatureTextView: TextView
    private lateinit var descriptionTextView: TextView
    private lateinit var refreshButton: Button

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inizializzazione delle view
        cityNameTextView = findViewById(R.id.cityNameTextView)
        temperatureTextView = findViewById(R.id.temperatureTextView)
        descriptionTextView = findViewById(R.id.descriptionTextView)
        refreshButton = findViewById(R.id.refreshButton)

        // Impostazione del listener per il pulsante di aggiornamento
        refreshButton.setOnClickListener {
            refreshWeatherData()
        }

        // Caricamento iniziale dei dati meteo
        refreshWeatherData()
    }

    private fun refreshWeatherData() {
        // Qui implementeremo la logica per recuperare i dati meteo
        // Per ora, mostriamo solo un messaggio di caricamento
        cityNameTextView.text = getString(R.string.loading)
        temperatureTextView.text = getString(R.string.loading)
        descriptionTextView.text = getString(R.string.loading)

        // Simuliamo un'operazione di rete con un ritardo
        cityNameTextView.postDelayed({
            // Qui aggiorneremo i dati con quelli reali quando implementeremo la chiamata di rete
            cityNameTextView.text = "Roma"
            temperatureTextView.text = "25°C"
            descriptionTextView.text = "Soleggiato"
        }, 2000) // Ritardo di 2 secondi
    }
}