import os
import sqlite3
import json
from sqlite3 import Error

# Define the path for the SQLite database file
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "pipeline.db")

def get_db_connection():
    """Establishes and returns a sqlite3 connection object."""
    os.makedirs(DB_DIR, exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        
        # Enable Write-Ahead Logging for concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        
        return conn
    except Error as e:
        print(f"ERROR: Could not connect to the SQLite database: {e}")
        return None

def create_tables(conn):
    """Creates all necessary tables for the new pipeline structure."""
    
    # 1. Cities Table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(255) UNIQUE NOT NULL,
        search_term VARCHAR(255),
        bbox TEXT,
        population INTEGER,
        
        download_status TEXT DEFAULT 'pending',
        downloaded_at DATETIME,
        
        analysis_status TEXT DEFAULT 'pending',
        analyzed_at DATETIME,
        
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # --- MIGRATION: Add columns to existing databases ---
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE cities ADD COLUMN search_term VARCHAR(255)")
    except sqlite3.OperationalError: pass 

    try:
        cursor.execute("ALTER TABLE cities ADD COLUMN population INTEGER")
    except sqlite3.OperationalError: pass
    # --------------------------------------------------------

    # 2. Mapillary Images Table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS mapillary_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_id BIGINT UNIQUE NOT NULL, 
        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
        captured_at DATETIME,
        location TEXT,
        file_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Detections Table (UPDATED SCHEMA)
    # We drop the old table to ensure the new schema is applied correctly
    conn.execute("DROP TABLE IF EXISTS mapillary_detections")
    
    conn.execute("""
    CREATE TABLE mapillary_detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
        original_image_id BIGINT, 
        captured_at DATETIME,
        location TEXT,
        confidence INTEGER, 
        bounding_box_detection TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    print("Database tables verified/created.")

# --- CITY MANAGEMENT (Locking Logic) ---

def get_and_lock_city_for_download(conn):
    """Atomically finds a city 'pending' download, sets to 'processing'."""
    return _get_and_lock_city(conn, "download_status")

def get_and_lock_city_for_analysis(conn):
    """Atomically finds a city 'done' downloading but 'pending' analysis."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE TRANSACTION")
            
            query = """
                SELECT id, name, bbox, population 
                FROM cities 
                WHERE download_status = 'done' 
                  AND analysis_status = 'pending' 
                LIMIT 1
            """
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                city = dict(row)
                if city['bbox']:
                    city['bbox'] = json.loads(city['bbox'])
                
                cursor.execute(
                    "UPDATE cities SET analysis_status = 'processing' WHERE id = ?", 
                    (city['id'],)
                )
                conn.commit()
                return city
            return None
    except Error as e:
        print(f"Error locking city for analysis: {e}")
        return None

def _get_and_lock_city(conn, status_column):
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE TRANSACTION")
            
            query = f"SELECT id, name, bbox, population FROM cities WHERE {status_column} = 'pending' LIMIT 1"
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                city = dict(row)
                if city['bbox']:
                    city['bbox'] = json.loads(city['bbox'])
                
                update = f"UPDATE cities SET {status_column} = 'processing' WHERE id = ?"
                cursor.execute(update, (city['id'],))
                conn.commit()
                return city
            return None
    except Error as e:
        print(f"Error locking city: {e}")
        return None

def mark_city_download_complete(conn, city_id):
    with conn:
        conn.execute(
            "UPDATE cities SET download_status = 'done', downloaded_at = CURRENT_TIMESTAMP WHERE id = ?", 
            (city_id,)
        )

def mark_city_analysis_complete(conn, city_id):
    with conn:
        conn.execute(
            "UPDATE cities SET analysis_status = 'done', analyzed_at = CURRENT_TIMESTAMP WHERE id = ?", 
            (city_id,)
        )

# --- IMAGE & DETECTION MANAGEMENT ---

def get_existing_image_ids(conn, city_id):
    cursor = conn.cursor()
    cursor.execute("SELECT image_id FROM mapillary_images WHERE city_id = ?", (city_id,))
    rows = cursor.fetchall()
    return {row['image_id'] for row in rows}

def insert_image_record(conn, image_data):
    try:
        with conn:
            conn.execute("""
            INSERT INTO mapillary_images (image_id, city_id, captured_at, location, file_path)
            VALUES (:image_id, :city_id, :captured_at, :location, :file_path)
            ON CONFLICT(image_id) DO NOTHING
            """, image_data)
    except Error as e:
        print(f"Error inserting image {image_data['image_id']}: {e}")

def get_images_for_analysis(conn, city_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mapillary_images WHERE city_id = ?", (city_id,))
    return cursor.fetchall()

def insert_detection(conn, detection_data):
    """
    Inserts a YOLO detection with full metadata.
    detection_data must contain:
    city_id, original_image_id, captured_at, location, confidence, bounding_box_detection
    """
    with conn:
        conn.execute("""
        INSERT INTO mapillary_detections (
            city_id, 
            original_image_id, 
            captured_at, 
            location, 
            confidence, 
            bounding_box_detection
        )
        VALUES (
            :city_id, 
            :original_image_id, 
            :captured_at, 
            :location, 
            :confidence, 
            :bounding_box_detection
        )
        """, detection_data)