import os
import sys
import json  # Import the json library
from ultralytics import YOLO
from dotenv import load_dotenv

# Add src directory to the Python path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now we can import from src and the local pipelines folder
from src.db.db_utils import get_db_connection, create_detections_table
import mapillary_processor as mp

# Load environment variables from .env file
load_dotenv()

def run_pipeline():
    """Main pipeline function."""
    
    MAPILLARY_ACCESS_TOKEN = os.getenv("MAPILLARY_ACCESS_TOKEN")
    if MAPILLARY_ACCESS_TOKEN == "YOUR_TOKEN_HERE" or not MAPILLARY_ACCESS_TOKEN:
        print("Error: MAPILLARY_ACCESS_TOKEN is not set in your .env file.")
        return

    # --- THIS IS THE NEW PART ---
    # Load city bounding boxes from the new JSON config file
    try:
        with open('config/cities.json', 'r') as f:
            cities_config = json.load(f)
        if not cities_config:
            print("Error: config/cities.json is empty or not found.")
            return
        print(f"Loaded {len(cities_config)} cities from config/cities.json")
    except Exception as e:
        print(f"Error loading config/cities.json: {e}")
        return
    # --- END NEW PART ---

    OUTPUT_DIR = "cropped_people"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # --- Step 1: Connect to Database & Create Table ---
    print("Initializing database connection...")
    db_conn = get_db_connection()
    if db_conn is None:
        print("Failed to connect to database. Exiting pipeline.")
        return
    
    # Ensure the table for our results exists
    create_detections_table(db_conn)

    # --- Step 2: Load YOLO Model (do this once) ---
    print("\nLoading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt') 
        print("YOLOv8 model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        db_conn.close()
        return

    # --- Step 3: Loop through each city and run the pipeline ---
    for city in cities_config:
        city_name = city['name']
        city_bbox = city['bbox']
        
        print(f"\n==================================================")
        print(f"Processing city: {city_name}")
        print(f"==================================================")

        # Get Image Info for this city
        image_list = mp.fetch_image_data(
            MAPILLARY_ACCESS_TOKEN, 
            city_bbox
        )
        
        if not image_list:
            print(f"No images found for {city_name}. Skipping.")
            continue
            
        # Process Images & Save to DB for this city
        mp.process_images(
            image_list, 
            model, 
            OUTPUT_DIR,
            db_conn  # Pass the database connection
        )
    
    # --- Step 4: Clean up ---
    db_conn.close()
    print("\n==================================================")
    print("Database connection closed.")
    print("All cities processed. Pipeline finished.")

if __name__ == "__main__":
    run_pipeline()