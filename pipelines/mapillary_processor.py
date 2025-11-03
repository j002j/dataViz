import os
import requests
import cv2
import json
import uuid
import mapillary.interface as mly
from ultralytics import YOLO
from psycopg2 import sql, extras

def fetch_image_data(token, bbox_dict):
    """
    Queries the Mapillary v4 Graph API directly for images in a bounding box.
    """
    print("Connecting to Mapillary API...")
    mly.set_access_token(token)
    
    search_url = "https://graph.mapillary.com/images"
    bbox_string = f"{bbox_dict['west']},{bbox_dict['south']},{bbox_dict['east']},{bbox_dict['north']}"
    
    params = {
        'access_token': token,
        'fields': 'id,geometry,captured_at',  # <-- ADDED 'captured_at'
        'bbox': bbox_string
    }

    print(f"Searching for images in bounding box: {bbox_string}")

    try:
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        features = data.get('data', [])
        
        if not features:
            print("No images found in the specified bounding box.")
            return []
            
        print(f"Found {len(features)} images. Fetching thumbnail URLs...")
        image_list = []

        for i, feature in enumerate(features):
            image_id = feature['id']
            location = feature['geometry']['coordinates']
            captured_at = feature.get('captured_at') # <-- GET 'captured_at'
            
            # Convert timestamp from milliseconds (str) to seconds (float) for database
            if captured_at:
                captured_at_seconds = float(captured_at) / 1000.0
            
            try:
                image_url = mly.image_thumbnail(image_id, resolution=2048)
            except Exception as e:
                print(f"  - Could not get thumbnail for {image_id}: {e}. Skipping.")
                continue
            
            image_list.append({
                'id': image_id,
                'location': location,
                'url': image_url,
                'captured_at': captured_at_seconds # <-- STORE 'captured_at'
            })
            
        print(f"Successfully retrieved data for {len(image_list)} images.")
        return image_list

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Mapillary API: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []

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