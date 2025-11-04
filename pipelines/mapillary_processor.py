import os
import requests
import cv2
import json
import uuid
import time  # <-- ADDED
import numpy as np  # <-- ADDED
import mapillary.interface as mly
from ultralytics import YOLO
from psycopg2 import sql, extras

def generate_bbox_tiles(bbox_dict, step=0.1):
    """
    Generates a grid of smaller bounding box "tiles" from a large one.
    Uses the dictionary format.
    A step of 0.1 degrees (area 0.01) is a safe bet for the Mapillary API.
    """
    # Extract values
    min_lon = bbox_dict['west']
    min_lat = bbox_dict['south']
    max_lon = bbox_dict['east']
    max_lat = bbox_dict['north']
    
    lon_steps = np.arange(min_lon, max_lon, step)
    lat_steps = np.arange(min_lat, max_lat, step)

    for min_lon_tile in lon_steps:
        for min_lat_tile in lat_steps:
            max_lon_tile = min_lon_tile + step
            max_lat_tile = min_lat_tile + step
            
            # Ensure tile doesn't go outside the original max bounds
            if max_lon_tile > max_lon:
                max_lon_tile = max_lon
            if max_lat_tile > max_lat:
                max_lat_tile = max_lat
            
            # Return in the same dict format
            yield {
                "west": min_lon_tile,
                "south": min_lat_tile,
                "east": max_lon_tile,
                "north": max_lat_tile
            }

def fetch_image_data(token, bbox_dict):
    """
    Queries the Mapillary v4 Graph API for images in a bounding box.
    HANDLES TILING for large bounding boxes to prevent 500 errors.
    """
    print("Connecting to Mapillary API...")
    mly.set_access_token(token)
    
    # --- NEW TILING LOGIC ---
    # Generate the list of small tiles
    tiles = list(generate_bbox_tiles(bbox_dict, step=0.1))
    print(f"Divided large bounding box into {len(tiles)} tiles for querying.")
    
    all_features = {} # Use a dict to store unique features by ID
    search_url = "https://graph.mapillary.com/images"
    
    for i, tile_bbox_dict in enumerate(tiles):
        bbox_string = f"{tile_bbox_dict['west']},{tile_bbox_dict['south']},{tile_bbox_dict['east']},{tile_bbox_dict['north']}"
        
        params = {
            'access_token': token,
            'fields': 'id,geometry,captured_at',
            'bbox': bbox_string
        }
        
        print(f"  -> Querying tile {i+1}/{len(tiles)}: {bbox_string}")

        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            
            features_in_tile = data.get('data', [])
            if features_in_tile:
                print(f"    -> Found {len(features_in_tile)} images.")
                # Add to our dict, automatically handling duplicates from overlapping tiles
                for feature in features_in_tile:
                    all_features[feature['id']] = feature
            
            # IMPORTANT: Be polite to the API, add a small delay
            time.sleep(0.2) # 200ms delay

        except requests.exceptions.RequestException as e:
            # Catch errors but continue the loop
            print(f"    -> WARNING: Error on tile {i+1}: {e}. Skipping this tile.")
            continue # Skip this tile, move to the next
        except Exception as e:
            print(f"    -> WARNING: An unexpected error occurred on tile {i+1}: {e}. Skipping tile.")
            continue
    # --- END NEW TILING LOGIC ---

    # Now, process the combined, unique features
    unique_features_list = list(all_features.values())

    if not unique_features_list:
        print("No images found in any tiles for the specified bounding box.")
        return []
        
    print(f"\nFound {len(unique_features_list)} unique images total. Fetching thumbnail URLs...")
    image_list = []

    # This part of the function (thumbnail fetching) is the same as before
    for i, feature in enumerate(unique_features_list):
        image_id = feature['id']
        location = feature['geometry']['coordinates']
        captured_at = feature.get('captured_at')
        
        if captured_at:
            captured_at_seconds = float(captured_at) / 1000.0
        else:
            captured_at_seconds = None # Handle missing capture_at
        
        try:
            image_url = mly.image_thumbnail(image_id, resolution=2048)
        except Exception as e:
            print(f"  - Could not get thumbnail for {image_id}: {e}. Skipping.")
            continue
        
        image_list.append({
            'id': image_id,
            'location': location,
            'url': image_url,
            'captured_at': captured_at_seconds
        })
        
    print(f"Successfully retrieved data for {len(image_list)} images.")
    return image_list


def download_image(url, path):
    """Downloads an image from a URL and saves it to a path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False

def insert_detection(conn, data):
    """Inserts a single detection record into the database."""
    insert_query = """
    INSERT INTO mapillary_detections
        (cropped_file, original_image_id, captured_at, location, bounding_box_original)
    VALUES
        (%(cropped_file)s, %(original_image_id)s, TO_TIMESTAMP(%(captured_at)s), %(location)s, %(bounding_box)s)
    """
    try:
        with conn.cursor() as cursor:
            # Use psycopg2's 'execute' for safe parameter substitution
            cursor.execute(insert_query, data)
            conn.commit()
    except Exception as e:
        print(f"  -> Error inserting detection to DB: {e}")
        conn.rollback()

def process_images(image_list, model, output_dir, db_conn):
    """
    Downloads, processes, saves crops, and writes metadata to the database.
    """
    temp_image_path = os.path.join(output_dir, "temp_image.jpg")
    
    if not image_list:
        print("No images to process.")
        return
        
    for i, info in enumerate(image_list):
        print(f"\nProcessing image {i+1}/{len(image_list)} (ID: {info['id']})")
        
        if not download_image(info['url'], temp_image_path):
            continue
            
        img = cv2.imread(temp_image_path)
        if img is None:
            print("Failed to read downloaded image.")
            continue
            
        results = model(temp_image_path, classes=[0], verbose=False) 
        boxes = results[0].boxes
        
        if len(boxes) == 0:
            print("  -> No people detected.")
            continue
            
        print(f"  -> Detected {len(boxes)} person(s). Cropping and saving...")
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped_person = img[y1:y2, x1:x2]
            
            unique_id = uuid.uuid4().hex[:8]
            output_filename = f"{info['id']}_person_{unique_id}.jpg"
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                cv2.imwrite(output_path, cropped_person)
            except cv2.error:
                print(f"    Error saving crop. Skipping.")
                continue

            # Prepare data for database insertion
            detection_data = {
                "cropped_file": output_filename,
                "original_image_id": int(info['id']),
                "captured_at": info['captured_at'],
                "location": json.dumps({
                    'longitude': info['location'][0],
                    'latitude': info['location'][1]
                }),
                "bounding_box": json.dumps([x1, y1, x2, y2])
            }
            
            # Insert this detection into the database
            insert_detection(db_conn, detection_data)
            
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    
    print("\nImage processing complete.")