import os
# The import works because this is run as `python -m src.db.init_db`
from db_utils import get_db_connection 

# Get connection
conn = get_db_connection()
if conn is None:
    print("Failed to get DB connection for init. Exiting.")
    exit(1)

cursor = conn.cursor()

# This path is relative to the /app WORKDIR
sql_file_path = "src/db/starterkit.session.sql" # <-- CORRECTED PATH

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