import os
import sys
import json
from ultralytics import YOLO
# from dotenv import load_dotenv # <-- REMOVED

# We can import from 'src' directly because PYTHONPATH="/app" is set in the Dockerfile
from src.db.db_utils import (
    get_db_connection, 
    create_detections_table,
    create_cities_table,
    get_unscanned_cities, 
    mark_city_as_scanned
)
# The `mapillary_processor` import works because it's in the same `pipelines/` folder
import mapillary_processor as mp

# --- load_dotenv() was removed ---

def run_pipeline():
    """Main pipeline function."""
    
    MAPILLARY_ACCESS_TOKEN = os.getenv("MAPILLARY_ACCESS_TOKEN")
    if MAPILLARY_ACCESS_TOKEN == "YOUR_TOKEN_HERE" or not MAPILLARY_ACCESS_TOKEN:
        print("Error: MAPILLARY_ACCESS_TOKEN is not set in your .env file.")
        return

    # This path is relative to the /app WORKDIR
    OUTPUT_DIR = "cropped_people"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # --- Step 1: Connect to Database & Create Tables ---
    print("Initializing database connection...")
    db_conn = get_db_connection()
    if db_conn is None:
        print("Failed to connect to database. Exiting pipeline.")
        return
    
    # Ensure tables exist
    create_cities_table(db_conn) 
    create_detections_table(db_conn)

    # --- Step 2: Load YOLO Model ---
    print("\nLoading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt') 
        print("YOLOv8 model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        db_conn.close()
        return

    # --- Step 3: Get list of unscanned cities from DB ---
    cities_to_scan = get_unscanned_cities(db_conn)
    
    if not cities_to_scan:
        print("No unscanned cities found in the database. Pipeline finished.")
        db_conn.close()
        return
        
    print(f"Starting pipeline for {len(cities_to_scan)} cities.")

    # --- Step 4: Loop through each city and run the pipeline ---
    for city in cities_to_scan:
        city_id = city['id']
        city_name = city['name']
        city_bbox = city['bbox'] 
        
        print(f"\n==================================================")
        print(f"Processing city: {city_name} (ID: {city_id})")
        print(f"==================================================")

        # Get Image Info for this city
        image_list = mp.fetch_image_data(
            MAPILLARY_ACCESS_TOKEN, 
            city_bbox
        )
        
        if not image_list:
            print(f"No images found for {city_name}.")
            print(f"Skipping {city_name} for this run.")
            continue
            
        # Process Images & Save to DB for this city
        mp.process_images(
            image_list, 
            model, 
            OUTPUT_DIR,
            db_conn,
            city_id  
        )

        # If we successfully processed, mark the city as scanned
        print(f"Successfully processed {city_name}. Marking as scanned.")
        mark_city_as_scanned(db_conn, city_id)
    
    # --- Step 5: Clean up ---
    db_conn.close()
    print("\n==================================================")
    print("Database connection closed.")
    print("All cities processed. Pipeline finished.")

if __name__ == "__main__":
    run_pipeline()