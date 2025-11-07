"""
Main script to run the Mapillary processing pipeline.

This script replaces the old JSON-based city loading with a database-driven
approach. It connects to the database, fetches a list of cities that
have not been scanned (scanned=FALSE), and processes them one by one.

If a city is processed successfully, it is marked as scanned=TRUE in the
database to prevent reprocessing.
"""

import os
import sys
import json
import sqlite3 # Import for database operations
import math
import numpy as np

# Add the project root to the Python path to allow imports from 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipelines.mapillary_processor import MapillaryProcessor
from src.db.db_utils import (
    get_db_connection, 
    create_detections_table, 
    create_cities_table,
    get_unscanned_cities,
    mark_city_as_scanned,
    get_and_lock_one_unscanned_city
)

from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

def process_city(conn, city_id, city_name, bbox, pbar):
    """
    Initializes a MapillaryProcessor for a specific city and starts
    the processing for its bounding box.
    """
    
    # Check if the bbox data is valid...
    if not bbox or 'west' not in bbox or 'south' not in bbox or 'east' not in bbox or 'north' not in bbox:
        print(f"  > Skipping city '{city_name}' (ID: {city_id}) due to missing or invalid bbox keys.")
        return

    # Update the progress bar description
    # pbar.set_description(f"Starting {city_name}")

    access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")
    if not access_token:
        print("ERROR: MAPILLARY_ACCESS_TOKEN environment variable not set.")
        return

    processor = MapillaryProcessor(
        conn=conn,
        city_id=city_id,
        access_token=access_token,
        model_path="yolov8n.pt"
    )
    
    main_bbox = [
        bbox['west'],   # min_lon
        bbox['south'],  # min_lat
        bbox['east'],   # max_lon
        bbox['north']   # max_lat
    ]
    
    # Pass the progress bar to the processor
    processor.process_bbox(main_bbox, pbar)
    print(f"Finished processing for city: {city_name}")

# --- REPLACE THIS ENTIRE FUNCTION ---
def main():
    """
    Main execution function.
    Connects to the DB, then enters a loop to process
    one city at a time from the queue.
    """
    conn = None
    try:
        # 1. Connect to the database
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database. Exiting.")
            return
            
        # 2. Ensure tables exist
        create_cities_table(conn)
        create_detections_table(conn)

        print(f"Process {os.getpid()} starting...")

        # 3. --- NEW: Main processing loop ---
        # Keep processing until the queue is empty
        while True:
            # 4. Get ONE city from the queue.
            # This function is now atomic and process-safe.
            city = get_and_lock_one_unscanned_city(conn)

            # 5. Check if we are done
            if city is None:
                print(f"Process {os.getpid()} found no more cities. Exiting.")
                break # Exit the while loop

            # --- We have a city to process ---
            city_id = city['id']
            city_name = city['name']
            city_bbox = city['bbox']
            
            print(f"\n--- Process {os.getpid()} processing: {city_name} (ID: {city_id}) ---")
            
            try:
                # We can't have a total pbar, so we pass None
                # (We will fix the processor in the next step)
                process_city(conn, city_id, city_name, city_bbox, pbar=None)
                
                # We no longer need to mark as scanned,
                # it was already done by get_and_lock_one_unscanned_city
                print(f"Process {os.getpid()} finished {city_name}.")
                
            except Exception as e:
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(f"ERROR: Process {os.getpid()} failed on {city_name}: {e}")
                print(f"City {city_name} (ID: {city_id}) is marked as scanned but FAILED.")
                print(f"You may need to manually reset it (scanned=0).")
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                continue # Move to the next city

        print(f"Process {os.getpid()} finished all work.")

    except Exception as e:
        print(f"A critical error occurred in process {os.getpid()}: {e}")
    finally:
        if conn:
            conn.close()
            print(f"Process {os.getpid()} closed database connection.")


if __name__ == "__main__":
    main()
