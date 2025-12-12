"""
Pipeline Stage 2: People Detection
Reads downloaded images from the DB, runs YOLOv8, and saves detection metadata.
Designed to run on GPU.
"""

import os
import sys
import cv2
import json
from ultralytics import YOLO
from tqdm import tqdm
import torch

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db.db_utils import (
    get_db_connection,
    get_and_lock_city_for_analysis,
    mark_city_analysis_complete,
    get_images_for_analysis,
    insert_detection,
    create_tables # Import to ensure schema matches
)

def process_city_detection(city, conn, model):
    city_id = city['id']
    city_name = city['name']
    print(f"\n>>> Starting DETECTION for: {city_name} (ID: {city_id})")
    
    # 1. Get images from DB
    # This row contains: id, image_id, city_id, captured_at, location, file_path
    images = get_images_for_analysis(conn, city_id)
    if not images:
        print("No images found in DB for this city. Marking as done.")
        mark_city_analysis_complete(conn, city_id)
        return

    print(f"Loaded {len(images)} images for analysis.")
    
    # 2. Iterate and Detect
    for img_row in tqdm(images, desc=f"Analyzing {city_name}"):
        file_path = img_row['file_path']
        original_image_id = img_row['image_id']
        captured_at = img_row['captured_at']
        location = img_row['location']
        
        # Verify file exists
        if not os.path.exists(file_path):
            continue
            
        # Run Inference
        results = model(file_path, verbose=False)
        
        # Process Results
        for result in results:
            for box in result.boxes:
                # Class 0 is 'person' in COCO
                if int(box.cls) == 0:
                    
                    # Get normalized bbox [x_min, y_min, x_max, y_max]
                    bbox_norm = box.xyxyn.tolist()[0]
                    
                    # Convert confidence to Integer percentage (0-100)
                    conf_int = int(float(box.conf) * 100)
                    
                    # Save to DB (New Schema)
                    detection_data = {
                        'city_id': city_id,
                        'original_image_id': original_image_id,
                        'captured_at': captured_at,
                        'location': location,
                        'confidence': conf_int,
                        'bounding_box_detection': json.dumps(bbox_norm)
                    }
                    insert_detection(conn, detection_data)
    
    # 3. Finish
    mark_city_analysis_complete(conn, city_id)
    print(f"Finished detection for {city_name}.")

def main():
    # Check for GPU
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    
    conn = get_db_connection()
    if not conn:
        return

    # Ensure tables are up to date (specifically detections table)
    create_tables(conn)

    # Load Model once
    print("Loading YOLOv8 model...")
    model = YOLO("yolov8n.pt")
    
    print("Detection Pipeline Started. Waiting for downloaded cities...")
    
    while True:
        # Get city that is DOWNLOADED but NOT ANALYZED
        city = get_and_lock_city_for_analysis(conn)
        
        if not city:
            print("No cities ready for analysis. Sleeping 10s...")
            import time
            time.sleep(10)
            continue
            
        try:
            process_city_detection(city, conn, model)
        except Exception as e:
            print(f"ERROR processing {city['name']}: {e}")
            # Depending on error severity, you might want to break or continue

if __name__ == "__main__":
    main()