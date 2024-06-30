from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from weather_api import get_weather_data
from weather_formatter import format_weather_forecast

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_reply():
    body = request.get_data('Body', as_text=True)
    resp = MessagingResponse()

    if body:
        location, time_range = parse_input(body)
        weather_data = get_weather_data(location)
        
        if weather_data:
            formatted_forecast = format_weather_forecast(weather_data['list'])
            resp.message(formatted_forecast)
        else:
            resp.message("Sorry, I couldn't find weather data for that location. Please try again with a different city name.")

    else:
        resp.message("Please send the name of your nearest city or location.")

    return str(resp)

def parse_input(input_string):
    parts = input_string.split(',')
    location = parts[0].strip()
    time_range = None
    if len(parts) > 1:
        time_range = parts[1].strip()
    return location, time_range

if __name__ == '__main__':
    app.run(debug=True)