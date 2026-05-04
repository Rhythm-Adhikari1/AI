import mysql.connector
from mysql.connector import Error
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

def create_connection():
    """Create a connection to MySQL server"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None

def create_database_and_tables(conn):
    """Create database and students table"""
    cursor = conn.cursor()
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS grades_db")
        print("[OK] Database 'grades_db' created/verified")
        
        # Use the database
        cursor.execute("USE grades_db")
        
        # Create students table
        students_table = """
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            subject VARCHAR(100) NOT NULL,
            score INT CHECK (score >= 0 AND score <= 100),
            grade CHAR(1),
            passed BOOLEAN
        )
        """
        cursor.execute(students_table)
        print("[OK] Table 'students' created/verified")
        
        conn.commit()
    except Error as e:
        print(f"[ERROR] Error creating database/tables: {e}")

def assign_grade(score):
    """
    Assign letter grade based on score
    A: 90-100, B: 80-89, C: 70-79, D: 60-69, F: < 60
    """
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def check_duplicate_name(conn, name):
    """Check if student name already exists"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        cursor.execute("SELECT id FROM students WHERE name = %s", (name,))
        result = cursor.fetchone()
        return result is not None
    except Error as e:
        print(f"[ERROR] Error checking duplicate: {e}")
        return False

def insert_students(conn):
    """Insert 15 students with various scores (40-100)"""
    cursor = conn.cursor()
    
    students = [
        ("Alice Johnson", "Mathematics", 95),
        ("Bob Smith", "Physics", 87),
        ("Charlie Brown", "Chemistry", 76),
        ("Diana Prince", "Mathematics", 92),
        ("Evan Davis", "Physics", 65),
        ("Fiona Green", "Chemistry", 58),
        ("George Harris", "Mathematics", 88),
        ("Hannah White", "Physics", 72),
        ("Isaac Newton", "Mathematics", 98),
        ("Julia Roberts", "Chemistry", 81),
        ("Kevin Hart", "Physics", 45),
        ("Laura Palmer", "Chemistry", 91),
        ("Michael Scott", "Mathematics", 55),
        ("Nina Simone", "Physics", 78),
        ("Oscar Wilson", "Chemistry", 62),
    ]
    
    insert_query = """
    INSERT INTO students (name, subject, score)
    VALUES (%s, %s, %s)
    """
    
    try:
        cursor.execute("USE grades_db")
        
        # Clear existing data
        cursor.execute("DELETE FROM students")
        
        inserted_count = 0
        skipped_count = 0
        
        for name, subject, score in students:
            # Check for duplicate before inserting
            if check_duplicate_name(conn, name):
                print(f"  [WARN] Skipped '{name}' - already exists in database")
                skipped_count += 1
                continue
            
            cursor.execute(insert_query, (name, subject, score))
            inserted_count += 1
        
        conn.commit()
        print(f"[OK] Inserted {inserted_count} students successfully")
        if skipped_count > 0:
            print(f"  [WARN] Skipped {skipped_count} duplicate entries")
    except Error as e:
        print(f"[ERROR] Error inserting students: {e}")

def update_grades(conn):
    """UPDATE all rows - set the grade column using assign_grade function"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        
        # Fetch all students
        cursor.execute("SELECT id, score FROM students")
        students = cursor.fetchall()
        
        update_query = "UPDATE students SET grade = %s WHERE id = %s"
        
        for student_id, score in students:
            grade = assign_grade(score)
            cursor.execute(update_query, (grade, student_id))
        
        conn.commit()
        print(f"[OK] Updated grades for {len(students)} students")
    except Error as e:
        print(f"[ERROR] Error updating grades: {e}")

def delete_failing_students(conn):
    """DELETE all students who scored below 50 (didn't pass)"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        
        # Count students to delete
        cursor.execute("SELECT COUNT(*) FROM students WHERE score < 50")
        delete_count = cursor.fetchone()[0]
        
        # Delete
        cursor.execute("DELETE FROM students WHERE score < 50")
        conn.commit()
        
        print(f"[OK] Deleted {delete_count} students with scores below 50")
    except Error as e:
        print(f"[ERROR] Error deleting students: {e}")

def add_passed_column(conn):
    """Add a new column 'passed BOOLEAN' using ALTER TABLE"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        
        # Check if column already exists
        cursor.execute("""
            SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME='students' AND COLUMN_NAME='passed'
        """)
        
        if cursor.fetchone() is None:
            # Column doesn't exist, so add it
            cursor.execute("""
                ALTER TABLE students 
                ADD COLUMN passed BOOLEAN DEFAULT FALSE
            """)
            print("[OK] Column 'passed' added to students table")
        else:
            print("[OK] Column 'passed' already exists")
        
        # Update passed column based on score >= 50
        cursor.execute("UPDATE students SET passed = (score >= 50)")
        conn.commit()
        print("[OK] Updated 'passed' column based on score >= 50")
        
    except Error as e:
        print(f"[ERROR] Error modifying table: {e}")

def query_students_by_grade(conn):
    """Query: show count of students per grade, ordered from A to F"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        
        cursor.execute("""
            SELECT grade, COUNT(*) as count
            FROM students
            GROUP BY grade
            ORDER BY FIELD(grade, 'A', 'B', 'C', 'D', 'F')
        """)
        
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error querying students: {e}")
        return []

def print_grade_distribution(conn, results):
    """Print grade distribution in formatted table"""
    if not results:
        print("No results found.")
        return
    
    print("\nGrade Distribution:")
    print(f"{'Grade':<10} {'Count':<10} {'Percentage':<10}")
    
    total = sum(count for grade, count in results)
    
    for grade, count in results:
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{grade:<10} {count:<10} {percentage:.1f}%")
    
    print("-" * 40)
    print(f"{'Total':<10} {total:<10}")

def query_all_students(conn):
    """Query all students with their details"""
    cursor = conn.cursor()
    try:
        cursor.execute("USE grades_db")
        
        cursor.execute("""
            SELECT id, name, subject, score, grade, passed
            FROM students
            ORDER BY score DESC
        """)
        
        results = cursor.fetchall()
        return results
    except Error as e:
        print(f"[ERROR] Error querying students: {e}")
        return []

def print_all_students(results):
    """Print all students in formatted table"""
    if not results:
        print("No students found.")
        return
    
    print("\nAll Students:")
    print("-" * 100)
    print(f"{'ID':<5} {'Name':<20} {'Subject':<15} {'Score':<8} {'Grade':<8} {'Passed':<8}")
    print("-" * 100)
    
    for student_id, name, subject, score, grade, passed in results:
        passed_str = "Yes" if passed else "No"
        print(f"{student_id:<5} {name:<20} {subject:<15} {score:<8} {grade:<8} {passed_str:<8}")

def generate_report(conn):
    """Generate comprehensive report"""
    report = []
    report.append("STUDENT GRADE MANAGEMENT SYSTEM - REPORT")
    report.append("")
    
    # Total students
    cursor = conn.cursor()
    cursor.execute("USE grades_db")
    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]
    report.append(f"Total Students: {total}")
    
    # Passed vs Failed
    cursor.execute("SELECT COUNT(*) FROM students WHERE passed = TRUE")
    passed_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM students WHERE passed = FALSE")
    failed_count = cursor.fetchone()[0]
    
    report.append(f"Passed (>= 50): {passed_count}")
    report.append(f"Failed (< 50): {failed_count}")
    
    # Average score
    cursor.execute("SELECT ROUND(AVG(score), 2) FROM students")
    avg_score = cursor.fetchone()[0]
    report.append(f"Average Score: {avg_score}")
    
    # Highest and lowest
    cursor.execute("SELECT MAX(score) FROM students")
    highest = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(score) FROM students")
    lowest = cursor.fetchone()[0]
    
    report.append(f"Highest Score: {highest}")
    report.append(f"Lowest Score: {lowest}")
    report.append("")
    
    return "\n".join(report)

def main():
    """Main execution"""
    print("STUDENT GRADE MANAGEMENT SYSTEM - TASK 04")
    print()
    
    # Create connection
    conn = create_connection()
    if conn is None:
        print("Failed to connect to MySQL server")
        return
    
    # Step 1: Create database and table
    print("Step 1: Creating database and table...")
    create_database_and_tables(conn)
    print()
    
    # Step 2: Insert students
    print("Step 2: Inserting 15 students...")
    insert_students(conn)
    print()
    
    # Step 3-4: Update grades
    print("Step 3-4: Assigning grades to all students...")
    update_grades(conn)
    print()
    
    # Step 5: Delete failing students
    print("Step 5: Deleting students who scored below 50...")
    delete_failing_students(conn)
    print()
    
    # Step 6: Add passed column
    print("Step 6: Adding 'passed' column and updating values...")
    add_passed_column(conn)
    print()
    
    # Step 7: Query grade distribution
    print("Step 7: Querying students per grade...")
    grade_results = query_students_by_grade(conn)
    print_grade_distribution(conn, grade_results)
    print()
    
    # Display all students
    print("All Students in Database:")
    all_students = query_all_students(conn)
    print_all_students(all_students)
    print()
    
    # Generate and display report
    print("Summary Report:")
    print(generate_report(conn))
    
    conn.close()
    print("[OK] Task completed successfully!\n")

if __name__ == "__main__":
    main()
