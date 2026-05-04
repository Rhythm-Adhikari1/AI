import mysql.connector
from mysql.connector import Error
import csv
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

DB_NAME = "store_db"

def create_connection():
    """Create connection to MySQL server"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None

def create_database_and_tables(conn):
    """Create store_db database with customers, products, and orders tables"""
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"[OK] Database '{DB_NAME}' created/verified")
        
        # Use database
        cursor.execute(f"USE {DB_NAME}")
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS orders")
        cursor.execute("DROP TABLE IF EXISTS products")
        cursor.execute("DROP TABLE IF EXISTS customers")
        
        # Create customers table
        customers_table = """
        CREATE TABLE customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100),
            city VARCHAR(50),
            phone VARCHAR(20)
        )
        """
        cursor.execute(customers_table)
        print("[OK] Table 'customers' created")
        
        # Create products table
        products_table = """
        CREATE TABLE products (
            product_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            price DECIMAL(10, 2) NOT NULL,
            stock INT DEFAULT 0
        )
        """
        cursor.execute(products_table)
        print("[OK] Table 'products' created")
        
        # Create orders table with foreign keys
        orders_table = """
        CREATE TABLE orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            customer_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL,
            order_date DATE,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
        """
        cursor.execute(orders_table)
        print("[OK] Table 'orders' created with foreign keys")
        
        conn.commit()
        return True
    except Error as e:
        print(f"[ERROR] Error creating database/tables: {e}")
        return False

def insert_customers(conn):
    """Insert 10 customers with parameterized queries"""
    cursor = conn.cursor()
    
    customers = [
        ("Alice Johnson", "alice@email.com", "New York", "555-0101"),
        ("Bob Smith", "bob@email.com", "Los Angeles", "555-0102"),
        ("Carol Williams", "carol@email.com", "Chicago", "555-0103"),
        ("David Brown", "david@email.com", "New York", "555-0104"),
        ("Emma Davis", "emma@email.com", "Houston", "555-0105"),
        ("Frank Miller", "frank@email.com", "Phoenix", "555-0106"),
        ("Grace Wilson", "grace@email.com", "Los Angeles", "555-0107"),
        ("Henry Moore", "henry@email.com", "Chicago", "555-0108"),
        ("Iris Taylor", "iris@email.com", "New York", "555-0109"),
        ("Jack Anderson", "jack@email.com", "Houston", "555-0110"),
    ]
    
    insert_query = "INSERT INTO customers (name, email, city, phone) VALUES (%s, %s, %s, %s)"
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for customer in customers:
            cursor.execute(insert_query, customer)
        
        conn.commit()
        print(f"[OK] Inserted {len(customers)} customers")
        return True
    except Error as e:
        print(f"[ERROR] Error inserting customers: {e}")
        return False

def insert_products(conn):
    """Insert 8 products with parameterized queries"""
    cursor = conn.cursor()
    
    products = [
        ("Laptop", "Electronics", 899.99, 50),
        ("Mouse", "Electronics", 29.99, 200),
        ("Keyboard", "Electronics", 79.99, 150),
        ("Monitor", "Electronics", 299.99, 75),
        ("Desk Chair", "Furniture", 199.99, 100),
        ("Desk Lamp", "Furniture", 49.99, 120),
        ("USB Cable", "Electronics", 9.99, 500),
        ("Webcam", "Electronics", 59.99, 80),
    ]
    
    insert_query = "INSERT INTO products (name, category, price, stock) VALUES (%s, %s, %s, %s)"
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for product in products:
            cursor.execute(insert_query, product)
        
        conn.commit()
        print(f"[OK] Inserted {len(products)} products")
        return True
    except Error as e:
        print(f"[ERROR] Error inserting products: {e}")
        return False

def insert_orders(conn):
    """Insert 20 orders with parameterized queries"""
    cursor = conn.cursor()
    
    orders = [
        (1, 1, 1, "2026-01-10"),
        (1, 2, 3, "2026-01-12"),
        (2, 4, 1, "2026-01-15"),
        (2, 7, 5, "2026-01-18"),
        (3, 3, 2, "2026-01-20"),
        (4, 1, 1, "2026-01-22"),
        (4, 5, 1, "2026-01-25"),
        (5, 8, 2, "2026-02-01"),
        (5, 2, 4, "2026-02-03"),
        (6, 6, 1, "2026-02-05"),
        (7, 4, 1, "2026-02-08"),
        (7, 3, 3, "2026-02-10"),
        (8, 1, 1, "2026-02-12"),
        (8, 2, 2, "2026-02-15"),
        (9, 5, 2, "2026-02-18"),
        (9, 7, 6, "2026-02-20"),
        (10, 4, 1, "2026-02-22"),
        (3, 8, 1, "2026-02-25"),
        (6, 3, 2, "2026-02-28"),
        (10, 6, 1, "2026-03-02"),
    ]
    
    insert_query = "INSERT INTO orders (customer_id, product_id, quantity, order_date) VALUES (%s, %s, %s, %s)"
    
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        for order in orders:
            cursor.execute(insert_query, order)
        
        conn.commit()
        print(f"[OK] Inserted {len(orders)} orders")
        return True
    except Error as e:
        print(f"[ERROR] Error inserting orders: {e}")
        return False

def query_revenue_per_customer(conn):
    """Query 1: Total money spent per customer (sorted highest first)"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            SUM(o.quantity * p.price) as total_spent
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        LEFT JOIN products p ON o.product_id = p.product_id
        GROUP BY c.customer_id, c.name, c.city
        ORDER BY total_spent DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in revenue query: {e}")
        return []

def query_most_ordered_product(conn):
    """Query 2: Most ordered product by total quantity"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            p.product_id,
            p.name,
            p.category,
            SUM(o.quantity) as total_quantity
        FROM products p
        LEFT JOIN orders o ON p.product_id = o.product_id
        GROUP BY p.product_id, p.name, p.category
        ORDER BY total_quantity DESC
        LIMIT 5
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in product query: {e}")
        return []

def query_frequent_customers(conn):
    """Query 3: Customers who placed more than 2 orders"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            c.customer_id,
            c.name,
            c.city,
            COUNT(o.order_id) as order_count
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name, c.city
        HAVING COUNT(o.order_id) > 2
        ORDER BY order_count DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in frequent customers query: {e}")
        return []

def query_avg_order_per_city(conn):
    """Query 4: Average order value per city"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"USE {DB_NAME}")
        
        query = """
        SELECT 
            c.city,
            COUNT(o.order_id) as order_count,
            ROUND(AVG(o.quantity * p.price), 2) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        LEFT JOIN products p ON o.product_id = p.product_id
        WHERE c.city IS NOT NULL
        GROUP BY c.city
        ORDER BY avg_order_value DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error in city average query: {e}")
        return []

def print_query_results(title, columns, results):
    """Print query results in formatted table"""
    print(f"\n{title}")
    print("-" * 80)
    
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

def export_revenue_to_csv(results):
    """Export revenue-per-customer results to CSV"""
    try:
        csv_file = "revenue_report.csv"
        
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(["Customer ID", "Name", "City", "Total Spent"])
            
            # Write data
            for row in results:
                writer.writerow([row[0], row[1], row[2], f"${row[3]:.2f}" if row[3] else "$0.00"])
        
        print(f"[OK] Exported revenue report to: {csv_file}")
        return True
    except IOError as e:
        print(f"[ERROR] Error writing CSV file: {e}")
        return False

def main():
    """Main execution"""
    print("MULTI-TABLE RELATIONAL SYSTEM - TASK A")
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
    
    # Step 3: Insert data
    print("Step 2: Inserting sample data...")
    if not insert_customers(conn):
        conn.close()
        return
    
    if not insert_products(conn):
        conn.close()
        return
    
    if not insert_orders(conn):
        conn.close()
        return
    print()
    
    # Step 4: Run queries
    print("Step 3: Running analysis queries...")
    
    # Query 1: Revenue per customer
    print("\nQuery 1: Total Revenue Per Customer")
    revenue_results = query_revenue_per_customer(conn)
    print_query_results("Revenue Per Customer (Highest First)", 
                       ["Customer ID", "Name", "City", "Total Spent"], 
                       revenue_results)
    
    # Query 2: Most ordered product
    print("\nQuery 2: Most Ordered Products")
    product_results = query_most_ordered_product(conn)
    print_query_results("Top 5 Most Ordered Products", 
                       ["Product ID", "Name", "Category", "Total Quantity"], 
                       product_results)
    
    # Query 3: Frequent customers
    print("\nQuery 3: Frequent Customers")
    frequent_results = query_frequent_customers(conn)
    print_query_results("Customers With More Than 2 Orders", 
                       ["Customer ID", "Name", "City", "Order Count"], 
                       frequent_results)
    
    # Query 4: Average order per city
    print("\nQuery 4: Average Order Value Per City")
    city_results = query_avg_order_per_city(conn)
    print_query_results("Average Order Value Per City", 
                       ["City", "Order Count", "Avg Order Value"], 
                       city_results)
    
    print()
    
    # Step 5: Export revenue report
    print("Step 4: Exporting revenue report...")
    export_revenue_to_csv(revenue_results)
    
    conn.close()
    print("\n[OK] Task A completed successfully!")

if __name__ == "__main__":
    main()
