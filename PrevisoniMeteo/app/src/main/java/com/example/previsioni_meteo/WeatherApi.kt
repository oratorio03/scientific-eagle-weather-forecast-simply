package com.example.previsioni_meteo

import retrofit2.http.GET
import retrofit2.http.Query

interface WeatherApi {
    @GET("weather")
    suspend fun getWeatherData(
        @Query("q") cityName: String,
        @Query("units") units: String = "metric",
        @Query("appid") apiKey: String
    ): WeatherResponse

    @GET("weather")
    suspend fun getWeatherDataByCoordinates(
        @Query("lat") latitude: Double,
        @Query("lon") longitude: Double,
        @Query("units") units: String = "metric",
        @Query("appid") apiKey: String
    ): WeatherResponse
}

data class WeatherResponse(
    val name: String,
    val main: MainWeather,
    val weather: List<WeatherDescription>
)

data class MainWeather(
    val temp: Double
)

data class WeatherDescription(
    val description: String
)