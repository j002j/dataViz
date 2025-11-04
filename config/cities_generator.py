"""
This script fetches bounding box coordinates for a list of cities.
It dynamically generates the city list by filtering a CSV
of world cities by population, then uses the OpenStreetMap
Nominatim API to find the bounding box for each.
"""

import requests
import json
import time
import csv  # <-- ADDED
import os   # <-- ADDED

# This is a mandatory requirement from the Nominatim API.
# Failure to set a unique User-Agent may result in your IP being banned.
USER_AGENT = 'CityBoxFinder/1.0 (anton.rabanus@study.hs-duesseldorf.de)'
# ---------------------

def get_city_bbox(city_name, headers):
    """
    Fetches the bounding box for a single city from Nominatim,
    prioritizing results explicitly typed as 'city'.
    (This is the improved function from our last conversation)
    """
    # Get up to 5 results to find the best match
    url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(city_name)}&format=json&limit=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            print(f"WARNING: No results found for '{city_name}'")
            return None

        # Try to find the best match (a 'city')
        best_match = None
        for result in data:
            if (result.get('class') == 'place' and 
                result.get('type') == 'city' and 
                result.get('boundingbox')):
                best_match = result
                break # Found the best possible match

        if not best_match:
            print(f"  -> WARNING: No 'city' type match for '{city_name}'. Falling back to first result.")
            best_match = data[0]
        
        if not best_match.get('boundingbox'):
            print(f"WARNING: Selected result for '{city_name}' has no bounding box.")
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
    
    Returns a list of search strings (e.g., "Tokyo, Japan").
    """
    city_list = []
    print(f"Reading from {csv_path}...")
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Use 'population' field, default to 0
                    population_str = row.get('population', '0')
                    if not population_str:
                        continue # Skip if population is empty
                        
                    population = float(population_str)
                    
                    if population >= min_population:
                        # Use ascii name for simpler/safer searching
                        city_name = row['city_ascii'] 
                        country_name = row['country']
                        search_term = f"{city_name}, {country_name}"
                        city_list.append(search_term)
                except (ValueError, TypeError):
                    continue # Skip rows with bad population data
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
    Main function to process the list of cities and save to JSON.
    """
    if USER_AGENT == 'MyCityBoxFinder/1.0 (your-email@example.com)':
        print("="*50)
        print("ERROR: Please edit the 'USER_AGENT' variable in this script")
        print("       before running. See the comments for details.")
        print("="*50)
        return

    # --- NEW DYNAMIC LIST GENERATION ---
    MIN_POPULATION = 200000
    INPUT_CSV = "worldcities.csv" # Assumes file is in root
    
    print(f"Loading cities from '{INPUT_CSV}' with population >= {MIN_POPULATION}...")
    city_list = load_cities_from_csv(INPUT_CSV, MIN_POPULATION)
    
    if city_list is None:
        print("Exiting due to error.")
        return
        
    # De-duplicate the list (e.g., if CSV has multiple entries)
    city_list = sorted(list(set(city_list)))
    print(f"Found {len(city_list)} unique cities matching criteria.")
    # --- END NEW DYNAMIC LIST ---

    headers = {'User-Agent': USER_AGENT}
    all_city_data = []
    output_filename = "cities_gt_400k.json" # New output file name

    print(f"Starting geocoding for {len(city_list)} cities...")
    print(f"Results will be saved to '{output_filename}'")
    
    for i, city in enumerate(city_list):
        print(f"\n({i + 1}/{len(city_list)}) Processing: '{city}'")
        
        city_data = get_city_bbox(city, headers)
        
        if city_data:
            all_city_data.append(city_data)
        
        # --- IMPORTANT: RATE LIMIT ---
        # Nominatim policy requires a 1-second delay between requests.
        # Do not remove or lower this value!
        time.sleep(1)
        # -----------------------------

    # Write the final list to a JSON file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_city_data, f, indent=2, ensure_ascii=False)
        print(f"\nProcess complete. All data saved to '{output_filename}'")
    except IOError as e:
        print(f"ERROR: Could not write to file. {e}")

if __name__ == "__main__":
    main()