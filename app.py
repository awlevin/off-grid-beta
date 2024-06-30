import os
import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

def parse_input(input_string):
    parts = input_string.split(',')
    location = parts[0].strip()
    time_range = None
    if len(parts) > 1:
        time_range = parts[1].strip()
    return location, time_range

def format_weather_message(weather_data, time_range=None):
    city = weather_data['city']['name']
    country = weather_data['city']['country']
    message = f"Weather forecast for {city}, {country}:\n\n"

    forecasts = weather_data['list']

    if time_range:
        return message + format_detailed_forecast(forecasts, time_range)
    else:
        return message + format_summarized_forecast(forecasts)

def format_detailed_forecast(forecasts, time_range):
    start_time, end_time = parse_time_range(time_range)
    message = ""
    for forecast in forecasts:
        timestamp = forecast['dt']
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
        
        hour = datetime.fromtimestamp(timestamp)
        if start_time <= hour.time() <= end_time:
            message += f"{hour.strftime('%Y-%m-%d %I %p')}: {temp:.1f}°F, {description}\n"
    
    return message.strip()

def format_summarized_forecast(forecasts):
    message = ""
    current_condition = None
    start_time = None
    temp_range = []

    for forecast in forecasts:
        timestamp = forecast['dt']
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
        
        hour = datetime.fromtimestamp(timestamp)

        if description != current_condition:
            if current_condition:
                message += format_condition_range(start_time, hour, temp_range, current_condition)
            current_condition = description
            start_time = hour
            temp_range = [temp]
        else:
            temp_range.append(temp)

    # Add the last condition
    if current_condition:
        message += format_condition_range(start_time, hour, temp_range, current_condition)

    return message.strip()

def format_condition_range(start, end, temp_range, condition):
    if start.date() == end.date():
        time_range = f"{start.strftime('%I %p')} - {end.strftime('%I %p')}"
    else:
        time_range = f"{start.strftime('%Y-%m-%d %I %p')} - {end.strftime('%Y-%m-%d %I %p')}"
    
    min_temp = min(temp_range)
    max_temp = max(temp_range)
    if abs(min_temp - max_temp) < 1:
        temp_str = f"{min_temp:.1f}°F"
    else:
        temp_str = f"{min_temp:.1f}°F - {max_temp:.1f}°F"
    
    return f"{time_range}: {temp_str}, {condition}\n"

def parse_time_range(time_range_str):
    try:
        start, end = time_range_str.split('-')
        start_time = datetime.strptime(start.strip(), "%I%p").time()
        end_time = datetime.strptime(end.strip(), "%I%p").time()
        return start_time, end_time
    except ValueError:
        return None, None

@app.route('/sms', methods=['POST'])
def sms_reply():
    body = request.get_data('Body', as_text=True)
    logger.debug(f"Received SMS with body: {body}")

    resp = MessagingResponse()

    if body:
        location, time_range = parse_input(body)
        weather_data = get_weather_data(location)
        
        if weather_data:
            message = format_weather_message(weather_data, time_range)
            logger.info(f"Sending weather data for location: {location}")
        else:
            message = "Sorry, I couldn't find weather data for that location. Please try again with a different city name."
            logger.warning(f"Failed to fetch weather data for location: {location}")

        resp.message(message)
    else:
        resp.message("Please send the name of your nearest city or location.")
        logger.warning("Received empty message body")

    return str(resp)

def get_weather_data(location):
    # OpenWeatherMap API endpoint for hourly forecast
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=imperial"

    logger.debug(f"Fetching weather data from URL: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        logger.debug("Successfully fetched weather data")
        return response.json()
    else:
        logger.error(f"Failed to fetch weather data. Status code: {response.status_code}")
        return None

if __name__ == '__main__':
    app.run(port=3001, debug=True)