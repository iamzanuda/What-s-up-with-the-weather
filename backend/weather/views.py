
from urllib import request
from django.shortcuts import render
from .forms import CityForm

def get_weather_data(city):
    url = f"https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m"

    response = request.get(url)
    return response.json()

def index(request):
    weather_data = None
    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            city = form.cleaned_data['city']
            weather_data = get_weather_data(city)
    else:
        form = CityForm()

    return render(
        request,
        'index.html',
        {'form': form, 'weather_data': weather_data}
        )