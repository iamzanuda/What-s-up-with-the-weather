# Приложение "Что там с погодой?"

Это приложение предназначено для получения и отображения информации о погоде для указанного пользователем города. Для этого приложение использует два основных API: [OpenCage Geocoding API](https://opencagedata.com/) для получения координат города и [Open-Meteo API](https://open-meteo.com/) для получения данных о погоде.


## Используемые технологии и библиотеки
- **Django 5.0.7**
- **Python 3.12.3**
- **Pandas 2.2.2**
- **HTML/CSS**
- **Docker**
- **OpenCage Geocoding API**
- **Open-Meteo API**

## Установка

1. Склонируйте репозиторий:

   ```bash
   git clone git@github.com:iamzanuda/what-s-up-with-the-weather.git
   cd what-s-up-with-the-weather

2. Установите зависимости:

   ```bash
   pip install -r requirements.txt

## Использование

1. Запустите Django сервер:

   ```bash
   python manage.py runserver

2. Откройте браузер и перейдите по адресу http://localhost:8000.

   Введите название города в форму на главной странице и нажмите кнопку "Узнать".

   После отправки формы вы увидите текущую погоду для указанного города и таблицу с почасовыми прогнозами на следующие 6 часов.

## Запуск приложения в Docker

Установите Docker: Следуйте инструкциям на сайте Docker для установки Docker на вашу операционную систему (https://docs.docker.com/get-docker/).

1. Войдите в Docker Hub:

   ```bash
   docker login

2. Загрузите образ Docker:

   ```bash
   docker pull mralmostfreeman/weather_backend:latest
   
3. Запустите контейнер:

   ```bash
   docker run --name weather_backend_container --rm -p 8000:8000 mralmostfreeman/weather_backend:latest

Теперь ваше приложение должно быть доступно по адресу http://localhost:8000.

## Лицензия
Этот проект лицензируется в соответствии с лицензией MIT.

## Автор
Барамыков Я.