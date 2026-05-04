import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


def create_connection():
    """Create a connection to MySQL server"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            port =os.getenv("DB_PORT", 3306),
            password=os.getenv("DB_PASSWORD", "")
        )
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database_and_table(conn):
    """Create database and books table"""
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS library")
        print("Database 'library' created/verified")
        
        # Use the database
        cursor.execute("USE library")
        
        # Create books table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            author VARCHAR(255) NOT NULL,
            year INT NOT NULL,
            genre VARCHAR(100) NOT NULL,
            rating REAL NOT NULL
        )
        """
        cursor.execute(create_table_query)
        print("Table 'books' created/verified")
        conn.commit()
    except Error as e:
        print(f"Error creating database/table: {e}")


def insert_books(conn):
    """Insert 8+ books into the books table"""
    cursor = conn.cursor()
    
    books_data = [
        ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "Fiction", 4.7),
        ("To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", 4.8),
        ("1984", "George Orwell", 1949, "Dystopian", 4.6),
        ("Pride and Prejudice", "Jane Austen", 1813, "Romance", 4.5),
        ("The Catcher in the Rye", "J.D. Salinger", 1951, "Fiction", 4.2),
        ("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy", 4.7),
        ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", 1997, "Fantasy", 4.9),
        ("The Lord of the Rings", "J.R.R. Tolkien", 1954, "Fantasy", 4.8),
        ("Sapiens", "Yuval Noah Harari", 2011, "Non-Fiction", 4.4),
        ("Educated", "Tara Westover", 2018, "Biography", 4.6)
    ]
    
    insert_query = """
    INSERT INTO books (title, author, year, genre, rating)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        # Clear existing data
        cursor.execute("TRUNCATE TABLE books")
        
        # Insert books
        cursor.executemany(insert_query, books_data)
        conn.commit()
        print(f"{len(books_data)} books inserted successfully\n")
    except Error as e:
        print(f"Error inserting books: {e}")


def print_query_results(title, query, conn):
    """Execute and print query results with formatting"""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
        
        if not results:
            print("No results found.")
        else:
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            print(f"  {' | '.join(column_names)}")
            print("  " + "-" * 66)
            
            for row in results:
                print(f"  {' | '.join(str(val) for val in row)}")
        
    except Error as e:
        print(f"Error executing query: {e}")


def run_queries(conn):
    """Run all 4 required queries"""
    cursor = conn.cursor()
    cursor.execute("USE library")
    
    # Query 1: Books published after 2000, ordered by rating (highest first)
    query1 = """
    SELECT title, author, year, rating
    FROM books
    WHERE year > 2000
    ORDER BY rating DESC
    """
    print_query_results("Query 1: Books published after 2000 (sorted by rating)", query1, conn)
    
    # Query 2: Fiction books with rating above 4.0
    query2 = """
    SELECT title, author, genre, rating
    FROM books
    WHERE genre = 'Fiction' AND rating > 4.0
    ORDER BY rating DESC
    """
    print_query_results("Query 2: Fiction books with rating > 4.0", query2, conn)
    
    # Query 3: Average rating across all books
    query3 = """
    SELECT ROUND(AVG(rating), 2) AS average_rating
    FROM books
    """
    print_query_results("Query 3: Average rating across all books", query3, conn)
    
    # Query 4: Count books per genre
    query4 = """
    SELECT genre, COUNT(*) AS book_count
    FROM books
    GROUP BY genre
    ORDER BY book_count DESC
    """
    print_query_results("Query 4: Books per genre", query4, conn)


def main():
    """Main function"""
    print("\nLIBRARY DATABASE TASK")
    print("=" * 70)
    
    # Create connection
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL server")
        return
    
    # Create database and table
    create_database_and_table(conn)
    
    # Insert books
    insert_books(conn)
    
    # Run queries
    run_queries(conn)
    
    # Close connection
    conn.close()
    print("\n" + "=" * 70)
    print("Task completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
