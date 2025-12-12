"""
Pipeline Stage 1: Mass Image Downloader (Optimized)
Fetches metadata and downloads raw street view images for cities.
"""

import os
import sys
import asyncio
import aiohttp
import json
import time
from dotenv import load_dotenv
from tqdm.asyncio import tqdm
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.db.db_utils import (
    get_db_connection, create_tables,
    get_and_lock_city_for_download, mark_city_download_complete,
    get_existing_image_ids, insert_image_record
)
from pipelines.image_tools import tile_bbox

load_dotenv()
MAPILLARY_TOKEN = os.getenv("MAPILLARY_ACCESS_TOKEN")
IMAGE_ROOT_DIR = "mapillary_images"

# --- CONFIGURATION ---
TILE_SIZE = 0.02       # ~2km tiles (Much faster than 0.0025)
API_LIMIT = 2000       # Max images per API call
CONCURRENCY = 100      # Number of parallel download threads
# ---------------------

async def fetch_images_in_tile(session, tile_bbox):
    """Fetches image IDs and metadata for a geo-tile."""
    bbox_str = f"{tile_bbox[0]:.6f},{tile_bbox[1]:.6f},{tile_bbox[2]:.6f},{tile_bbox[3]:.6f}"
    url = "https://graph.mapillary.com/images"
    params = {
        'access_token': MAPILLARY_TOKEN,
        'fields': 'id,captured_at,geometry,thumb_2048_url',
        'bbox': bbox_str,
        'limit': API_LIMIT 
    }
    
    try:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return data.get('data', [])
            else:
                return []
    except Exception as e:
        print(f"API Error: {e}")
        return []

async def download_image(session, url, save_path):
    """Downloads bytes from URL and saves to file."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                with open(save_path, 'wb') as f:
                    f.write(content)
                return True
    except Exception:
        return False
    return False

async def process_city(city, db_conn):
    city_id = city['id']
    city_name = city['name']
    print(f"\n>>> Starting DOWNLOAD for: {city_name} (ID: {city_id})")

    # 1. Setup Directories
    city_dir = os.path.join(IMAGE_ROOT_DIR, city_name.replace(" ", "_").replace(",", ""))
    os.makedirs(city_dir, exist_ok=True)

    # 2. Get existing images
    existing_ids = get_existing_image_ids(db_conn, city_id)
    print(f"Found {len(existing_ids)} previously downloaded images. Skipping them.")

    # 3. Generate Tiles (Using larger TILE_SIZE)
    tiles = list(tile_bbox(city['bbox'], tile_size_deg=TILE_SIZE))
    print(f"Generated {len(tiles)} tiles to scan (Tile Size: {TILE_SIZE}°).")

    # 4. Async Processing
    sem = asyncio.Semaphore(CONCURRENCY)

    async with aiohttp.ClientSession() as session:
        
        # --- Phase A: Scan Tiles for Metadata ---
        images_to_download = []
        found_count = 0
        
        # We use a progress bar for the scanning phase
        scan_pbar = tqdm(tiles, desc="Scanning Area", unit="tile")
        
        for tile in scan_pbar:
            images = await fetch_images_in_tile(session, tile)
            
            for img in images:
                img_id = int(img['id'])
                if img_id not in existing_ids:
                    # Simple deduplication list check
                    # (For huge lists, a set is faster, but this is per-city)
                    if not any(x['id'] == img['id'] for x in images_to_download):
                         images_to_download.append(img)
                         found_count += 1
            
            # Update description to show found images live
            scan_pbar.set_description(f"Scanning Area (Found {found_count} images)")
        
        print(f"\nScan Complete. Found {len(images_to_download)} new images to download.")

        # --- Phase B: Download Images ---
        if not images_to_download:
            mark_city_download_complete(db_conn, city_id)
            print(f"No new images found for {city_name}. Marked as done.")
            return

        async def downloader(img_data):
            async with sem:
                img_id = img_data['id']
                url = img_data.get('thumb_2048_url')
                
                if not url: return
                
                # Parse Timestamp
                ts_str = img_data.get('captured_at')
                captured_at = None
                if ts_str:
                    try:
                        if isinstance(ts_str, (int, float)):
                            captured_at = datetime.fromtimestamp(ts_str/1000, timezone.utc)
                        else:
                            captured_at = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                    except: pass

                filename = f"{img_id}.jpg"
                file_path = os.path.join(city_dir, filename)
                
                # Perform Download
                success = await download_image(session, url, file_path)
                
                if success:
                    # Insert Metadata into DB
                    record = {
                        'image_id': int(img_id),
                        'city_id': city_id,
                        'captured_at': captured_at,
                        'location': json.dumps(img_data.get('geometry')),
                        'file_path': file_path
                    }
                    insert_image_record(db_conn, record)

        # Launch Download Tasks
        tasks = [downloader(img) for img in images_to_download]
        
        # Use asyncio.as_completed for the progress bar
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Downloading Files", unit="img"):
            await f
    
    # 5. Mark Done
    mark_city_download_complete(db_conn, city_id)
    print(f"Finished downloading {city_name}.")

async def main():
    if not MAPILLARY_TOKEN:
        print("ERROR: MAPILLARY_ACCESS_TOKEN not set.")
        return

    conn = get_db_connection()
    create_tables(conn)

    print(f"Download Pipeline Started (Concurrency: {CONCURRENCY}). Waiting for work...")
    
    while True:
        city = get_and_lock_city_for_download(conn)
        
        if not city:
            print("No 'pending' cities found. Sleeping 10s...")
            time.sleep(10)
            continue
            
        try:
            await process_city(city, conn)
        except Exception as e:
            print(f"CRITICAL FAILURE on city {city['name']}: {e}")
            time.sleep(5)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())