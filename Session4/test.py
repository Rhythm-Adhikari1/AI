import mysql.connector
from dotenv import load_dotenv
import os

# load environment variables from .env file
load_dotenv()

# connect to database
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = conn.cursor()

# fetch data
cursor.execute("SELECT * FROM users")

for row in cursor.fetchall():
    print(row)

conn.close()