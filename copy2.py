from django.shortcuts import render
import urllib.request
import json
import requests_cache
from retry_requests import retry
import numpy as np
import datetime
from openmeteo_requests import Client
import pandas as pd

from .forms import CityForm  # Предполагается, что у вас есть форма для ввода города

def weather_view(request):
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            # Setup the Open-Meteo API client with cache and retry on error
            cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
            retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
            openmeteo = Client(session=retry_session)

            # Получаем координаты города с помощью OpenCage Geocoding API
            coord_response = urllib.request.urlopen(f"https://api.opencagedata.com/geocode/v1/json?q={city}&key=7bfd1f0f7ac642d2a0afb5a327956a45")
            coord_data = json.loads(coord_response.read())

            lat = coord_data['results'][0]['geometry']['lat']
            lng = coord_data['results'][0]['geometry']['lng']

            # Устанавливаем параметры для запроса к Open-Meteo API
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lng,
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "surface_pressure", "wind_speed_10m", "wind_gusts_10m"],
                "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation_probability", "surface_pressure", "wind_speed_10m", "wind_gusts_10m"]
            }

            # Получаем ответы от Open-Meteo API
            responses = openmeteo.weather_api(url, params=params)

            # Обрабатываем первый ответ (можно добавить цикл для обработки нескольких ответов или моделей погоды)
            response = responses[0]

            # Обработка текущих данных
            current = response.Current()
            current_weather = {
                "temperature_2m": round(current.Variables(0).Value(), 1),
                "relative_humidity_2m": round(current.Variables(1).Value(), 1),
                "precipitation": round(current.Variables(3).Value(), 1),
                "surface_pressure": round(current.Variables(4).Value(), 1),
                "wind_speed_10m": round(current.Variables(5).Value(), 1),
                "wind_gusts_10m": round(current.Variables(6).Value(), 1),
            }

            # Передаем данные в шаблон
            weather_data = {
                'city': city,
                'current': current_weather,
            }
            return render(request, 'index.html', {'weather_data': weather_data, 'form': form})

    else:
        form = CityForm()
    
    return render(request, 'index.html', {'form': form})
