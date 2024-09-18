package com.example.previsioni_meteo

import android.Manifest
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.location.Location
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
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
    private lateinit var fusedLocationClient: FusedLocationProviderClient

    companion object {
        private const val PREFS_NAME = "WeatherPrefs"
        private const val LAST_CITY_KEY = "LastCity"
        private const val API_KEY = "YOUR_API_KEY_HERE" // Sostituisci con la tua chiave API di OpenWeatherMap
        private const val BASE_URL = "https://api.openweathermap.org/data/2.5/"
        private const val LOCATION_PERMISSION_REQUEST_CODE = 1001
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

        // Inizializzazione del FusedLocationProviderClient
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

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

        // Richiesta della posizione dell'utente
        requestLocationPermission()
    }

    private fun refreshWeatherData() {
        if (hasLocationPermission()) {
            getLastLocation()
        } else {
            val lastCity = getLastSearchedCity()
            if (lastCity.isNotEmpty()) {
                searchWeatherData(lastCity)
            } else {
                Toast.makeText(this, "Nessuna città cercata in precedenza", Toast.LENGTH_SHORT).show()
            }
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

    private fun requestLocationPermission() {
        if (!hasLocationPermission()) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.ACCESS_FINE_LOCATION),
                LOCATION_PERMISSION_REQUEST_CODE
            )
        } else {
            getLastLocation()
        }
    }

    private fun hasLocationPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            this,
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun getLastLocation() {
        if (hasLocationPermission()) {
            fusedLocationClient.lastLocation
                .addOnSuccessListener { location: Location? ->
                    location?.let {
                        searchWeatherDataByLocation(it.latitude, it.longitude)
                    } ?: run {
                        Toast.makeText(this, "Impossibile ottenere la posizione", Toast.LENGTH_SHORT).show()
                        refreshWeatherData()
                    }
                }
                .addOnFailureListener { e ->
                    Toast.makeText(this, "Errore nel recupero della posizione", Toast.LENGTH_SHORT).show()
                    e.printStackTrace()
                    refreshWeatherData()
                }
        } else {
            requestLocationPermission()
        }
    }

    private fun searchWeatherDataByLocation(latitude: Double, longitude: Double) {
        showLoadingState()

        lifecycleScope.launch {
            try {
                val response = weatherApi.getWeatherDataByCoordinates(latitude, longitude, apiKey = API_KEY)
                updateUI(response.name, "${response.main.temp}°C", response.weather.firstOrNull()?.description ?: "")
                saveLastSearchedCity(response.name)
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Errore nel recupero dei dati meteo", Toast.LENGTH_SHORT).show()
                e.printStackTrace()
            }
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == LOCATION_PERMISSION_REQUEST_CODE) {
            if (grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                getLastLocation()
            } else {
                Toast.makeText(this, "Permesso di localizzazione negato", Toast.LENGTH_SHORT).show()
                refreshWeatherData()
            }
        }
    }
}
    }
}