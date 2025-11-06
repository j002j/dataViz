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

# Add the project root to the Python path to allow imports from 'src'
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipelines.mapillary_processor import MapillaryProcessor
from src.db.db_utils import (
    get_db_connection, 
    create_detections_table, 
    create_cities_table,
    get_unscanned_cities,
    mark_city_as_scanned
)

def process_city(conn, city_id, city_name, bbox):
    """
    Initializes a MapillaryProcessor for a specific city and starts
    the processing for its bounding box.
    
    Args:
        conn: Active psycopg2 database connection.
        city_id: The primary key (ID) of the city from the 'cities' table.
        city_name: The name of the city (for logging).
        bbox: The bounding box dictionary (e.g., {'east': ..., 'west': ...}).
    """
    
    # --- THIS IS THE FIX ---
    # Check if the bbox data is valid and has the keys we expect from the DB
    if not bbox or 'west' not in bbox or 'south' not in bbox or 'east' not in bbox or 'north' not in bbox:
        print(f"  > Skipping city '{city_name}' (ID: {city_id}) due to missing or invalid bbox keys (east, west, north, south).")
        return
    # --- END OF FIX ---

    print(f"Initializing processor for city: {city_name} (ID: {city_id})")
    
    # Retrieve Mapillary Access Token from environment variables
    access_token = os.getenv("MAPILLARY_ACCESS_TOKEN")
    if not access_token:
        print("ERROR: MAPILLARY_ACCESS_TOKEN environment variable not set.")
        return

    # Initialize the processor, passing the DB connection and city_id
    processor = MapillaryProcessor(
        conn=conn,
        city_id=city_id,
        access_token=access_token,
        model_path="yolov8n.pt"  # Path to the model inside the container
    )
    
    # --- THIS IS THE FIX ---
    # Map the database keys (east, west, etc.) to the list format
    # that the process_bbox function expects: [min_lon, min_lat, max_lon, max_lat]
    main_bbox = [
        bbox['west'],   # min_lon
        bbox['south'],  # min_lat
        bbox['east'],   # max_lon
        bbox['north']   # max_lat
    ]
    # --- END OF FIX ---
    
    processor.process_bbox(main_bbox)
    print(f"Finished processing for city: {city_name}")


def main():
    """
    Main execution function.
    Connects to the DB, fetches unscanned cities, and processes them.
    """
    conn = None
    try:
        # 1. Connect to the database
        conn = get_db_connection()
        if conn is None:
            print("Failed to connect to the database. Exiting.")
            return
            
        # 2. Ensure tables exist
        # These functions have 'IF NOT EXISTS' so they are safe to run
        create_cities_table(conn)
        create_detections_table(conn)

        # 3. Fetch cities that have not been scanned yet
        print("Fetching unscanned cities from the database...")
        cities_to_scan = get_unscanned_cities(conn)

        if not cities_to_scan:
            print("No unscanned cities found. Exiting.")
            return

        print(f"Found {len(cities_to_scan)} cities to process.")

        # 4. Process each city one by one
        for i, city in enumerate(cities_to_scan, 1):
            city_id = city['id']
            city_name = city['name']
            city_bbox = city['bbox'] # This is a dict (e.g., {'east': ...})
            
            print(f"\n--- Processing City {i}/{len(cities_to_scan)} ---")
            print(f"City: {city_name} (ID: {city_id})")
            
            try:
                # Process the entire city
                process_city(conn, city_id, city_name, city_bbox)
                
                # 5. Mark city as scanned ONLY if processing was successful
                print(f"Successfully processed {city_name}, marking as scanned.")
                mark_city_as_scanned(conn, city_id)
                
            except Exception as e:
                # If one city fails, log the error and continue to the next
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(f"ERROR: An unexpected error occurred while processing {city_name}: {e}")
                print(f"City {city_name} (ID: {city_id}) will NOT be marked as scanned and will be retried on next run.")
                print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                continue # Move to the next city

        print("\nAll cities processed.")

    except Exception as e:
        print(f"A critical error occurred: {e}")
    finally:
        # 6. Always close the connection
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
