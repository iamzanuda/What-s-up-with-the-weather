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

# Set up the Open-Meteo API client without caching
openmeteo = Client()

def get_weather_data(request):
    """
    Handles weather data requests from the user.

    This function is designed to handle POST requests from the form,
    fetch weather data for the specified city using the Open-Meteo API and
    OpenCage Geocoding API to obtain city coordinates, process this data,
    and display the results on the web page.

    Args:
        request (HttpRequest): HTTP request from the user.

    Returns:
        HttpResponse: Response with rendered weather data on the web page.
    """

    form = CityForm(request.POST or None)
    weather_data = None

    if request.method == "POST" and form.is_valid():
        city = form.cleaned_data['city']  # Extract city name from form

        # Get city coordinates using OpenCage Geocoding API
        OPEN_CAGE_GEO_API_URL = os.getenv('OPEN_CAGE_GEO_API_URL')
        coord_response = urllib.request.urlopen(OPEN_CAGE_GEO_API_URL)
        coord_data = json.loads(coord_response.read())

        lat = coord_data['results'][0]['geometry']['lat']  # Latitude
        lng = coord_data['results'][0]['geometry']['lng']  # Longitude

        # Set up request parameters for Open-Meteo API
        OPEN_METEO_API_URL = os.getenv('OPEN_METEO_API_URL')
        params = {
            "latitude": lat,
            "longitude": lng,
            "current": [  # Parameters for current weather data
                "temperature_2m",  # Air temperature at 2 meters
                "relative_humidity_2m",  # Relative humidity at 2 meters
                "precipitation",  # Precipitation amount
                "surface_pressure",  # Surface pressure
                "wind_speed_10m",  # Wind speed at 10 meters
                "wind_gusts_10m",  # Wind gusts at 10 meters
            ],
            "hourly": [  # Parameters for hourly weather data
                "temperature_2m",  # Air temperature at 2 meters
                "relative_humidity_2m",  # Relative humidity at 2 meters
                "precipitation_probability",  # Precipitation probability
                "surface_pressure",  # Surface pressure
                "wind_speed_10m",  # Wind speed at 10 meters
                "wind_gusts_10m",  # Wind gusts at 10 meters
            ]
        }

        # Get response from Open-Meteo API
        responses = openmeteo.weather_api(OPEN_METEO_API_URL, params=params)
        response = responses[0]

        # Process current weather data
        current = response.Current()

        def get_value(variable, index):
            """
            Extracts the value of a variable by index.

            Args:
                variable: Variable object to extract value from.
                index (int): Index of the value in the variable.

            Returns:
                float: Rounded value to one decimal place
                    or None if the value could not be obtained.
            """

            try:
                value = variable.Variables(index).Value()
                if isinstance(value, (int, float)):
                    return round(value, 1)
                else:
                    return None
            except (TypeError, IndexError):
                return None

        # Form a dictionary with current weather
        current_weather = {
            "temperature_2m": get_value(current, 0),
            "relative_humidity_2m": get_value(current, 1),
            "precipitation": get_value(current, 2),
            "surface_pressure": get_value(current, 3),
            "wind_speed_10m": get_value(current, 4),
            "wind_gusts_10m": get_value(current, 5),
        }

        # Process hourly forecast data
        hourly = response.Hourly()
        hourly_weather = {
            "hourly_temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "hourly_relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "hourly_precipitation_probability": hourly.Variables(2).ValuesAsNumpy(),
            "hourly_surface_pressure": hourly.Variables(3).ValuesAsNumpy(),
            "hourly_wind_speed_10m": hourly.Variables(4).ValuesAsNumpy(),
            "hourly_wind_gusts_10m": hourly.Variables(5).ValuesAsNumpy(),
        }

        # Create a time series for the next 6 hours from the current time,
        # round the data to the nearest hour, and output only the time information
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

        # Form weather data to pass to the template context
        weather_data = {
            "current": current_weather,
            "hourly": hourly_weather_list,
            "city": city
        }

    # Form context to pass to the template
    context = {
        "form": form,
        "weather_data": weather_data
    }

    return render(request, "index.html", context)
