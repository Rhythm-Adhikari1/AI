import requests
import csv

# Kathmandu location
lat = 27.72
lon = 85.32

# Fetch weather from API
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "daily": "temperature_2m_max",
    "timezone": "auto"
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    
    dates = data['daily']['time']
    temps = data['daily']['temperature_2m_max']
    
    # Save to CSV
    with open('weather.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'max_temp'])
        
        for date, temp in zip(dates, temps):
            writer.writerow([date, temp])
    
    print("Weather data saved to weather.csv")
    
    for date, temp in zip(dates, temps):
        print(date + ": " + str(temp) + " C")
else:
    print("Error getting weather data")
