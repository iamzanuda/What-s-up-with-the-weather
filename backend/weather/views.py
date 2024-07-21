import datetime
import json
import os
import urllib.request

import pandas as pd
from django.shortcuts import render
from dotenv import load_dotenv
from openmeteo_requests import Client

from .forms import CityForm

load_dotenv()

# Устанавливаем клиент Open-Meteo API без кеширования
openmeteo = Client()


def get_weather_data(request):
    """
    Обрабатывает запрос данных о погоде от пользователя.

    Эта функция предназначена для обработки POST-запроса от формы,
    получения данных о погод для указанного города с использованием
    API Open-Meteo и API OpenCage Geocoding для получения координат города,
    обработки этих данных и вывода результатов на веб-страницу.

    Args:
        request (HttpRequest): HTTP-запрос от пользователя.

    Returns:
        HttpResponse: Ответ с отрендеренными данными о погоде на веб-странице.
    """

    form = CityForm(request.POST or None)
    weather_data = None

    if request.method == "POST" and form.is_valid():
        city = form.cleaned_data['city']  # Извлечение названия города из формы

        # Получение координат города с помощью OpenCage Geocoding API
        OPEN_CAGE_GEO_API_URL = os.getenv('OPEN_CAGE_GEO_API_URL')
        coord_response = urllib.request.urlopen(OPEN_CAGE_GEO_API_URL)
        coord_data = json.loads(coord_response.read())

        lat = coord_data['results'][0]['geometry']['lat']  # Широта
        lng = coord_data['results'][0]['geometry']['lng']  # Долгота

        # Установка параметров запроса к Open-Meteo API
        OPEN_METEO_API_URL = os.getenv('OPEN_METEO_API_URL')
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": [  # Параметры для получения текущих погодных данных
                "temperature_2m",  # Температура воздуха на высоте 2 метра
                "relative_humidity_2m",  # Относительная влажность на высоте 2 метра
                "precipitation",  # Количество осадков
                "surface_pressure",  # Атмосферное давление на уровне поверхности
                "wind_speed_10m",  # Скорость ветра на высоте 10 метров
                "wind_gusts_10m",  # Порывы ветра на высоте 10 метров
            ],
            "hourly": [  # Параметры для получения почасовых погодных данных
                "temperature_2m",  # Температура воздуха на высоте 2 метра
                "relative_humidity_2m",  # Относительная влажность на высоте 2 метра
                "precipitation_probability",  # Вероятность осадков
                "surface_pressure",  # Атмосферное давление на уровне поверхности
                "wind_speed_10m",  # Скорость ветра на высоте 10 метров
                "wind_gusts_10m",  # Порывы ветра на высоте 10 метров
            ]
        }

        # Получение ответа от Open-Meteo API
        responses = openmeteo.weather_api(OPEN_METEO_API_URL, params=params)
        response = responses[0]

        # Обработка текущих данных о погоде
        current = response.Current()

        def get_value(variable, index):
            """
            Извлекает значение переменной по индексу.

            Args:
                variable: Объект переменной для извлечения значения.
                index (int): Индекс значения в переменной.

            Returns:
                float: Округленное до одной десятой значение переменной
                    или None, если значение не удалось получить.
            """

            try:
                value = variable.Variables(index).Value()
                if isinstance(value, (int, float)):
                    return round(value, 1)
                else:
                    return None
            except (TypeError, IndexError):
                return None

        # Формирование словаря с текущей погодой
        current_weather = {
            "temperature_2m": get_value(current, 0),
            "relative_humidity_2m": get_value(current, 1),
            "precipitation": get_value(current, 2),
            "surface_pressure": get_value(current, 3),
            "wind_speed_10m": get_value(current, 4),
            "wind_gusts_10m": get_value(current, 5),
        }

        # Обработка данных почасового прогноза
        hourly = response.Hourly()
        hourly_weather = {
            "hourly_temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "hourly_relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "hourly_precipitation_probability": hourly.Variables(2).ValuesAsNumpy(),
            "hourly_surface_pressure": hourly.Variables(3).ValuesAsNumpy(),
            "hourly_wind_speed_10m": hourly.Variables(4).ValuesAsNumpy(),
            "hourly_wind_gusts_10m": hourly.Variables(5).ValuesAsNumpy(),
        }

        # Создание временного ряда на 6 часов вперед от текущего времени,
        # округление данных до ближайшего целого часа и вывод
        # только информации о времени
        current_time = datetime.datetime.now().replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        end_time = current_time + datetime.timedelta(hours=6)

        time_range = pd.date_range(
            start=current_time,
            end=end_time,
            freq='h',
        )
        
        time_strings = [ts.strftime('%H:%M') for ts in time_range]

        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly_weather[
                "hourly_temperature_2m"].round(0).astype(int),
            "relative_humidity_2m": hourly_weather[
                "hourly_relative_humidity_2m"].round(0).astype(int),
            "precipitation_probability": hourly_weather[
                "hourly_precipitation_probability"].round(0).astype(int),
            "surface_pressure": hourly_weather[
                "hourly_surface_pressure"].round(0).astype(int),
            "wind_speed_10m": hourly_weather[
                "hourly_wind_speed_10m"].round(0).astype(int),
            "wind_gusts_10m": hourly_weather[
                "hourly_wind_gusts_10m"].round(0).astype(int),
        }

        hourly_dataframe = pd.DataFrame(data=hourly_data)
        time_datetimes = pd.to_datetime(time_strings).tz_localize('UTC')

        filtered_hourly_data = hourly_dataframe[
            hourly_dataframe['date'].isin(time_datetimes)]

        hourly_weather_list = []
        for _, data in filtered_hourly_data.iterrows():
            hourly_weather_list.append({
                "date": data['date'].strftime('%H:%M'),
                "temperature_2m": data['temperature_2m'],
                "relative_humidity_2m": data['relative_humidity_2m'],
                "precipitation_probability": data['precipitation_probability'],
                "surface_pressure": data['surface_pressure'],
                "wind_speed_10m": data['wind_speed_10m'],
                "wind_gusts_10m": data['wind_gusts_10m']
            })

        # Формирование данных о погоде для передачи в контекст шаблона
        weather_data = {
            "current": current_weather,
            "hourly": hourly_weather_list,
            "city": city
        }

    # Формирование контекста для передачи в шаблон
    context = {
        "form": form,
        "weather_data": weather_data
    }

    return render(request, "index.html", context)
