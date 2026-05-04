import requests
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Step 1: Fetch 7-day weather data for 3 cities using Open-Meteo API
def fetch_weather_data():
    """Fetch 7-day weather forecast for 3 cities"""
    cities = {
        "London": {"lat": 51.5074, "lon": -0.1278},
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "Tokyo": {"lat": 35.6762, "lon": 139.6503}
    }
    
    weather_data = {}
    
    for city, coords in cities.items():
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "daily": "temperature_2m_max,temperature_2m_min,relative_humidity_2m_max",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            weather_data[city] = {
                "dates": data["daily"]["time"],
                "max_temps": data["daily"]["temperature_2m_max"],
                "min_temps": data["daily"]["temperature_2m_min"],
                "humidity": data["daily"]["relative_humidity_2m_max"]
            }
            print(f"[OK] Successfully fetched data for {city}")
        except Exception as e:
            print(f"[ERROR] Error fetching data for {city}: {e}")
    
    return weather_data

# Step 2: Create MySQL connection
def create_connection():
    """Create a connection to MySQL server"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            port=int(os.getenv("DB_PORT", 3306))
        )
        return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None

# Step 3: Create database and table
def create_database(conn):
    """Create MySQL database with forecasts table"""
    cursor = conn.cursor()
    
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS weather_db")
        print("[OK] Database 'weather_db' created/verified")
        
        # Use the database
        cursor.execute("USE weather_db")
        
        # Drop table if exists (for fresh runs)
        cursor.execute("DROP TABLE IF EXISTS forecasts")
        
        # Create forecasts table with humidity column
        cursor.execute("""
            CREATE TABLE forecasts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                city VARCHAR(100) NOT NULL,
                date VARCHAR(20) NOT NULL,
                max_temp DECIMAL(5, 2) NOT NULL,
                min_temp DECIMAL(5, 2) NOT NULL,
                humidity INT
            )
        """)
        
        conn.commit()
        print("[OK] Table 'forecasts' created successfully")
        return True
    except Error as e:
        print(f"[ERROR] Error creating database/table: {e}")
        return False

# Step 4: Insert all data into database
def insert_weather_data(conn, weather_data):
    """Insert 21 rows (3 cities × 7 days) into the database"""
    cursor = conn.cursor()
    rows_inserted = 0
    
    insert_query = """
    INSERT INTO forecasts (city, date, max_temp, min_temp, humidity)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        for city, data in weather_data.items():
            for i in range(7):  # 7 days
                cursor.execute(insert_query, (
                    city,
                    data["dates"][i],
                    data["max_temps"][i],
                    data["min_temps"][i],
                    data["humidity"][i]
                ))
                rows_inserted += 1
        
        conn.commit()
        print(f"[OK] Inserted {rows_inserted} rows into database")
    except Error as e:
        print(f"[ERROR] Error inserting data: {e}")

# Step 5: Query 1 - Which city has the highest average max temperature?
def query_highest_avg_temp(conn):
    """Find the city with highest average maximum temperature"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE weather_db")
        cursor.execute("""
            SELECT city, ROUND(AVG(max_temp), 2) as avg_max_temp
            FROM forecasts
            GROUP BY city
            ORDER BY avg_max_temp DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f" Error in query 1: {e}")
        return None

# Step 6: Query 2 - Find the single hottest day across all cities
def query_hottest_day(conn):
    """Find the single hottest day across all 3 cities"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE weather_db")
        cursor.execute("""
            SELECT city, date, max_temp
            FROM forecasts
            ORDER BY max_temp DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f" Error in query 2: {e}")
        return None

# Step 7: Query 3 - Find days where temperature difference > 10°C
def query_large_temp_diff(conn):
    """Find days where max_temp - min_temp > 10°C"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE weather_db")
        cursor.execute("""
            SELECT city, date, max_temp, min_temp, ROUND(max_temp - min_temp, 2) as temp_diff
            FROM forecasts
            WHERE (max_temp - min_temp) > 10
            ORDER BY temp_diff DESC
        """)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in query 3: {e}")
        return []

# Step 8: Generate summary report
def generate_summary_report(conn, q1_result, q2_result, q3_results, db_name="weather_db"):
    """Generate summary report and save to summary.txt"""
    
    summary = []
    summary.append("WEATHER DATA ANALYSIS REPORT")
    summary.append("")
    
    # Fetch database statistics
    cursor = conn.cursor()
    try:
        cursor.execute("USE weather_db")
        
        cursor.execute("SELECT COUNT(*) FROM forecasts")
        total_records = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT city) FROM forecasts")
        total_cities = cursor.fetchone()[0]
        
        summary.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Database: {db_name}")
        summary.append(f"Total Records: {total_records} (3 cities × 7 days)")
        summary.append("")
        
        # Query 1 Results
        summary.append("QUERY 1: City with Highest Average Maximum Temperature")
        if q1_result:
            city, avg_temp = q1_result
            summary.append(f"City: {city}")
            summary.append(f"Average Max Temperature: {avg_temp}°C")
        summary.append("")
        
        # Query 2 Results
        summary.append("QUERY 2: Hottest Day Across All Cities")
        if q2_result:
            city, date, max_temp = q2_result
            summary.append(f"City: {city}")
            summary.append(f"Date: {date}")
            summary.append(f"Maximum Temperature: {max_temp}°C")
        summary.append("")
        
        # Query 3 Results
        summary.append("QUERY 3: Days with Temperature Difference > 10°C")
        if q3_results:
            summary.append(f"Found {len(q3_results)} day(s) with temperature difference > 10°C:\n")
            for city, date, max_temp, min_temp, temp_diff in q3_results:
                summary.append(f"  • {city} on {date}: Max {max_temp}°C, Min {min_temp}°C (Diff: {temp_diff}°C)")
        else:
            summary.append("No days found with temperature difference > 10°C")
        summary.append("")
        
        # Temperature Statistics
        summary.append("TEMPERATURE STATISTICS")
        
        cursor.execute("SELECT city, ROUND(MIN(min_temp), 2), ROUND(MAX(max_temp), 2), ROUND(AVG((max_temp + min_temp) / 2), 2) FROM forecasts GROUP BY city ORDER BY city")
        stats = cursor.fetchall()
        for city, min_t, max_t, avg_t in stats:
            summary.append(f"{city:12} | Lowest: {min_t:6}°C | Highest: {max_t:6}°C | Average: {avg_t:6}°C")
        summary.append("")
        
        # Humidity Statistics
        summary.append("HUMIDITY STATISTICS (Bonus Feature)")
        
        cursor.execute("SELECT city, ROUND(AVG(humidity), 1) as avg_humidity FROM forecasts GROUP BY city ORDER BY city")
        humidity_stats = cursor.fetchall()
        for city, avg_humidity in humidity_stats:
            summary.append(f"{city:12} | Average Humidity: {avg_humidity}%")
        summary.append("")
        
        # Save to file
        report_text = "\n".join(summary)
        with open("summary.txt", "w", encoding="utf-8") as f:
            f.write(report_text)
        
        print("[OK] Summary report generated: summary.txt")
        return report_text
        
    except Error as e:
        print(f"[ERROR] Error generating report: {e}")
        return ""

# Main execution
if __name__ == "__main__":
    print("Starting Weather Data Analysis Task...\n")
    
    # Step 1: Fetch weather data
    print("Step 1: Fetching weather data from Open-Meteo API...")
    weather_data = fetch_weather_data()
    print()
    
    # Step 2: Create MySQL connection
    print("Step 2: Connecting to MySQL database...")
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL server")
        exit(1)
    print()
    
    # Step 3: Create database and table
    print("Step 3: Creating database and table...")
    if not create_database(conn):
        print("Failed to create database")
        conn.close()
        exit(1)
    print()
    
    # Step 4: Insert data
    print("Step 4: Inserting weather data...")
    insert_weather_data(conn, weather_data)
    print()
    
    # Run queries
    print("Step 5-7: Running analysis queries...\n")
    q1_result = query_highest_avg_temp(conn)
    if q1_result:
        city, avg_temp = q1_result
        print(f"Query 1 Result: City '{city}' has highest avg max temp of {avg_temp}°C")
    q2_result = query_hottest_day(conn)
    if q2_result:
        city, date, temp = q2_result
        print(f"Query 2 Result: Hottest day is {date} in {city} with {temp}°C")
    
    q3_results = query_large_temp_diff(conn)
    print(f"Query 3 Result: Found {len(q3_results)} day(s) with temp difference > 10°C")
    print()
    
    # Generate summary report
    print("Step 8: Generating summary report...")
    report = generate_summary_report(conn, q1_result, q2_result, q3_results)
    print()
    
    # Display report
    print("SUMMARY REPORT:")
    print(report)
    
    conn.close()
    print("\n[OK] Task completed successfully!")
