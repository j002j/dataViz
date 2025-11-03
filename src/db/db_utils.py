import os
import psycopg2
from psycopg2 import sql

def get_db_connection():
    """Establishes and returns a psycopg2 connection object."""
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
        print(f"Successfully connected to {DB_NAME} at {DB_HOST}:{DB_PORT}")
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to the database: {e}")
        return None

def create_detections_table(conn):
    """Creates the mapillary_detections table if it doesn't exist."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS mapillary_detections (
        id SERIAL PRIMARY KEY,
        cropped_file VARCHAR(255) NOT NULL,
        original_image_id BIGINT NOT NULL,
        captured_at TIMESTAMPTZ,
        location JSONB,
        bounding_box_original JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
        print("Table 'mapillary_detections' is ready.")
    except Exception as e:
        print(f"Error creating table: {e}")
        conn.rollback()