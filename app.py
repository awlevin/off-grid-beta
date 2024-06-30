from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from weather_api import get_weather_data
from weather_formatter import format_weather_forecast
from datetime import datetime, timezone

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_reply():
  body = request.get_data('Body', as_text=True)
  resp = MessagingResponse()

  if body:
    city, coordinates, time_range = parse_input(body)
    print(city, coordinates, time_range)
    weather_data = get_weather_data(city, coordinates, time_range)
    
    if weather_data:
      formatted_forecast = format_weather_forecast(weather_data['list'])
      resp.message(formatted_forecast)
    else:
      resp.message("Sorry, I couldn't find weather data for that location. Please try again with a different city name.")

  else:
    resp.message("Please send the name of your nearest city or location.")

  return str(resp)

def parse_input(input_string):

  """
  Parse the input string to determine the location and time range requested by the user.

  Parameters:
  input_string (str): The user's input string.

  Returns:
    city, coordinates (tuple), time_range (tuple)
    city may be None if coordinates are provided.
    time_range not required
  """

  # User can specify:
  ## Coordinates
  ## `Coordinates -- e.g. `39.32758, -106.12928`
  ## `Coordinates, time range` -- e.g. `39.32758, -106.12928, 3am-6pm`

  city = None
  coordinates = None
  time_range = None

  parts = input_string.split(',')

  if len(parts) < 1:
    raise ValueError("Invalid input format. Please provide a city name or coordinates.")
  elif len(parts) == 1:
    # Only city provided
    city = parts[0].strip()
  elif len(parts) == 2:
    # Only coordinates provided, or city and time range

    # If first part is a number, assume it's coordinates
    if is_number(parts[0]):
      coordinates = parts[0].strip(), parts[1].strip()
    else:
      city = parts[0].strip()
      time_range = process_time_range(parts[1].strip())
  elif len(parts) == 3:
    # Coordinates and time range provided
    coordinates = parts[0].strip(), parts[1].strip()
    time_range = process_time_range(parts[2].strip())  

  return city, coordinates, time_range

def process_time_range(s):
  """
  Formats the time range string provided by the user.

  Parameters:
  s (str): The time range string provided by the user. Example: "3am-6pm" or " 3pm - 6pm"

  Returns:
    tuple: A tuple of two UTC timestamps representing the start and end time of the range.
  """
  
  # Remove any leading/trailing whitespace
  s = s.strip()

  # Split the time range string into two parts
  start_time, end_time = s.split('-')

  # Parse the start and end times
  start_time = parse_time(start_time)
  end_time = parse_time(end_time)

  return start_time, end_time

def parse_time(s):
  """
  Parses the time string provided by the user and returns a UTC timestamp.

  Parameters:
  s (str): The time string provided by the user. Example: "3am" or "6pm"

  Returns:
    int: A UTC timestamp representing the time.
  """
  
  # Remove any leading/trailing whitespace
  s = s.strip()

  # Parse the time string
  time = datetime.strptime(s, "%I%p").time()
  
  # Combine with today's date
  today = datetime.now().date()
  combined_datetime = datetime.combine(today, time)
  
  # Convert the time to a UTC timestamp
  utc_time = combined_datetime.replace(tzinfo=timezone.utc)
  print(utc_time)

  # Convert the time to a UTC timestamp
  return int(utc_time.timestamp())

def is_number(s):
  # have to do this to safely check for positive/negative, int/float without crashing
  # isdigit() doesn't work for negative numbers
  # isnumeric() doesn't work for floats
  try:
    float(s)
    return True
  except ValueError:
    return False

if __name__ == '__main__':
  app.run(port=3001, debug=True)