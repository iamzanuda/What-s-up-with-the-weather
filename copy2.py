import datetime
import json
import urllib.request

import pandas as pd
from openmeteo_requests import Client


# Setup the Open-Meteo API client without caching
openmeteo = Client()

# Получаем координаты города Москва с помощью OpenCage Geocoding API
coord_response = urllib.request.urlopen(f"https://api.opencagedata.com/geocode/v1/json?q=Moscow&key=7bfd1f0f7ac642d2a0afb5a327956a45")
coord_data = json.loads(coord_response.read())

lat = coord_data['results'][0]['geometry']['lat']
lng = coord_data['results'][0]['geometry']['lng']

# Устанавливаем параметры для запроса к Open-Meteo API
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lng,
    "current": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "surface_pressure",
        "wind_speed_10m",
        "wind_gusts_10m",
    ],
    "hourly": [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation_probability",
        "surface_pressure",
        "wind_speed_10m",
        "wind_gusts_10m",
    ]
}

# Получаем ответы от Open-Meteo API
responses = openmeteo.weather_api(url, params=params)

# Обрабатываем первый ответ (можно добавить цикл для обработки
# нескольких ответов или моделей погоды)
response = responses[0]
# print(response)

# Обработка текущих данных
current = response.Current()


# Проверка и обработка текущих данных
def safe_get_value(variable, index):
    try:
        value = variable.Variables(index).Value()
        if isinstance(value, (int, float)):
            return round(value, 1)
        else:
            return None
    except (TypeError, IndexError):
        return None


current_weather = {
    "current_temperature_2m": safe_get_value(current, 0),
    "current_relative_humidity_2m": safe_get_value(current, 1),
    "current_precipitation": safe_get_value(current, 2),
    "current_surface_pressure": safe_get_value(current, 3),
    "current_wind_speed_10m": safe_get_value(current, 4),
    "current_wind_gusts_10m": safe_get_value(current, 5),
}

# Обработка почасовых данных
hourly = response.Hourly()
hourly_weather = {
    "hourly_temperature_2m":
        hourly.Variables(0).ValuesAsNumpy(),
    "hourly_relative_humidity_2m":
        hourly.Variables(1).ValuesAsNumpy(),
    "hourly_precipitation_probability":
        hourly.Variables(2).ValuesAsNumpy(),
    "hourly_surface_pressure":
        hourly.Variables(3).ValuesAsNumpy(),
    "hourly_wind_speed_10m":
        hourly.Variables(4).ValuesAsNumpy(),
    "hourly_wind_gusts_10m":
        hourly.Variables(5).ValuesAsNumpy(),
}

# Создаем временной ряд на 6 часов вперед от текущего времени
# и округляем в сторону ближайшего часа.
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

# Преобразуем временной ряд в список строк времени в нужном формате
time_strings = [str(ts) for ts in time_range]

# Создаем DataFrame для почасовых данных и округляем данные до целого числа.
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

# Фильтрация данных hourly_data по временному ряду
filtered_hourly_data = hourly_dataframe[
    hourly_dataframe['date'].isin(time_datetimes)
]

# Вывод отфильтрованных данных
for _, data in filtered_hourly_data.iterrows():
    print(f"Дата: {data['date']}, Температура: {data['temperature_2m']}°C, "
          f"Влажность: {data['relative_humidity_2m']}%, "
          f"Вероятность осадков: {data['precipitation_probability']}%, "
          f"Давление: {data['surface_pressure']} hPa, "
          f"Скорость ветра: {data['wind_speed_10m']} м/c, "
          f"Порывы ветра: {data['wind_gusts_10m']} м/c")
