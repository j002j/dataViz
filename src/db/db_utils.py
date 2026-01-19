import os
import sqlite3
import json
import time
from sqlite3 import Error

# Define the path for the SQLite database file
DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "pipeline.db")

def get_db_connection(timeout=30.0):
    """Establishes and returns a sqlite3 connection object."""
    os.makedirs(DB_DIR, exist_ok=True)
    try:
        # Increase timeout to handle locking during heavy concurrency
        conn = sqlite3.connect(DB_PATH, timeout=timeout)
        conn.row_factory = sqlite3.Row
        
        # Enable Write-Ahead Logging for concurrency (Readers don't block Writers)
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA synchronous = NORMAL;") # Slight speed up, less safe on power loss
        
        return conn
    except Error as e:
        print(f"ERROR: Could not connect to the SQLite database: {e}")
        return None

def create_tables(conn):
    """Creates tables and handles migrations."""
    
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

    # 2. Mapillary Images Table
    # Added processing_status for granular tracking
    conn.execute("""
    CREATE TABLE IF NOT EXISTS mapillary_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image_id BIGINT UNIQUE NOT NULL, 
        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
        captured_at DATETIME,
        location TEXT,
        file_path TEXT,
        processing_status TEXT DEFAULT 'pending', 
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # MIGRATION: Check if processing_status exists, if not add it
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mapillary_images)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'processing_status' not in columns:
        print("Migrating: Adding processing_status to mapillary_images...")
        conn.execute("ALTER TABLE mapillary_images ADD COLUMN processing_status TEXT DEFAULT 'pending'")
        # Reset any old data to pending if needed, or assume done? 
        # For safety, let's leave them as pending default for new rows.

    # 3. Detections Table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS mapillary_detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
        original_image_id BIGINT, 
        captured_at DATETIME,
        location TEXT,
        confidence INTEGER, 
        bounding_box_detection TEXT,
        crop_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Check for crop_path migration
    cursor.execute("PRAGMA table_info(mapillary_detections)")
    det_columns = [info[1] for info in cursor.fetchall()]
    if 'crop_path' not in det_columns:
         print("Migrating: Adding crop_path to mapillary_detections...")
         conn.execute("ALTER TABLE mapillary_detections ADD COLUMN crop_path TEXT")
    
    # 4. Clothing Measurements Table (New)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS clothing_measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        detection_id INTEGER REFERENCES mapillary_detections(id) ON DELETE CASCADE,
        category VARCHAR(50),
        confidence REAL,
        color_h REAL,
        color_s REAL,
        color_v REAL,
        texture_score REAL,
        area_ratio REAL,
        bbox_json TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. MIGRATION: Add 'clothing_status' to mapillary_detections
    # This ensures we don't re-process people we've already analyzed
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(mapillary_detections)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'clothing_status' not in columns:
        print("Migrating: Adding clothing_status to mapillary_detections...")
        conn.execute("ALTER TABLE mapillary_detections ADD COLUMN clothing_status TEXT DEFAULT 'pending'")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clothing_status ON mapillary_detections(clothing_status)")

    print("Database tables verified.")

    print("Database tables verified/created.")

# --- PRODUCER (DOWNLOADER) FUNCTIONS ---

def get_and_lock_city_for_download(conn):
    """Finds a city pending download and locks it."""
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            
            # CHANGED: Added 'ORDER BY population DESC' to prioritize populous cities
            query = "SELECT id, name, bbox, population FROM cities WHERE download_status = 'pending' ORDER BY population DESC LIMIT 1"
            cursor.execute(query)
            row = cursor.fetchone()
            
            if row:
                city = dict(row)
                if city['bbox']:
                    # This keeps your original json.loads which prevents the "unpack" error
                    city['bbox'] = json.loads(city['bbox'])
                
                cursor.execute("UPDATE cities SET download_status = 'processing' WHERE id = ?", (city['id'],))
                return city
            return None
    except Exception as e:
        print(f"Error locking city: {e}")
        return None

def mark_city_download_complete(conn, city_id):
    try:
        with conn:
            conn.execute(
                "UPDATE cities SET download_status = 'done', downloaded_at = CURRENT_TIMESTAMP WHERE id = ?", 
                (city_id,)
            )
    except Error as e:
        print(f"Error marking city complete: {e}")

def get_existing_image_ids(conn, city_id):
    cursor = conn.cursor()
    cursor.execute("SELECT image_id FROM mapillary_images WHERE city_id = ?", (city_id,))
    rows = cursor.fetchall()
    return {row['image_id'] for row in rows}

def insert_image_records_batch(conn, records):
    """
    Bulk insert images.
    records: list of dicts {'image_id', 'city_id', 'captured_at', 'location', 'file_path'}
    """
    if not records:
        return
    try:
        with conn:
            conn.executemany("""
            INSERT INTO mapillary_images (image_id, city_id, captured_at, location, file_path, processing_status)
            VALUES (:image_id, :city_id, :captured_at, :location, :file_path, 'pending')
            ON CONFLICT(image_id) DO NOTHING
            """, records)
    except Error as e:
        print(f"Error bulk inserting images: {e}")

# --- CONSUMER (DETECTOR) FUNCTIONS ---

def claim_batch_for_analysis(conn, batch_size=32, worker_id="gpu_worker"):
    """
    Atomically claims a batch of 'pending' images for processing.
    Returns a list of image rows.
    """
    try:
        with conn:
            cursor = conn.cursor()
            # Start transaction to ensure atomicity
            cursor.execute("BEGIN IMMEDIATE")
            
            # 1. Select IDs to lock
            # We filter by pending. We don't care about city status, just image status.
            query = f"""
                SELECT id FROM mapillary_images 
                WHERE processing_status = 'pending' 
                LIMIT {batch_size}
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                return []
            
            ids_to_lock = [row['id'] for row in rows]
            
            # 2. Mark them as processing so other workers don't grab them
            # SQLite doesn't have "SKIP LOCKED", so we must update immediately inside the transaction
            placeholders = ','.join(['?'] * len(ids_to_lock))
            update_query = f"""
                UPDATE mapillary_images 
                SET processing_status = 'processing' 
                WHERE id IN ({placeholders})
            """
            cursor.execute(update_query, ids_to_lock)
            
            # 3. Retrieve the full data for these locked IDs
            select_query = f"""
                SELECT * FROM mapillary_images 
                WHERE id IN ({placeholders})
            """
            cursor.execute(select_query, ids_to_lock)
            locked_images = cursor.fetchall()
            
            return [dict(row) for row in locked_images]
            
    except Error as e:
        print(f"Error claiming batch: {e}")
        return []

def mark_batch_analysis_complete(conn, image_ids):
    """Marks a list of image database IDs as completed."""
    if not image_ids:
        return
    try:
        with conn:
            placeholders = ','.join(['?'] * len(image_ids))
            sql = f"UPDATE mapillary_images SET processing_status = 'completed' WHERE id IN ({placeholders})"
            conn.execute(sql, tuple(image_ids))
    except Error as e:
        print(f"Error marking batch complete: {e}")

def insert_detections_batch(conn, detections):
    """
    Bulk insert detections.
    detections: list of dicts
    """
    if not detections:
        return
    try:
        with conn:
            conn.executemany("""
            INSERT INTO mapillary_detections (
                city_id, original_image_id, captured_at, location, confidence, bounding_box_detection, crop_path
            )
            VALUES (
                :city_id, :original_image_id, :captured_at, :location, :confidence, :bounding_box_detection, :crop_path
            )
            """, detections)
    except Error as e:
        print(f"Error inserting detections: {e}")

def get_pending_crops(conn, batch_size=1000):
    """Fetches crops that haven't been analyzed for clothing yet."""
    # We assume if a detection exists but has no entries in clothing_measurements, it needs processing.
    # OR better: Add an 'analysis_status' to mapillary_detections. 
    # For now, let's just grab ID/Path.
    try:
        cursor = conn.cursor()
        # Simple Logic: Find detections that are not yet "done". 
        # Ideally, add 'clothing_status' column to mapillary_detections for tracking.
        # Here we just select all for the demo.
        cursor.execute("SELECT id, crop_path FROM mapillary_detections WHERE crop_path IS NOT NULL LIMIT ?", (batch_size,))
        return [dict(row) for row in cursor.fetchall()]
    except Error as e:
        print(f"Error fetching crops: {e}")
        return []

def insert_clothing_batch(conn, items):
    """Bulk insert clothing vectors."""
    if not items: return
    try:
        with conn:
            conn.executemany("""
            INSERT INTO clothing_measurements (
                detection_id, category, confidence, 
                color_h, color_s, color_v, texture_score, 
                area_ratio, bbox_json
            ) VALUES (
                :detection_id, :category, :confidence, 
                :color_h, :color_s, :color_v, :texture_score, 
                :area_ratio, :bbox_json
            )
            """, items)
    except Error as e:
        print(f"Error inserting clothing: {e}")

def claim_detections_for_analysis(conn, batch_size=32):
    """
    Atomically claims a batch of 'pending' people detections.
    """
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            
            # 1. Find pending people that have a valid crop path
            query = f"""
                SELECT id FROM mapillary_detections 
                WHERE clothing_status = 'pending' 
                AND crop_path IS NOT NULL
                LIMIT {batch_size}
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            if not rows:
                return []
            
            ids_to_lock = [row['id'] for row in rows]
            
            # 2. Mark as processing
            placeholders = ','.join(['?'] * len(ids_to_lock))
            update_query = f"""
                UPDATE mapillary_detections 
                SET clothing_status = 'processing' 
                WHERE id IN ({placeholders})
            """
            cursor.execute(update_query, ids_to_lock)
            
            # 3. Return data
            select_query = f"""
                SELECT id, crop_path FROM mapillary_detections 
                WHERE id IN ({placeholders})
            """
            cursor.execute(select_query, ids_to_lock)
            return [dict(row) for row in cursor.fetchall()]
            
    except Exception as e:
        print(f"Error claiming detections: {e}")
        return []

def mark_clothing_analysis_complete(conn, detection_ids):
    """Marks detection rows as 'completed'."""
    if not detection_ids: return
    try:
        with conn:
            placeholders = ','.join(['?'] * len(detection_ids))
            sql = f"UPDATE mapillary_detections SET clothing_status = 'completed' WHERE id IN ({placeholders})"
            conn.execute(sql, tuple(detection_ids))
    except Exception as e:
        print(f"Error marking clothing analysis complete: {e}")

def insert_clothing_measurements(conn, measurements):
    """Bulk insert the extracted vectors."""
    if not measurements: return
    try:
        with conn:
            conn.executemany("""
            INSERT INTO clothing_measurements (
                detection_id, category, confidence, 
                color_h, color_s, color_v, texture_score, 
                area_ratio, bbox_json
            ) VALUES (
                :detection_id, :category, :confidence, 
                :color_h, :color_s, :color_v, :texture_score, 
                :area_ratio, :bbox_json
            )
            """, measurements)
    except Exception as e:
        print(f"Error inserting measurements: {e}")