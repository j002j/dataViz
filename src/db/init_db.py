import os
# The import works because this is run as `python -m src.db.init_db`
from src.db.db_utils import get_db_connection, create_cities_table, create_detections_table

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

def main():
    print("Initializing database schema...")
    conn = get_db_connection()
    if conn is None:
        print("Failed to get DB connection. Exiting.")
        sys.exit(1)

    # This is now the single source of truth for the schema
    create_cities_table(conn)
    create_detections_table(conn)
    # Add future tables here, e.g.:
    # create_analysis_table(conn)

    conn.close()
    print("Database schema is ready.")

if __name__ == "__main__":
    main()