import os
import sqlite3
import json
from sqlite3 import Error

# Define the path for the SQLite database file
# This will live at /app/data/pipeline.db inside the container
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "pipeline.db")

def get_db_connection():
    """Establishes and returns a sqlite3 connection object."""
    
    # Ensure the data directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Use Row factory to access columns by name (like RealDictCursor)
        conn.row_factory = sqlite3.Row
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON;")
        print(f"Successfully connected to SQLite database at {DB_PATH}")
        return conn
    except Error as e:
        print(f"ERROR: Could not connect to the SQLite database: {e}")
        return None

def create_detections_table(conn):
    """
    Creates the mapillary_detections table for SQLite.
    """
    # SQLite syntax:
    # SERIAL PRIMARY KEY -> INTEGER PRIMARY KEY AUTOINCREMENT
    # JSONB -> TEXT
    # TIMESTAMPTZ -> DATETIME
    # NOW() -> CURRENT_TIMESTAMP
    create_table_query = """
    CREATE TABLE IF NOT EXISTS mapillary_detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cropped_file VARCHAR(255) NOT NULL,
        original_image_id BIGINT NOT NULL,
        captured_at DATETIME,
        location TEXT,
        bounding_box_original TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        city_id INTEGER REFERENCES cities(id) ON DELETE SET NULL
    );
    """
    try:
        with conn:
            conn.execute(create_table_query)
        print("Table 'mapillary_detections' is ready.")
    except Error as e:
        print(f"Error creating 'mapillary_detections' table: {e}")

def create_cities_table(conn):
    """Creates the cities table for SQLite."""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) UNIQUE NOT NULL,
        bbox TEXT,
        scanned BOOLEAN DEFAULT 0 NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    try:
        with conn:
            conn.execute(create_table_query)
        print("Table 'cities' is ready.")
    except Error as e:
        print(f"Error creating 'cities' table: {e}")

def check_or_create_city(conn, city_name, city_bbox):
    """
    Checks if a city exists in the DB (using sqlite3).
    If yes, returns its ID and 'scanned' status.
    If no, creates it and returns new ID.
    """
    try:
        with conn:
            cursor = conn.cursor()
            
            # 1. Check if city exists (use ? for parameters)
            cursor.execute("SELECT id, scanned FROM cities WHERE name = ?", (city_name,))
            result = cursor.fetchone()
            
            if result:
                # City exists, return its ID and scanned status
                # (scanned is 0 or 1, bool() handles this)
                city_id = result['id']
                is_scanned = bool(result['scanned'])
                return city_id, is_scanned, False # (id, is_scanned, was_created)
            else:
                # 2. City doesn't exist, insert it
                print(f"  -> Adding new city '{city_name}' to database.")
                sql_insert = """
                INSERT INTO cities (name, bbox, scanned) 
                VALUES (?, ?, ?)
                """
                # Store bbox as a JSON string (TEXT)
                # scanned=False becomes 0
                cursor.execute(sql_insert, (city_name, json.dumps(city_bbox), 0))
                
                # Get the new ID
                city_id = cursor.lastrowid
                
                # Return new ID and scanned status
                return city_id, False, True # (id, is_scanned, was_created)
                
    except Error as e:
        print(f"Error checking/creating city '{city_name}': {e}")
        return None, None, False

def mark_city_as_scanned(conn, city_id):
    """Updates a city's 'scanned' status to TRUE (1)."""
    try:
        with conn:
            # Use ? for parameters
            conn.execute("UPDATE cities SET scanned = 1 WHERE id = ?", (city_id,))
        print(f"Successfully marked city ID {city_id} as scanned.")
    except Error as e:
        print(f"Error marking city {city_id} as scanned: {e}")

def get_unscanned_cities(conn):
    """Queries for unscanned cities. Returns a list of dicts."""
    cities_to_scan = []
    try:
        with conn:
            cursor = conn.cursor()
            # scanned = 0 means FALSE
            cursor.execute("SELECT id, name, bbox FROM cities WHERE scanned = 0")
            results = cursor.fetchall()
            
            if results:
                # Convert sqlite3.Row objects to plain dicts
                # Also parse the bbox string back into a dict
                for row in results:
                    city = dict(row)
                    city['bbox'] = json.loads(city['bbox']) # Convert TEXT back to dict
                    cities_to_scan.append(city)
        
        print(f"Found {len(cities_to_scan)} unscanned cities in the database.")
        return cities_to_scan
    except Error as e:
        print(f"Error fetching unscanned cities: {e}")
        return []
    
def get_and_lock_one_unscanned_city(conn):
    """
    Atomically fetches one unscanned city and marks it as scanned
    to prevent other processes from grabbing it.
    """
    city = None
    try:
        with conn:
            # BEGIN IMMEDIATE locks the db for writing.
            # This is critical for parallel processing.
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE TRANSACTION")
            
            # Find one unscanned city
            cursor.execute(
                "SELECT id, name, bbox FROM cities WHERE scanned = 0 LIMIT 1"
            )
            result = cursor.fetchone()
            
            if result:
                # We found a city. Mark it as scanned *immediately*.
                city = dict(result) # Convert sqlite3.Row to dict
                cursor.execute(
                    "UPDATE cities SET scanned = 1 WHERE id = ?", (city['id'],)
                )
                print(f"Process {os.getpid()} locked city: {city['name']}")
                
                # Parse the bbox string
                if city['bbox']:
                    city['bbox'] = json.loads(city['bbox'])
            else:
                # No more cities
                print(f"Process {os.getpid()} found no unscanned cities.")
                
            # Commit the transaction to release the lock
            conn.commit()
            return city
            
    except sqlite3.Error as e:
        print(f"Error locking city: {e}")
        conn.rollback() # Roll back on error
        return None