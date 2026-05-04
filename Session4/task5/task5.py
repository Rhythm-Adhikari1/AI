"""
TASK 05 - CAPSTONE PROJECT: Complete Automated Data System
Combines Week 1 (File Handling), Week 2 (Database), Week 3 (APIs)
Fetches, stores, analyzes, and exports data with comprehensive error handling
"""

import requests
import mysql.connector
from mysql.connector import Error
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 3306))
}

# ==================== CONFIGURATION ====================

API_URL = "https://jsonplaceholder.typicode.com/users"
DB_NAME = "capstone_db"
TABLE_NAME = "users_data"
OUTPUT_DIR = "capstone_output"
CSV_FILE = os.path.join(OUTPUT_DIR, "analysis_results.csv")
TXT_FILE = os.path.join(OUTPUT_DIR, "analysis_report.txt")

# ==================== UTILITY FUNCTIONS ====================

def create_output_directory():
    """Create output directory for exports"""
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"[OK] Created output directory: {OUTPUT_DIR}")
        return True
    except Exception as e:
        print(f"[ERROR] Error creating output directory: {e}")
        return False

# ==================== API FUNCTIONS ====================

def fetch_data(api_url, timeout=10):
    """
    Fetch data from public API with error handling
    Week 3 Skill: API Integration
    
    Args:
        api_url: URL of the API endpoint
        timeout: Request timeout in seconds
    
    Returns:
        list: JSON data from API, or empty list on error
    """
    try:
        print(f"[INFO] Fetching data from: {api_url}")
        response = requests.get(api_url, timeout=timeout)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        print(f"[OK] Successfully fetched {len(data)} records from API")
        return data
    
    except requests.exceptions.Timeout:
        print(f"[ERROR] API request timed out after {timeout} seconds")
        return []
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - unable to reach API")
        return []
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP Error: {e.response.status_code} - {e.response.reason}")
        return []
    except requests.exceptions.JSONDecodeError:
        print("[ERROR] Invalid JSON response from API")
        return []
    except Exception as e:
        print(f"[ERROR] Unexpected error fetching data: {e}")
        return []

# ==================== DATABASE FUNCTIONS ====================

def create_connection():
    """Create connection to MySQL server"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None

def create_database_and_table(conn):
    """
    Create database and users_data table
    Week 2 Skill: Database Management
    """
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"[OK] Database '{DB_NAME}' created/verified")
        
        # Use database
        cursor.execute(f"USE {DB_NAME}")
        
        # Drop existing table for fresh run
        cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        
        # Create users_data table with proper schema
        create_table_query = f"""
        CREATE TABLE {TABLE_NAME} (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            phone VARCHAR(30),
            website VARCHAR(100),
            company_name VARCHAR(150),
            city VARCHAR(100),
            latitude DECIMAL(10, 8),
            longitude DECIMAL(11, 8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"[OK] Table '{TABLE_NAME}' created successfully")
        return True
    
    except Error as e:
        print(f"[ERROR] Error creating database/table: {e}")
        return False

def store_data(conn, data):
    """
    Store fetched API data in MySQL
    Week 2 Skill: Data Storage with Error Handling
    """
    cursor = conn.cursor()
    inserted_count = 0
    error_count = 0
    
    insert_query = f"""
    INSERT INTO {TABLE_NAME} 
    (id, name, email, phone, website, company_name, city, latitude, longitude)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for record in data:
            try:
                # Extract nested JSON data safely
                company_name = record.get("company", {}).get("name", "Unknown")
                city = record.get("address", {}).get("city", "Unknown")
                lat = record.get("address", {}).get("geo", {}).get("lat")
                lon = record.get("address", {}).get("geo", {}).get("lng")
                
                # Convert to float if available
                lat = float(lat) if lat else None
                lon = float(lon) if lon else None
                
                cursor.execute(insert_query, (
                    record.get("id"),
                    record.get("name"),
                    record.get("email"),
                    record.get("phone"),
                    record.get("website"),
                    company_name,
                    city,
                    lat,
                    lon
                ))
                inserted_count += 1
            
            except Error as e:
                print(f"  [WARN] Error inserting record ID {record.get('id')}: {e}")
                error_count += 1
                continue
        
        conn.commit()
        print(f"[OK] Stored {inserted_count} records in database")
        if error_count > 0:
            print(f"  [WARN] {error_count} records failed to insert")
        
        return inserted_count > 0
    
    except Error as e:
        print(f"[ERROR] Error storing data: {e}")
        return False

# ==================== ANALYSIS QUERIES ====================

def query_users_by_city(conn):
    """
    Query 1: Get user count per city
    Week 3 Skill: SQL Analysis
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute(f"""
            SELECT city, COUNT(*) as user_count
            FROM {TABLE_NAME}
            GROUP BY city
            ORDER BY user_count DESC
        """)
        results = cursor.fetchall()
        return ("Users by City", ["city", "user_count"], results)
    
    except Error as e:
        print(f"[ERROR] Error in Query 1: {e}")
        return ("Users by City", [], [])

def query_companies_with_email_domains(conn):
    """
    Query 2: Get companies and their email domain statistics
    Week 3 Skill: SQL Analysis with String Functions
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute(f"""
            SELECT 
                company_name,
                COUNT(*) as employee_count,
                GROUP_CONCAT(DISTINCT SUBSTRING_INDEX(email, '@', -1) SEPARATOR ', ') as email_domains
            FROM {TABLE_NAME}
            WHERE company_name != 'Unknown'
            GROUP BY company_name
            ORDER BY employee_count DESC
        """)
        results = cursor.fetchall()
        return ("Companies & Email Domains", ["company_name", "employee_count", "email_domains"], results)
    
    except Error as e:
        print(f"[ERROR] Error in Query 2: {e}")
        return ("Companies & Email Domains", [], [])

def query_geographic_distribution(conn):
    """
    Query 3: Geographic distribution - users with valid coordinates
    Week 3 Skill: Spatial SQL Analysis
    """
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute(f"""
            SELECT 
                city,
                COUNT(*) as user_count,
                ROUND(AVG(ABS(latitude)), 4) as avg_latitude,
                ROUND(AVG(ABS(longitude)), 4) as avg_longitude
            FROM {TABLE_NAME}
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            GROUP BY city
            ORDER BY user_count DESC
        """)
        results = cursor.fetchall()
        return ("Geographic Distribution", ["city", "user_count", "avg_latitude", "avg_longitude"], results)
    
    except Error as e:
        print(f"[ERROR] Error in Query 3: {e}")
        return ("Geographic Distribution", [], [])

def run_all_queries(conn):
    """Run all analysis queries and return results"""
    print("\n" + "="*70)
    print("RUNNING ANALYSIS QUERIES")
    print("="*70)
    
    queries_results = []
    
    # Query 1
    print("\n[Query 1] Users by City:")
    q1_title, q1_cols, q1_data = query_users_by_city(conn)
    queries_results.append((q1_title, q1_cols, q1_data))
    print_query_results(q1_title, q1_cols, q1_data)
    
    # Query 2
    print("\n[Query 2] Companies & Email Domains:")
    q2_title, q2_cols, q2_data = query_companies_with_email_domains(conn)
    queries_results.append((q2_title, q2_cols, q2_data))
    print_query_results(q2_title, q2_cols, q2_data)
    
    # Query 3
    print("\n[Query 3] Geographic Distribution:")
    q3_title, q3_cols, q3_data = query_geographic_distribution(conn)
    queries_results.append((q3_title, q3_cols, q3_data))
    print_query_results(q3_title, q3_cols, q3_data)
    
    return queries_results

def print_query_results(title, columns, data):
    """Print query results in formatted table"""
    if not data:
        print("  No results found.")
        return
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in data:
        for i, col in enumerate(columns):
            col_widths[col] = max(col_widths[col], len(str(row[i])))
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(f"  {header}")
    print("  " + "-" * len(header))
    
    # Print rows
    for row in data:
        row_str = " | ".join(str(row[i]).ljust(col_widths[columns[i]]) for i in range(len(columns)))
        print(f"  {row_str}")

# ==================== EXPORT FUNCTIONS ====================

def export_to_csv(queries_results):
    """
    Export query results to CSV
    Week 1 Skill: File Handling with CSV
    """
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            for title, columns, data in queries_results:
                # Write section header
                writer.writerow([])
                writer.writerow([title])
                writer.writerow(columns)
                
                # Write data rows
                for row in data:
                    writer.writerow(row)
        
        print(f"[OK] Exported results to CSV: {CSV_FILE}")
        return True
    
    except IOError as e:
        print(f"[ERROR] Error writing CSV file: {e}")
        return False

def export_to_txt(conn, queries_results):
    """
    Export comprehensive analysis report to TXT
    Week 1 Skill: File Handling with Text
    """
    try:
        with open(TXT_FILE, 'w', encoding='utf-8') as txtfile:
            # Header
            txtfile.write("CAPSTONE PROJECT - DATA ANALYSIS REPORT\n\n")
            
            # Timestamp
            txtfile.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            txtfile.write(f"Database: {DB_NAME}\n")
            txtfile.write(f"Data Source: {API_URL}\n\n")
            
            # Summary statistics
            cursor = conn.cursor()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            total_users = cursor.fetchone()[0]
            
            txtfile.write("SUMMARY STATISTICS\n")
            txtfile.write(f"Total Records: {total_users}\n\n")
            
            # Query results
            for title, columns, data in queries_results:
                txtfile.write(f"\n{title}\n")
                
                if not data:
                    txtfile.write("No results found.\n")
                else:
                    # Write header
                    header = " | ".join(f"{col:<20}" for col in columns)
                    txtfile.write(f"{header}\n")
                    txtfile.write("-" * len(header) + "\n")
                    
                    # Write data
                    for row in data:
                        row_str = " | ".join(f"{str(val):<20}" for val in row)
                        txtfile.write(f"{row_str}\n")
            
            # Footer
            txtfile.write("\nEND OF REPORT\n")
        
        print(f"[OK] Exported report to TXT: {TXT_FILE}")
        return True
    
    except IOError as e:
        print(f"[ERROR] Error writing TXT file: {e}")
        return False

# ==================== MAIN ORCHESTRATION ====================

def run_complete_pipeline():
    """
    Execute complete data pipeline:
    Fetch → Store → Analyze → Export
    """
    print("\n" + "CAPSTONE PROJECT - AUTOMATED DATA SYSTEM".center(90))
    print("Week 1 + Week 2 + Week 3 Integration".center(90))
    print("\n")
    
    # Step 0: Create output directory
    print("Step 0: Preparing environment...")
    if not create_output_directory():
        print("Failed to create output directory. Exiting.")
        return
    print()
    
    # Step 1: Fetch data (Week 3)
    print("STEP 1: FETCH DATA FROM API")
    api_data = fetch_data(API_URL)
    if not api_data:
        print("Failed to fetch API data. Exiting.")
        return
    print()
    
    # Step 2: Connect to database (Week 2)
    print("STEP 2: DATABASE CONNECTION")
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL. Exiting.")
        return
    print()
    
    # Step 3: Create database and table (Week 2)
    print("STEP 3: CREATE DATABASE SCHEMA")
    if not create_database_and_table(conn):
        print("Failed to create database schema. Exiting.")
        conn.close()
        return
    print()
    
    # Step 4: Store data (Week 2)
    print("STEP 4: STORE DATA IN DATABASE")
    if not store_data(conn, api_data):
        print("Failed to store data. Exiting.")
        conn.close()
        return
    print()
    
    # Step 5: Run analysis queries (Week 3)
    print("STEP 5: ANALYZE DATA WITH SQL QUERIES")
    queries_results = run_all_queries(conn)
    print()
    
    # Step 6: Export results (Week 1)
    print("STEP 6: EXPORT RESULTS")
    export_to_csv(queries_results)
    export_to_txt(conn, queries_results)
    print()
    
    # Cleanup
    conn.close()
    
    # Final summary
    print("[OK] PIPELINE COMPLETED SUCCESSFULLY")
    print(f"\nOutput files created in: {OUTPUT_DIR}/")
    print(f"  • CSV file: {CSV_FILE}")
    print(f"  • TXT file: {TXT_FILE}")
    print("\n[SUCCESS] Capstone Project Complete!\n")

# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    try:
        run_complete_pipeline()
    except KeyboardInterrupt:
        print("\n\n[ERROR] Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
