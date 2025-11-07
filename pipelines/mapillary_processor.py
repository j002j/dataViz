"""
This module contains the MapillaryProcessor class, which handles:
1. Tiling a large bounding box.
2. Fetching Mapillary images for each tile.
3. Running YOLO object detection on each image.
4. Cropping detected 'person' objects.
5. Saving cropped images to a folder.
6. NEW: Saving detection metadata to the PostgreSQL database.
"""

import os
import requests
import cv2
import numpy as np
from ultralytics import YOLO
import time
from datetime import datetime, timezone  # --- MODIFIED IMPORT ---
import json
import sqlite3 # Import for database operations
import math
from tqdm import tqdm

class MapillaryProcessor:
    """
    Processes a geographic bounding box to find images,
    detect people, and save cropped images and detection data.
    """
    
    def __init__(self, conn, city_id, access_token, model_path="yolov8n.pt"):
        """
        Initializes the processor.

        Args:
            conn: An active psycopg2 database connection.
            city_id: The ID of the city being processed (for foreign key).
            access_token: Mapillary API access token.
            model_path: Path to the YOLOv8 model file.
        """
        self.conn = conn
        self.city_id = city_id
        self.access_token = access_token
        self.headers = {"Authorization": f"OAuth {self.access_token}"}
        
        # Load the YOLO model
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        print("YOLO model loaded.")
        
        # Define the output directory for cropped images
        self.output_dir = "cropped_people"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Define the class ID for 'person' (COCO dataset)
        self.person_class_id = 0

    def _tile_bbox(self, main_bbox, tile_size_deg=0.05):
        """
        Splits a large bounding box into smaller square tiles.
        
        Args:
            main_bbox: [min_lon, min_lat, max_lon, max_lat]
            tile_size_deg: The side length of each square tile in degrees.

        Yields:
            A list [min_lon, min_lat, max_lon, max_lat] for each tile.
        """
        min_lon, min_lat, max_lon, max_lat = main_bbox
        
        lon_steps = np.arange(min_lon, max_lon, tile_size_deg)
        lat_steps = np.arange(min_lat, max_lat, tile_size_deg)
        
        for lon in lon_steps:
            for lat in lat_steps:
                tile = [
                    lon, 
                    lat, 
                    lon + tile_size_deg, 
                    lat + tile_size_deg
                ]
                yield tile

    def fetch_images_in_tile(self, tile_bbox):
        """
        Fetches image data from Mapillary for a given tile.
        
        Args:
            tile_bbox: [min_lon, min_lat, max_lon, max_lat]

        Returns:
            A list of image data dictionaries, or None if the request fails.
        """
        
        # Round the coordinates to 6 decimal places to avoid API errors
        bbox_str = (
            f"{tile_bbox[0]:.6f},"  # min_lon
            f"{tile_bbox[1]:.6f},"  # min_lat
            f"{tile_bbox[2]:.6f},"  # max_lon
            f"{tile_bbox[3]:.6f}"   # max_lat
        )
        
        # Mapillary API endpoint for image search
        url = (
            f"https://graph.mapillary.com/images"
            f"?access_token={self.access_token}"
            f"&fields=id,captured_at,geometry" # Get fields needed for DB
            f"&bbox={bbox_str}"
            f"&limit=100" # Request max images per tile
        )
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # Raise an error for bad status codes
            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"  > API Error: {e}")
            return None

    # --- THIS IS THE FIXED FUNCTION ---
    def _save_detection_to_db(self, cropped_file, original_image_id, captured_at_data, location, bounding_box_original):
        """
        Saves a single detection record to the 'mapillary_detections' table
        using sqlite3-compatible syntax.
        """
        
        # --- 1. Parse Timestamp ---
        parsed_captured_at = None
        try:
            if isinstance(captured_at_data, str):
                # It's a string, parse it as ISO format
                parsed_captured_at = datetime.fromisoformat(captured_at_data.replace('Z', '+00:00'))
            
            elif isinstance(captured_at_data, (int, float)):
                # It's a number. Assume it's a millisecond timestamp.
                timestamp_sec = captured_at_data / 1000.0
                parsed_captured_at = datetime.fromtimestamp(timestamp_sec, tz=timezone.utc)
            
            elif captured_at_data is not None:
                # It's some other type we don't recognize.
                 print(f"    > WARNING: Unknown 'captured_at' format ({type(captured_at_data)}). Saving as NULL.")
        
        except Exception as e:
             print(f"    > WARNING: Failed to parse timestamp '{captured_at_data}': {e}")
             # Continue with parsed_captured_at = None


        # --- 2. Save to Database ---
        try:
            sql_query = """
            INSERT INTO mapillary_detections (
                cropped_file, 
                original_image_id, 
                captured_at, 
                location, 
                bounding_box_original, 
                city_id
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            # Data to be inserted (use ? placeholders)
            data = (
                cropped_file,
                int(original_image_id),
                parsed_captured_at,
                json.dumps(location),   # Convert dict to JSON string for TEXT
                json.dumps(bounding_box_original), # Convert list to JSON string for TEXT
                self.city_id
            )
            
            # Use the connection as the context manager.
            # This automatically commits on success or rolls back on error.
            with self.conn:
                self.conn.execute(sql_query, data)
                
            print(f"    > Saved detection {cropped_file} to database.")
            
        except Exception as e:
            # The 'with self.conn' block already handled the rollback
            print(f"    > ERROR: Failed to save detection to DB: {e}")


    def process_image(self, image_data):
        """
        Downloads an image, runs YOLO detection, crops 'person' objects,
        and saves the cropped image and detection data.
        """
        image_id = image_data['id']
        
        try:
            # 1. Get image download URL
            image_url = f"https://graph.mapillary.com/{image_id}?fields=thumb_2048_url&access_token={self.access_token}"
            response = requests.get(image_url, headers=self.headers)
            response.raise_for_status()
            thumb_url = response.json().get('thumb_2048_url')
            
            if not thumb_url:
                print(f"  > No 2048px thumbnail for image {image_id}")
                return

            # 2. Download the image
            image_response = requests.get(thumb_url)
            image_response.raise_for_status()
            
            # Convert image data to OpenCV format
            image_array = np.frombuffer(image_response.content, np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                print(f"  > Failed to decode image {image_id}")
                return

            # 3. Run YOLO detection
            results = self.model(image, verbose=False) # verbose=False silences YOLO logs
            
            detections_found = 0
            
            # 4. Process results
            for i, box in enumerate(results[0].boxes):
                if int(box.cls) == self.person_class_id:
                    detections_found += 1
                    
                    # Get bounding box coordinates (normalized)
                    # We use xyxyn for normalized [xmin, ymin, xmax, ymax]
                    norm_coords = box.xyxyn.tolist()[0]
                    
                    # Convert normalized coords to pixel coords
                    h, w, _ = image.shape
                    xmin = int(norm_coords[0] * w)
                    ymin = int(norm_coords[1] * h)
                    xmax = int(norm_coords[2] * w)
                    ymax = int(norm_coords[3] * h)

                    # 5. Crop the image
                    crop_img = image[ymin:ymax, xmin:xmax]
                    
                    # Create a unique filename
                    crop_filename = os.path.join(
                        self.output_dir, 
                        f"{image_id}_person_{i}.jpg"
                    )
                    
                    # 6. Save the cropped image
                    cv2.imwrite(crop_filename, crop_img)
                    
                    # 7. NEW: Save detection metadata to the database
                    # --- MODIFIED FUNCTION CALL ---
                    self._save_detection_to_db(
                        cropped_file=os.path.basename(crop_filename),
                        original_image_id=image_id,
                        captured_at_data=image_data.get('captured_at'), # Use .get() for safety
                        location=image_data['geometry'],
                        bounding_box_original=norm_coords # Save the normalized bbox
                    )

            if detections_found > 0:
                print(f"  > Processed image {image_id}, found {detections_found} person(s).")
            
        except Exception as e:
            print(f"  > Failed to process image {image_id}: {e}")

    def process_bbox(self, main_bbox, pbar): # pbar may be None
        """
        Orchestrates the processing of a large bounding box by
        tiling it and processing images in each tile.
        """
        
        GRID_SIZE = 0.0025
        
        snapped_min_lon = math.floor(main_bbox[0] / GRID_SIZE) * GRID_SIZE
        snapped_min_lat = math.floor(main_bbox[1] / GRID_SIZE) * GRID_SIZE
        snapped_max_lon = math.ceil(main_bbox[2] / GRID_SIZE) * GRID_SIZE
        snapped_max_lat = math.ceil(main_bbox[3] / GRID_SIZE) * GRID_SIZE
        
        snapped_bbox = [snapped_min_lon, snapped_min_lat, snapped_max_lon, snapped_max_lat]
        
        print(f"Snapped main BBOX to {GRID_SIZE} grid: {snapped_bbox}")

        tiles = list(self._tile_bbox(snapped_bbox))
        
        # --- NEW: Use a local tqdm if pbar is None ---
        # This gives us a progress bar for the *current city*
        local_pbar = tqdm(total=len(tiles), unit="tile", desc=f"City Tiles")
        
        for i, tile in enumerate(tiles, 1):
            images = self.fetch_images_in_tile(tile)
            
            if images is None:
                print("  > Skipping tile due to API error.")
            elif not images:
                pass
            else:
                for image_data in images:
                    self.process_image(image_data)
                
            time.sleep(1)
            
            # --- Update the correct progress bar ---
            if pbar:
                pbar.update(1) # Update global pbar (if we ever add it back)
            else:
                local_pbar.update(1) # Update local city pbar
        
        local_pbar.close() # Close the local pbar
        print("Finished processing all tiles for this city.")