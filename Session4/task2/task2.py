import mysql.connector
from mysql.connector import Error
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API endpoints
USERS_API = "https://jsonplaceholder.typicode.com/users"
POSTS_API = "https://jsonplaceholder.typicode.com/posts"


def create_connection():
    """Create a connection to MySQL server"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            port =os.getenv("DB_PORT", 3306)
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database_and_tables(conn):
    """Create database and tables"""
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS app_db")
        print("Database 'app_db' created/verified")
        
        # Use the database
        cursor.execute("USE app_db")
        
        # Create users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone VARCHAR(50),
            city VARCHAR(100),
            company_name VARCHAR(255)
        )
        """
        cursor.execute(users_table)
        print("Table 'users' created/verified")
        
        # Create posts table
        posts_table = """
        CREATE TABLE IF NOT EXISTS posts (
            id INT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            body LONGTEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        cursor.execute(posts_table)
        print("Table 'posts' created/verified")
        
        conn.commit()
    except Error as e:
        print(f"Error creating database/tables: {e}")


def fetch_users_from_api():
    """Fetch users from the API"""
    try:
        print("\nFetching users from API...")
        response = requests.get(USERS_API)
        response.raise_for_status()
        users = response.json()
        print(f"Successfully fetched {len(users)} users")
        return users
    except requests.exceptions.RequestException as e:
        print(f"Error fetching users from API: {e}")
        return []


def fetch_posts_from_api():
    """Fetch posts from the API"""
    try:
        print("\nFetching posts from API...")
        response = requests.get(POSTS_API)
        response.raise_for_status()
        posts = response.json()
        print(f"Successfully fetched {len(posts)} posts")
        return posts
    except requests.exceptions.RequestException as e:
        print(f"Error fetching posts from API: {e}")
        return []


def insert_users(conn, users):
    """Insert users into the database"""
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO users (id, name, email, phone, city, company_name)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE name=VALUES(name), email=VALUES(email)
    """
    
    try:
        # Disable foreign key checks to truncate
        cursor.execute("SET FOREIGN_KEY_CHECKS=0")
        cursor.execute("TRUNCATE TABLE users")
        cursor.execute("TRUNCATE TABLE posts")
        cursor.execute("SET FOREIGN_KEY_CHECKS=1")
        
        for user in users:
            # Extract nested JSON fields
            city = user.get("address", {}).get("city", "Unknown")
            company_name = user.get("company", {}).get("name", "Unknown")
            
            user_data = (
                user.get("id"),
                user.get("name"),
                user.get("email"),
                user.get("phone"),
                city,
                company_name
            )
            cursor.execute(insert_query, user_data)
        
        conn.commit()
        print(f"Inserted {len(users)} users successfully\n")
    except Error as e:
        print(f"Error inserting users: {e}")


def insert_posts(conn, posts):
    """Insert posts for users 1, 2, and 3"""
    cursor = conn.cursor()
    
    insert_query = """
    INSERT INTO posts (id, user_id, title, body)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE title=VALUES(title), body=VALUES(body)
    """
    
    try:
        # Filter posts for user_id 1, 2, 3
        filtered_posts = [p for p in posts if p.get("userId") in [1, 2, 3]]
        
        for post in filtered_posts:
            post_data = (
                post.get("id"),
                post.get("userId"),
                post.get("title"),
                post.get("body")
            )
            cursor.execute(insert_query, post_data)
        
        conn.commit()
        print(f"Inserted {len(filtered_posts)} posts for users 1, 2, 3\n")
    except Error as e:
        print(f"Error inserting posts: {e}")


def print_query_results(title, query, conn, readme_file=None):
    """Execute and print query results with clean formatting"""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        # Print to console
        print(f"\n{title}")
        print("-" * 80)
        
        # Write to README
        if readme_file:
            readme_file.write(f"\n## {title}\n\n")
        
        if not results:
            msg = "No results found."
            print(msg)
            if readme_file:
                readme_file.write(f"{msg}\n\n")
        else:
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            
            # Create formatted table
            col_widths = [max(len(str(name)), max(len(str(row[i])) for row in results)) for i, name in enumerate(column_names)]
            
            # Header
            header = " | ".join(name.ljust(col_widths[i]) for i, name in enumerate(column_names))
            separator = "-" * len(header)
            
            print(header)
            print(separator)
            
            if readme_file:
                readme_file.write("| " + " | ".join(name for name in column_names) + " |\n")
                readme_file.write("|" + "|".join(["---" for _ in column_names]) + "|\n")
            
            # Rows
            for row in results:
                row_str = " | ".join(str(row[i]).ljust(col_widths[i]) for i in range(len(row)))
                print(row_str)
                if readme_file:
                    readme_file.write("| " + " | ".join(str(val) for val in row) + " |\n")
            
            if readme_file:
                readme_file.write("\n")
        
    except Error as e:
        error_msg = f"Error executing query: {e}"
        print(error_msg)
        if readme_file:
            readme_file.write(f"{error_msg}\n\n")


def run_queries(conn, readme_file=None):
    """Run all required queries"""
    cursor = conn.cursor()
    cursor.execute("USE app_db")
    
    # Query 1: All users sorted alphabetically by name
    query1 = """
    SELECT id, name, email, city, company_name
    FROM users
    ORDER BY name ASC
    """
    print_query_results("Query 1: All users sorted by name (A-Z)", query1, conn, readme_file)
    
    # Query 2: Users from the same city
    query2 = """
    SELECT city, COUNT(*) AS user_count, GROUP_CONCAT(name SEPARATOR ', ') AS names
    FROM users
    GROUP BY city
    HAVING COUNT(*) > 1
    ORDER BY user_count DESC
    """
    print_query_results("Query 2: Cities with multiple users", query2, conn, readme_file)
    
    # Bonus Query: JOIN users and posts
    bonus_query = """
    SELECT u.name, p.title, p.body
    FROM users u
    LEFT JOIN posts p ON u.id = p.user_id
    WHERE u.id IN (1, 2, 3)
    ORDER BY u.name, p.id
    """
    print_query_results("BONUS: Users and their posts (JOIN)", bonus_query, conn, readme_file)


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("API TO MYSQL PIPELINE - TASK 02")
    print("=" * 80)
    
    # Create output file
    readme_filename = os.path.join(os.path.dirname(__file__), "README.md")
    readme_file = open(readme_filename, "w")
    
    readme_file.write("# API TO MYSQL PIPELINE - TASK 02\n\n")
    readme_file.write("## Overview\n")
    readme_file.write("This script fetches user and post data from JSONPlaceholder API and stores it in MySQL database.\n\n")
    
    # Create connection
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL server")
        readme_file.write("**Error:** Failed to connect to MySQL server\n")
        readme_file.close()
        return
    
    # Create database and tables
    create_database_and_tables(conn)
    
    # Fetch data from APIs
    users = fetch_users_from_api()
    posts = fetch_posts_from_api()
    
    if not users:
        print("No users fetched. Exiting.")
        readme_file.write("**Error:** No users fetched. Exiting.\n")
        readme_file.close()
        conn.close()
        return
    
    # Insert users
    insert_users(conn, users)
    
    # Insert posts
    if posts:
        insert_posts(conn, posts)
    
    # Run queries
    print("\n" + "=" * 80)
    print("QUERY RESULTS")
    print("=" * 80)
    readme_file.write("## Query Results\n\n")
    
    run_queries(conn, readme_file)
    
    # Close connection
    conn.close()
    print("\n" + "=" * 80)
    print("Pipeline completed successfully!")
    print(f"Results saved to: {readme_filename}")
    print("=" * 80 + "\n")
    
    readme_file.write("\n---\n")
    readme_file.write("*Pipeline completed successfully!*\n")
    readme_file.close()


if __name__ == "__main__":
    main()
