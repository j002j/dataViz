import os
import sys
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

    # Load BBOX from environment
    try:
        TARGET_BBOX = {
            "west": float(os.getenv("TARGET_BBOX_WEST")),
            "south": float(os.getenv("TARGET_BBOX_SOUTH")),
            "east": float(os.getenv("TARGET_BBOX_EAST")),
            "north": float(os.getenv("TARGET_BBOX_NORTH")),
        }
    except Exception as e:
        print(f"Error loading bounding box coordinates from .env file: {e}")
        return

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

    # --- Step 2: Get Image Info ---
    image_list = mp.fetch_image_data(
        MAPILLARY_ACCESS_TOKEN, 
        TARGET_BBOX
    )
    
    if not image_list:
        print("Pipeline finished: No images to process.")
        db_conn.close()
        return
        
    # --- Step 3: Load YOLO Model ---
    print("\nLoading YOLOv8 model...")
    try:
        model = YOLO('yolov8n.pt') 
        print("YOLOv8 model loaded successfully.")
    except Exception as e:
        print(f"Error loading YOLO model: {e}")
        db_conn.close()
        return

    # --- Step 4: Process Images & Save to DB ---
    mp.process_images(
        image_list, 
        model, 
        OUTPUT_DIR,
        db_conn  # Pass the database connection
    )
    
    # --- Step 5: Clean up ---
    db_conn.close()
    print("Database connection closed.")
    print("\nPipeline finished.")

if __name__ == "__main__":
    run_pipeline()