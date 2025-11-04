"""
This script populates the 'cities' table in the database.
It dynamically generates the city list by filtering a CSV
of world cities by population, then uses the OpenStreetMap
Nominatim API to find the bounding box for each.
"""

import requests
import json
import time
import csv
import os
import sys
from dotenv import load_dotenv

# Add src directory to the Python path to allow db_utils import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.db.db_utils import get_db_connection, check_or_create_city, create_cities_table

# This is a mandatory requirement from the Nominatim API.
USER_AGENT = 'CityBoxFinder/1.0 (anton.rabanus@study.hs-duesseldorf.de)'
# ---------------------

def get_city_bbox(city_name, headers):
    """
    Fetches the bounding box for a single city from Nominatim,
    prioritizing results explicitly typed as 'city'.
    (This is the robust function from our previous conversation)
    """
    url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(city_name)}&format=json&limit=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print(f"WARNING: No results found for '{city_name}'")
            return None

        best_match = None
        for result in data:
            if (result.get('class') == 'place' and 
                result.get('type') == 'city' and 
                result.get('boundingbox')):
                best_match = result
                break 

        if not best_match:
            print(f"  -> WARNING: No 'city' type match for '{city_name}'. Falling back to first result.")
            if data and data[0].get('boundingbox'):
                best_match = data[0]
            else:
                print(f"WARNING: No usable results with a bounding box for '{city_name}'. Skipping.")
                return None
            
        bbox_osm = best_match['boundingbox'] # [south, north, west, east]
        
        formatted_bbox = {
            "west": float(bbox_osm[2]),
            "south": float(bbox_osm[0]),
            "east": float(bbox_osm[3]),
            "north": float(bbox_osm[1])
        }
        
        city_data = {
            "name": best_match['display_name'],
            "search_term": city_name,
            "bbox": formatted_bbox
        }
        
        print(f"SUCCESS: Found '{best_match['display_name']}' (Type: {best_match.get('type')})")
        return city_data
            
    except requests.RequestException as e:
        print(f"EXCEPTION: {e} for '{city_name}'")
        return None

def load_cities_from_csv(csv_path, min_population):
    """
    Loads cities from the Simple Maps worldcities.csv file
    and filters them by population.
    """
    city_list = []
    print(f"Reading from {csv_path}...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    population_str = row.get('population', '0')
                    if not population_str:
                        continue 
                        
                    population = float(population_str)
                    
                    if population >= min_population:
                        city_name = row['city_ascii'] 
                        country_name = row['country']
                        search_term = f"{city_name}, {country_name}"
                        city_list.append(search_term)
                except (ValueError, TypeError):
                    continue 
    except FileNotFoundError:
        print("="*50)
        print(f"ERROR: Could not find the file '{csv_path}'.")
        print("Please download the 'Basic' database from:")
        print("https://simplemaps.com/data/world-cities")
        print("And place 'worldcities.csv' in your project root.")
        print("="*50)
        return None
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None
        
    return city_list

def main():
    """
    Main function to populate the 'cities' table in the database.
    """
    if USER_AGENT == 'MyCityBoxFinder/1.0 (your-email@example.com)':
        print("="*50)
        print("ERROR: Please edit the 'USER_AGENT' variable in this script")
        print("="*50)
        return
        
    # --- Load .env variables for database connection ---
    load_dotenv()

    # --- Connect to Database ---
    print("Initializing database connection...")
    db_conn = get_db_connection()
    if db_conn is None:
        print("Failed to connect to database. Exiting.")
        return
        
    # Ensure 'cities' table exists
    create_cities_table(db_conn)

    # --- Load Cities from CSV ---
    MIN_POPULATION = 400000
    INPUT_CSV = "assets/worldcities.csv"
    
    print(f"Loading cities from '{INPUT_CSV}' with population >= {MIN_POPULATION}...")
    city_list = load_cities_from_csv(INPUT_CSV, MIN_POPULATION)
    
    if city_list is None:
        print("Exiting due to error.")
        db_conn.close()
        return
        
    city_list = sorted(list(set(city_list)))
    print(f"Found {len(city_list)} unique cities matching criteria.")

    # --- Process and Save Cities to DB ---
    headers = {'User-Agent': USER_AGENT}
    cities_added = 0
    cities_skipped = 0

    print(f"Starting geocoding and database insertion for {len(city_list)} cities...")
    
    for i, city in enumerate(city_list):
        print(f"\n({i + 1}/{len(city_list)}) Processing: '{city}'")
        
        city_data = get_city_bbox(city, headers)
        
        if city_data:
            # --- SAVE TO DATABASE ---
            # This function inserts the city if it doesn't exist.
            city_id, is_scanned = check_or_create_city(
                db_conn, 
                city_data['name'], 
                city_data['bbox']
            )
            if city_id and not is_scanned:
                cities_added += 1
            elif is_scanned:
                print("  -> City already exists and is marked as scanned. Skipping.")
                cities_skipped += 1
            else:
                print("  -> Failed to add city to database.")
        
        # --- IMPORTANT: RATE LIMIT ---
        time.sleep(1)
        # -----------------------------

    db_conn.close()
    print("\n==================================================")
    print("Database connection closed.")
    print(f"Process complete. Added {cities_added} new cities. Skipped {cities_skipped}.")

if __name__ == "__main__":
    main()