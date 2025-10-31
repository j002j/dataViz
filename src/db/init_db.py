
import os
import psycopg2 
from psycopg2 import sql

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
DB_NAME = os.getenv("POSTGRES_DB", "starterkit_db")
DB_USER = os.getenv("POSTGRES_USER", "jenny")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor() #Cursor-object for SQL command and get results
    print(f"Connected to {DB_NAME} at {DB_HOST}:{DB_PORT}")
except Exception as e:
    print("ERROR connecting to the database:", e)
    exit(1)

sql_file_path = "db/starterkit.session.sql"

try:
    with open(sql_file_path, "r") as file: #read file
        sql_commands = file.read()
    cursor.execute(sql_commands)
    conn.commit()
    print(f"Executed SQL from {sql_file_path}")
except Exception as e:
    print("Error executing SQL:", e)
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("Connection closed.")
