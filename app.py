from flask import Flask, render_template, request
import requests
import geocoder
from collections import defaultdict

app = Flask(__name__)

API_KEY = 'bc14876e0cb7fe1c35f038efaec12a09'  # Replace with your own if needed

# Function to get current weather
def get_weather(city):
    urls = [
        f"https://api.openweathermap.org/data/2.5/weather?q={city},IN&appid={API_KEY}&units=metric",
        f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    ]
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    return None

# Function to get 5-day forecast
def get_forecast(city):
    urls = [
        f"https://api.openweathermap.org/data/2.5/forecast?q={city},IN&appid={API_KEY}&units=metric",
        f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    ]
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        city = request.form['city'].strip().title()
    else:
        g = geocoder.ip('me')
        city = g.city.strip().title() if g.city else 'Delhi'

    print(f"Looking up weather for: {city}")
    data = get_weather(city)

    if data:
        weather = {
            'city': city,
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon']
        }
    else:
        weather = {'error': f"City '{city}' not found. Please try another one."}

    return render_template('index.html', weather=weather)

@app.route('/forecast/<city>')
def forecast(city):
    city = city.strip().title()
    data = get_forecast(city)

    if not data:
        return f"Forecast not available for {city}"

    daily = defaultdict(list)
    for entry in data['list']:
        date = entry['dt_txt'].split(' ')[0]
        daily[date].append(entry)

    result = []
    for date, entries in list(daily.items())[:5]:  # Show 5 days
        mid = next((e for e in entries if "12:00:00" in e['dt_txt']), entries[0])
        result.append({
            'date': date,
            'temp': mid['main']['temp'],
            'desc': mid['weather'][0]['description'].title(),
            'icon': mid['weather'][0]['icon']
        })

    return render_template('forecast.html', forecasts=result, city=city)

if __name__ == '__main__':
    app.run(debug=True)
