import os
from .db_utils import get_db_connection # Import from our new utils file

# Get connection
conn = get_db_connection()
if conn is None:
    exit(1)

cursor = conn.cursor()

# This part remains the same from your file
sql_file_path = "db/starterkit.session.sql"

try:
    with open(sql_file_path, "r") as file:
        sql_commands = file.read()
    cursor.execute(sql_commands)
    conn.commit()
    print(f"Successfully executed SQL from {sql_file_path}")
except Exception as e:
    print(f"Error executing {sql_file_path}: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
    print("Database connection closed.")