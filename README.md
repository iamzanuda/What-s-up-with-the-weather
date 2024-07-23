# What's Up with the Weather?

This application is designed to retrieve and display weather information for a user-specified city. It uses two main APIs:
- [OpenCage Geocoding API](https://opencagedata.com/) to get the coordinates of the city.
- [Open-Meteo API](https://open-meteo.com/) to fetch weather data.


## Technologies and Libraries Used

- Django 5.0.7
- Python 3.12.3
- Pandas 2.2.2
- HTML/CSS
- Docker
- Unittest
- OpenCage Geocoding API
- Open-Meteo API

## Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:iamzanuda/what-s-up-with-the-weather.git

2. Navigate to the directory with the requirements.txt file:

   ```bash
   cd what-s-up-with-the-weather/backend/

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt

## Usage

1. Start the Django server:

   ```bash
   python manage.py runserver

2. Open a browser and go to http://localhost:8000

   Enter the name of the city in the form on the main page and click the "Find Out" button.

   After submitting the form, you will see the current weather for the specified city and a table with hourly forecasts for the next 6 hours.

## Running the Application in Docker

Install Docker: Follow the instructions on the Docker website to install Docker for your operating system (https://docs.docker.com/get-docker/).

1. Log in to Docker Hub:

   ```bash
   docker login

2. Pull the Docker image:

   ```bash
   docker pull mralmostfreeman/weather_backend:latest
   
3. Run the container:

   ```bash
   docker run --name weather_backend_container --rm -p 8000:8000 mralmostfreeman/weather_backend:latest

Now your application should be accessible at http://localhost:8000

## License

This project is licensed under the MIT License.

## Author

Baramykov Ya.