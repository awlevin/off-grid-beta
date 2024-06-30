import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

def get_weather_data(city, coordinates, time_range):
    
    # Prioritize lat/long coordinates if provided
    if coordinates:
      url = f"http://api.openweathermap.org/data/2.5/forecast?lat={coordinates[0]}&lon={coordinates[1]}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
    elif city:
      url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"
    else:
      raise ValueError("No location or coordinates provided.")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None