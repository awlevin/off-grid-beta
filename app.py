import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# OpenWeatherMap API key
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get the message body from the incoming SMS
    location = request.get_data("body").decode("utf-8") # Expecting just a city name

    # Create a Twilio response object
    resp = MessagingResponse()

    if location:
        # Fetch weather data for the given location
        weather_data = get_weather_data(location)
        
        if weather_data:
            # Format the weather data into a readable message
            message = format_weather_message(weather_data)
        else:
            message = "Sorry, I couldn't find weather data for that location. Please try again with a different city name."

        # Add the message to the response
        resp.message(message)
    else:
        resp.message("Please send the name of your nearest city or location.")

    return str(resp)

def get_weather_data(location):
    # OpenWeatherMap API endpoint for hourly forecast
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric"

    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def format_weather_message(weather_data):
    city = weather_data['city']['name']
    country = weather_data['city']['country']
    message = f"Weather forecast for {city}, {country}:\n\n"

    for forecast in weather_data['list'][:12]:  # Get next 12 hours
        timestamp = forecast['dt']
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
        
        # Convert timestamp to hour
        hour = datetime.fromtimestamp(timestamp).strftime('%I %p')
        
        message += f"{hour}: {temp:.1f}°C, {description}\n"

    return message

if __name__ == '__main__':
    app.run(debug=True)