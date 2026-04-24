import csv

# Read weather.csv
data = []
with open('weather.csv', 'r') as f:
    reader = csv.reader(f)
    header = next(reader)
    
    for row in reader:
        data.append({
            'date': row[0],
            'temp': float(row[1])
        })

if data:
    # Find max and min
    hottest = max(data, key=lambda x: x['temp'])
    coldest = min(data, key=lambda x: x['temp'])
    
    avg = sum(d['temp'] for d in data) / len(data)
    
    # Print results
    print("KATHMANDU WEATHER ANALYSIS")
    print("=" * 50)
    print("Average temp: " + str(round(avg, 2)))
    print("Hottest day: " + hottest['date'] + " - " + str(hottest['temp']) + " C")
    print("Coldest day: " + coldest['date'] + " - " + str(coldest['temp']) + " C")
    print("=" * 50)
    
    print("\nAll days:")
    for item in data:
        print(item['date'] + ": " + str(item['temp']) + " C")
    
    # Save summary
    with open('weather_summary.txt', 'w') as f:
        f.write("KATHMANDU WEATHER FORECAST\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Average temperature: " + str(round(avg, 2)) + " C\n")
        f.write("Hottest day: " + hottest['date'] + " - " + str(hottest['temp']) + " C\n")
        f.write("Coldest day: " + coldest['date'] + " - " + str(coldest['temp']) + " C\n\n")
        
        f.write("7-day forecast:\n")
        f.write("-" * 50 + "\n")
        for item in data:
            f.write(item['date'] + ": " + str(item['temp']) + " C\n")
    
    print("\nSummary saved to weather_summary.txt")
else:
    print("No data found")
