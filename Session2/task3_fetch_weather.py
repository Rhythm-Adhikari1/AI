import requests
import csv
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Location from environment
lat = float(os.getenv('LATITUDE'))
lon = float(os.getenv('LONGITUDE'))

# Fetch weather from API
url = os.getenv('WEATHER_API_URL')
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
    output_file = os.getenv('OUTPUT_WEATHER_CSV')
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'max_temp'])
        
        for date, temp in zip(dates, temps):
            writer.writerow([date, temp])
    
    print(f"Weather data saved to {output_file}")
    
    for date, temp in zip(dates, temps):
        print(date + ": " + str(temp) + " C")
else:
    print("Error getting weather data")
