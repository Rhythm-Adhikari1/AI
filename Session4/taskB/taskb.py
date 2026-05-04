import mysql.connector
from mysql.connector import Error
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "port": int(os.getenv("DB_PORT", 3306))
}

DB_NAME = "monitor_db"
API_URL = "https://jsonplaceholder.typicode.com/posts"

def create_connection():
    """Create connection to MySQL server"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None

def fetch_posts_from_api():
    """Fetch posts from JSONPlaceholder API"""
    try:
        print("[INFO] Fetching posts from API...")
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        posts = response.json()
        print(f"[OK] Fetched {len(posts)} posts from API")
        return posts
    except requests.exceptions.Timeout:
        print("[ERROR] API request timeout")
        return None
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error to API")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return None
    except ValueError as e:
        print(f"[ERROR] Failed to parse JSON response: {e}")
        return None

def create_database_and_tables(conn):
    """Create monitor_db database with posts and change_log tables"""
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"[OK] Database '{DB_NAME}' created/verified")
        
        # Use database
        cursor.execute(f"USE {DB_NAME}")
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS change_log")
        cursor.execute("DROP TABLE IF EXISTS posts")
        
        # Create posts table
        posts_table = """
        CREATE TABLE posts (
            id INT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            body LONGTEXT NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(posts_table)
        print("[OK] Table 'posts' created")
        
        # Create change_log table
        change_log_table = """
        CREATE TABLE change_log (
            change_id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            change_type VARCHAR(20) NOT NULL,
            change_description VARCHAR(255),
            change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(change_log_table)
        print("[OK] Table 'change_log' created")
        
        conn.commit()
        return True
    except Error as e:
        print(f"[ERROR] Error creating database/tables: {e}")
        return False

def check_if_first_run(conn):
    """Check if this is the first run by checking if posts table has data"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute("SELECT COUNT(*) FROM posts")
        result = cursor.fetchone()
        return result[0] == 0
    except Error as e:
        print(f"[ERROR] Error checking first run status: {e}")
        return True

def insert_posts_on_first_run(conn, posts):
    """Insert all posts on first run and log as NEW"""
    cursor = conn.cursor()
    run_timestamp = datetime.now()
    
    insert_post_query = "INSERT INTO posts (id, user_id, title, body) VALUES (%s, %s, %s, %s)"
    log_query = "INSERT INTO change_log (post_id, user_id, change_type, change_description, run_timestamp) VALUES (%s, %s, %s, %s, %s)"
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for post in posts:
            post_id = post.get("id")
            user_id = post.get("userId")
            title = post.get("title")
            body = post.get("body")
            
            cursor.execute(insert_post_query, (post_id, user_id, title, body))
            cursor.execute(log_query, (post_id, user_id, "NEW", f"Initial post creation", run_timestamp))
        
        conn.commit()
        print(f"[OK] Inserted {len(posts)} posts and logged as NEW")
        return True
    except Error as e:
        print(f"[ERROR] Error inserting posts on first run: {e}")
        return False

def get_existing_posts(conn):
    """Retrieve existing posts from database"""
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute("SELECT id, user_id, title, body FROM posts")
        posts = cursor.fetchall()
        return posts
    except Error as e:
        print(f"[ERROR] Error retrieving existing posts: {e}")
        return []

def detect_and_log_changes(conn, api_posts, existing_posts):
    """Detect changes between API posts and database posts"""
    cursor = conn.cursor()
    run_timestamp = datetime.now()
    
    log_query = "INSERT INTO change_log (post_id, user_id, change_type, change_description, run_timestamp) VALUES (%s, %s, %s, %s, %s)"
    update_post_query = "UPDATE posts SET title=%s, body=%s WHERE id=%s"
    
    # Create dictionary of existing posts for easy lookup
    existing_dict = {post['id']: post for post in existing_posts}
    
    changes_detected = 0
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for api_post in api_posts:
            post_id = api_post.get("id")
            user_id = api_post.get("userId")
            title = api_post.get("title")
            body = api_post.get("body")
            
            if post_id in existing_dict:
                existing_post = existing_dict[post_id]
                
                # Check for changes
                if existing_post['title'] != title or existing_post['body'] != body:
                    change_desc = ""
                    if existing_post['title'] != title:
                        change_desc += f"Title changed from '{existing_post['title'][:50]}...' to '{title[:50]}...'"
                    if existing_post['body'] != body:
                        if change_desc:
                            change_desc += " | "
                        change_desc += "Body content modified"
                    
                    cursor.execute(log_query, (post_id, user_id, "MODIFIED", change_desc, run_timestamp))
                    cursor.execute(update_post_query, (title, body, post_id))
                    changes_detected += 1
        
        conn.commit()
        print(f"[OK] Detected and logged {changes_detected} changes")
        return True
    except Error as e:
        print(f"[ERROR] Error detecting changes: {e}")
        return False

def query_post_count_per_user(conn):
    """Query 1: Post count per user"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            user_id,
            COUNT(*) as post_count
        FROM posts
        GROUP BY user_id
        ORDER BY post_count DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in post count query: {e}")
        return []

def query_change_log_latest_run(conn):
    """Query 2: All change log entries from the latest run"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            post_id,
            user_id,
            change_type,
            change_description,
            change_time
        FROM change_log
        WHERE run_timestamp = (SELECT MAX(run_timestamp) FROM change_log)
        ORDER BY change_time DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in change log query: {e}")
        return []

def query_user_most_changes(conn):
    """Query 3: Which user triggered the most change events"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            user_id,
            COUNT(*) as change_count,
            GROUP_CONCAT(DISTINCT change_type) as change_types
        FROM change_log
        GROUP BY user_id
        ORDER BY change_count DESC
        LIMIT 10
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in user changes query: {e}")
        return []

def print_query_results(title, columns, results):
    """Print query results in formatted table"""
    print(f"\n{title}")
    print("-" * 100)
    
    if not results:
        print("No results found.")
        return
    
    # Calculate column widths
    col_widths = {col: len(col) for col in columns}
    for row in results:
        for i, col in enumerate(columns):
            col_widths[col] = max(col_widths[col], len(str(row[i])))
    
    # Print header
    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in results:
        row_str = " | ".join(str(row[i]).ljust(col_widths[columns[i]]) for i in range(len(columns)))
        print(row_str)

def export_analysis_to_file(post_count_results, change_log_results, user_changes_results):
    """Export analysis results to a text file"""
    try:
        with open("monitor_report.txt", "w", encoding="utf-8") as f:
            f.write("API MONITOR - CHANGE DETECTION REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Post count per user
            f.write("POST COUNT PER USER\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'User ID':<15} {'Post Count':<15}\n")
            f.write("-" * 30 + "\n")
            for row in post_count_results:
                f.write(f"{row[0]:<15} {row[1]:<15}\n")
            
            f.write("\n\n")
            
            # Change log entries
            f.write("CHANGE LOG ENTRIES FROM LATEST RUN\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Post ID':<12} {'User ID':<12} {'Type':<15} {'Description':<40} {'Time':<20}\n")
            f.write("-" * 99 + "\n")
            for row in change_log_results:
                desc = row[3][:37] + "..." if len(row[3]) > 40 else row[3]
                f.write(f"{row[0]:<12} {row[1]:<12} {row[2]:<15} {desc:<40} {str(row[4]):<20}\n")
            
            f.write("\n\n")
            
            # User with most changes
            f.write("USERS WITH MOST CHANGE EVENTS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'User ID':<15} {'Change Count':<15} {'Change Types':<50}\n")
            f.write("-" * 80 + "\n")
            for row in user_changes_results:
                f.write(f"{row[0]:<15} {row[1]:<15} {row[2]:<50}\n")
            
            f.write("\n")
        
        print("[OK] Exported analysis to: monitor_report.txt")
        return True
    except IOError as e:
        print(f"[ERROR] Error writing report file: {e}")
        return False

def main():
    """Main execution"""
    print("API MONITOR WITH CHANGE DETECTION - TASK B")
    print()
    
    # Step 1: Create connection
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL server")
        return
    print()
    
    # Step 2: Create database and tables
    print("Step 1: Creating database and tables...")
    if not create_database_and_tables(conn):
        conn.close()
        return
    print()
    
    # Step 3: Fetch posts from API
    print("Step 2: Fetching posts from API...")
    api_posts = fetch_posts_from_api()
    if api_posts is None:
        conn.close()
        return
    print()
    
    # Step 4: Check if first run
    print("Step 3: Checking if first run...")
    is_first_run = check_if_first_run(conn)
    if is_first_run:
        print("[INFO] First run detected - inserting all posts")
        if not insert_posts_on_first_run(conn, api_posts):
            conn.close()
            return
    else:
        print("[INFO] Subsequent run - detecting changes")
        existing_posts = get_existing_posts(conn)
        if not detect_and_log_changes(conn, api_posts, existing_posts):
            conn.close()
            return
    print()
    
    # Step 5: Run queries
    print("Step 4: Running analysis queries...")
    
    # Query 1: Post count per user
    print("\nQuery 1: Post Count Per User")
    post_count_results = query_post_count_per_user(conn)
    print_query_results("Post Count Per User", ["User ID", "Post Count"], post_count_results)
    
    # Query 2: Change log entries
    print("\nQuery 2: Change Log Entries From Latest Run")
    change_log_results = query_change_log_latest_run(conn)
    print_query_results("Change Log Entries", 
                       ["Post ID", "User ID", "Type", "Description", "Time"], 
                       change_log_results)
    
    # Query 3: User with most changes
    print("\nQuery 3: Users With Most Change Events")
    user_changes_results = query_user_most_changes(conn)
    print_query_results("User Change Activity", 
                       ["User ID", "Change Count", "Change Types"], 
                       user_changes_results)
    
    print()
    
    # Step 6: Export report
    print("Step 5: Exporting analysis report...")
    export_analysis_to_file(post_count_results, change_log_results, user_changes_results)
    
    conn.close()
    print("\n[OK] Task B completed successfully!")
    print("\nIMPORTANT: To test change detection:")
    print("1. Run this script once (first run - all posts logged as NEW)")
    print("2. Manually update a post in MySQL:")
    print("   mysql> UPDATE monitor_db.posts SET title='Changed' WHERE id=1;")
    print("3. Run this script again (should detect and log the change as MODIFIED)")

if __name__ == "__main__":
    main()
