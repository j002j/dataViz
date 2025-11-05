import os
import psycopg2
import json
from psycopg2 import sql
from psycopg2 import extras # <-- ADD THIS

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
    """
    Creates the mapillary_detections table if it doesn't exist,
    now with a foreign key link to the cities table.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS mapillary_detections (
        id SERIAL PRIMARY KEY,
        cropped_file VARCHAR(255) NOT NULL,
        original_image_id BIGINT NOT NULL,
        captured_at TIMESTAMPTZ,
        location JSONB,
        bounding_box_original JSONB,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        
        -- NEW: Link to the city this detection belongs to
        city_id INTEGER REFERENCES cities(id) ON DELETE SET NULL
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

# --- NEW FUNCTION 1 (from your file) ---
def create_cities_table(conn):
    """Creates the cities table to track scanned status."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cities (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        bbox JSONB,
        scanned BOOLEAN DEFAULT FALSE NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)
            conn.commit()
        print("Table 'cities' is ready.")
    except Exception as e:
        print(f"Error creating 'cities' table: {e}")
        conn.rollback()

# --- NEW FUNCTION 2 (from your file) ---
def check_or_create_city(conn, city_name, city_bbox):
    """
    Checks if a city exists in the DB.
    If yes, returns its ID and 'scanned' status.
    If no, creates it with scanned=False and returns new ID and False.
    """
    try:
        with conn.cursor() as cursor:
            # Check if city exists
            cursor.execute("SELECT id, scanned FROM cities WHERE name = %s", (city_name,))
            result = cursor.fetchone()
            
            if result:
                # City exists, return its ID and scanned status
                city_id, is_scanned = result
                return city_id, is_scanned, False # <-- ADD ', False'
            else:
                # City doesn't exist, insert it
                print(f"  -> Adding new city '{city_name}' to database.") # <-- I added indentation
                cursor.execute(
                    """
                    INSERT INTO cities (name, bbox, scanned) 
                    VALUES (%s, %s, %s) 
                    RETURNING id
                    """,
                    (city_name, json.dumps(city_bbox), False)
                )
                city_id = cursor.fetchone()[0]
                conn.commit()
                # Return new ID and scanned status (which is False)
                return city_id, False, True # <-- ADD ', True'
                
    except Exception as e:
        print(f"Error checking/creating city '{city_name}': {e}")
        conn.rollback()
        # Return None, None to signal an error
        return None, None, False # <-- ADD ', False'
                
    except Exception as e:
        print(f"Error checking/creating city '{city_name}': {e}")
        conn.rollback()
        # Return None, None to signal an error
        return None, None, False
                
    except Exception as e:
        print(f"Error checking/creating city '{city_name}': {e}")
        conn.rollback()
        # Return None, None to signal an error
        return None, None

# --- NEW FUNCTION 3 (from your file) ---
def mark_city_as_scanned(conn, city_id):
    """Updates a city's 'scanned' status to TRUE."""
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE cities SET scanned = TRUE WHERE id = %s", (city_id,))
            conn.commit()
        print(f"Successfully marked city ID {city_id} as scanned.")
    except Exception as e:
        print(f"Error marking city {city_id} as scanned: {e}")
        conn.rollback()

# --- NEW FUNCTION 4 ---
def get_unscanned_cities(conn):
    """
    Queries the database for all cities that have not been scanned.
    Returns a list of dictionaries.
    """
    cities_to_scan = []
    try:
        # RealDictCursor makes the result a list of dicts
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT id, name, bbox FROM cities WHERE scanned = FALSE")
            results = cursor.fetchall()
            if results:
                # Convert RealDictRow to plain dict
                cities_to_scan = [dict(row) for row in results] 
        
        print(f"Found {len(cities_to_scan)} unscanned cities in the database.")
        return cities_to_scan
    except Exception as e:
        print(f"Error fetching unscanned cities: {e}")
        return []