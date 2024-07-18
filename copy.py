import urllib.request
import json
from django.shortcuts import render
from .forms import CityForm

def get_weather(city):

    coord_response = urllib.request.urlopen(f"https://api.opencagedata.com/geocode/v1/json?q={city}&key=7bfd1f0f7ac642d2a0afb5a327956a45")
    coord_data = json.loads(coord_response.read())
    # print(coord_data)

    if coord_data['results']:
        lat = coord_data['results'][0]['geometry']['lat']
        lng = coord_data['results'][0]['geometry']['lng']
    else:
        return None

    weather_response = urllib.request.urlopen(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,surface_pressure,wind_speed_10m,wind_gusts_10m")
    weather_data = json.loads(weather_response.read())
    print(weather_data)

    return weather_data

def index(request):
    weather_data = None
    city = None

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            weather_data = get_weather(city)
    else:
        form = CityForm()

    return render(request, 'index.html', {'form': form, 'weather_data': weather_data, 'city': city})
