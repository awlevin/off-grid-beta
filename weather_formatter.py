from datetime import datetime

def get_weather_emoji(description):
    emoji_map = {
        'clear sky': '☀️',
        'few clouds': '🌤️',
        'scattered clouds': '⛅',
        'broken clouds': '🌥️',
        'overcast clouds': '☁️',
        'light rain': '🌦️',
        'rain': '🌧️',
        'thunderstorm': '⛈️',
        'snow': '❄️',
        'mist': '🌫️'
    }
    return emoji_map.get(description.lower(), '🌡️')

def format_temperature(temp_min, temp_max):
    if abs(temp_min - temp_max) < 2:
        return f"{temp_min:.1f}°F"
    return f"{temp_min:.1f}°F - {temp_max:.1f}°F"

def format_time(time_str):
    return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").strftime("%I %p").lstrip('0')

def group_by_date(forecasts):
    grouped = {}
    for forecast in forecasts:
        date = forecast['dt_txt'].split()[0]
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(forecast)
    return grouped

def format_weather_forecast(forecasts):
    grouped_forecasts = group_by_date(forecasts)
    formatted_output = ""

    for date, day_forecasts in grouped_forecasts.items():
        formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d")
        formatted_output += f"\n{formatted_date}:\n"

        current_condition = None
        start_time = None
        temps = []

        for forecast in day_forecasts:
            temp = forecast['main']['temp']
            condition = forecast['weather'][0]['description']
            time = format_time(forecast['dt_txt'])

            if condition != current_condition:
                if current_condition:
                    emoji = get_weather_emoji(current_condition)
                    temp_range = format_temperature(min(temps), max(temps))
                    formatted_output += f"  {start_time} - {time}: {temp_range} {emoji} {current_condition}\n"
                
                current_condition = condition
                start_time = time
                temps = [temp]
            else:
                temps.append(temp)

        # Add the last condition of the day
        if current_condition:
            emoji = get_weather_emoji(current_condition)
            temp_range = format_temperature(min(temps), max(temps))
            formatted_output += f"  {start_time} - {time}: {temp_range} {emoji} {current_condition}\n"

    return formatted_output.strip()