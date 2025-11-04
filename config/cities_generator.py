#!/usr/bin/env python3

"""
This script fetches bounding box coordinates for a list of cities
using the free OpenStreetMap Nominatim API.

!!! IMPORTANT !!!
Before running, you MUST change the 'USER_AGENT' variable below
to something that identifies your script or application, as required
by the Nominatim usage policy.
For example: 'MyAwesomeApp/1.0 (your-email@example.com)'
"""

import requests
import json
import time

# --- CONFIGURATION ---
# !!! CHANGE THIS VALUE !!!
# This is a mandatory requirement from the Nominatim API.
# Failure to set a unique User-Agent may result in your IP being banned.
USER_AGENT = 'CityBoxFinder/1.0 (anton.rabanus@study.hs-duesseldorf.de)'
# ---------------------

def get_city_bbox(city_name, headers):
    """
    Fetches the bounding box for a single city from Nominatim.
    """
    # Construct the API URL
    url = f"https://nominatim.openstreetmap.org/search?q={requests.utils.quote(city_name)}&format=json&limit=1"
    
    try:
        # Make the request with the required User-Agent
        response = requests.get(url, headers=headers, timeout=10)
        
        # Check for successful response
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got any results and if the result has a boundingbox
            if data and data[0].get('boundingbox'):
                bbox_osm = data[0]['boundingbox'] # Nominatim format: [south, north, west, east]
                
                # Format to match the user's requested JSON structure
                formatted_bbox = {
                    "west": float(bbox_osm[2]),
                    "south": float(bbox_osm[0]),
                    "east": float(bbox_osm[3]),
                    "north": float(bbox_osm[1])
                }
                
                # Use the full name from the API for clarity
                city_data = {
                    "name": data[0]['display_name'],
                    "search_term": city_name,
                    "bbox": formatted_bbox
                }
                
                print(f"SUCCESS: Found '{data[0]['display_name']}'")
                return city_data
            else:
                print(f"WARNING: No results found for '{city_name}'")
                return None
        else:
            print(f"ERROR: HTTP {response.status_code} for '{city_name}'")
            return None
            
    except requests.RequestException as e:
        print(f"EXCEPTION: {e} for '{city_name}'")
        return None

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

    # --- INPUT ---
    # Paste your list of 300 cities here.
    # I've added a small sample from your "Africa" list to get you started.
    city_list = [
        # Africa
        "Lagos, Nigeria",
        "Cairo, Egypt",
        "Kinshasa, DR Congo",
        "Johannesburg, South Africa",
        "Luanda, Angola",
        "Khartoum, Sudan",
        "Abidjan, Côte d'Ivoire",
        "Nairobi, Kenya",
        "Accra, Ghana",
        "Dar es Salaam, Tanzania",
        "Alexandria, Egypt",
        "Bamako, Mali",
        "Kano, Nigeria",
        "Cape Town, South Africa",
        "Addis Ababa, Ethiopia",
        "Giza, Egypt",
        "Casablanca, Morocco",
        "Algiers, Algeria",
        "Kampala, Uganda",
        "Dakar, Senegal",
        "Ekurhuleni, South Africa",
        "Yaoundé, Cameroon",
        "Durban, South Africa",
        "Douala, Cameroon",
        "Ouagadougou, Burkina Faso",
        "Ibadan, Nigeria",
        "Antananarivo, Madagascar",
        "Abuja, Nigeria",
        "Lusaka, Zambia",
        "Conakry, Guinea",
        "Kumasi, Ghana",
        "Lubumbashi, DR Congo",
        "Omdurman, Sudan",
        "Pretoria, South Africa",
        "Tunis, Tunisia",
        "Harare, Zimbabwe",
        "Lomé, Togo",
        "Maputo, Mozambique",
        "Mbuji-Mayi, DR Congo",
        "Brazzaville, Republic of the Congo",
        "Port Harcourt, Nigeria",
        "Mogadishu, Somalia",
        "Cotonou, Benin",
        "Rabat, Morocco",
        "Kaduna, Nigeria",
        "Kigali, Rwanda",
        "N'Djamena, Chad",
        "Monrovia, Liberia",
        "Tripoli, Libya",
        "Matola, Mozambique",
        # Asia
        "Tokyo, Japan",
        "Delhi, India",
        "Shanghai, China",
        "Mumbai, India",
        "Beijing, China",
        "Dhaka, Bangladesh",
        "Osaka, Japan",
        "Karachi, Pakistan",
        "Chongqing, China",
        "Kolkata, India",
        "Manila, Philippines",
        "Cairo, Egypt (transcontinental)",
        "Guangzhou, China",
        "Shenzhen, China",
        "Jakarta, Indonesia",
        "Seoul, South Korea",
        "Chengdu, China",
        "Tianjin, China",
        "Bangalore, India",
        "Nanjing, China",
        "Lahore, Pakistan",
        "Ho Chi Minh City, Vietnam",
        "Chennai, India",
        "Wuhan, China",
        "Bangkok, Thailand",
        "Hyderabad, India",
        "Hong Kong, China",
        "Tehran, Iran",
        "Xi'an, China",
        "Ahmedabad, India",
        "Kuala Lumpur, Malaysia",
        "Singapore, Singapore",
        "Suzhou, China",
        "Hangzhou, China",
        "Riyadh, Saudi Arabia",
        "Harbin, China",
        "Baghdad, Iraq",
        "Pune, India",
        "Qingdao, China",
        "Dalian, China",
        "Dongguan, China",
        "Surat, India",
        "Yangon, Myanmar",
        "Shenyang, China",
        "Foshan, China",
        "Zhengzhou, China",
        "Shantou, China",
        "Changsha, China",
        "Urumqi, China",
        "Kunming, China",
        # Europe
        "Istanbul, Turkey (transcontinental)",
        "Moscow, Russia",
        "London, United Kingdom",
        "Saint Petersburg, Russia",
        "Berlin, Germany",
        "Madrid, Spain",
        "Kyiv, Ukraine",
        "Rome, Italy",
        "Paris, France",
        "Bucharest, Romania",
        "Minsk, Belarus",
        "Vienna, Austria",
        "Hamburg, Germany",
        "Warsaw, Poland",
        "Budapest, Hungary",
        "Barcelona, Spain",
        "Munich, Germany",
        "Kharkiv, Ukraine",
        "Milan, Italy",
        "Belgrade, Serbia",
        "Prague, Czechia",
        "Kazan, Russia",
        "Sofia, Bulgaria",
        "Nizhny Novgorod, Russia",
        "Yekaterinburg, Russia",
        "Samara, Russia",
        "Odesa, Ukraine",
        "Birmingham, United Kingdom",
        "Ufa, Russia",
        "Rostov-on-Don, Russia",
        "Cologne, Germany",
        "Voronezh, Russia",
        "Perm, Russia",
        "Volgograd, Russia",
        "Dnipro, Ukraine",
        "Naples, Italy",
        "Krasnoyarsk, Russia",
        "Turin, Italy",
        "Saratov, Russia",
        "Marseille, France",
        "Zagreb, Croatia",
        "Valencia, Spain",
        "Łódź, Poland",
        "Kraków, Poland",
        "Amsterdam, Netherlands",
        "Athens, Greece",
        "Seville, Spain",
        "Frankfurt, Germany",
        "Krasnodar, Russia",
        "Zaragoza, Spain",
        # North America
        "Mexico City, Mexico",
        "New York City, USA",
        "Los Angeles, USA",
        "Toronto, Canada",
        "Chicago, USA",
        "Houston, USA",
        "Havana, Cuba",
        "Montreal, Canada",
        "Ecatepec de Morelos, Mexico",
        "Phoenix, USA",
        "Philadelphia, USA",
        "San Antonio, USA",
        "Tijuana, Mexico",
        "San Diego, USA",
        "León, Mexico",
        "Dallas, USA",
        "Puebla, Mexico",
        "Juárez, Mexico",
        "Guatemala City, Guatemala",
        "Guadalajara, Mexico",
        "Zapopan, Mexico",
        "Austin, USA",
        "Calgary, Canada",
        "San Jose, USA",
        "Monterrey, Mexico",
        "Jacksonville, USA",
        "Fort Worth, USA",
        "Columbus, USA",
        "Charlotte, USA",
        "Nezahualcóyotl, Mexico",
        "Indianapolis, USA",
        "Santo Domingo, Dominican Republic",
        "San Francisco, USA",
        "Seattle, USA",
        "Denver, USA",
        "Washington, D.C., USA",
        "Boston, USA",
        "El Paso, USA",
        "Nashville, USA",
        "Detroit, USA",
        "Edmonton, Canada",
        "Oklahoma City, USA",
        "Ottawa, Canada",
        "Portland, USA",
        "Las Vegas, USA",
        "Memphis, USA",
        "Louisville, USA",
        "Baltimore, USA",
        "Milwaukee, USA",
        "Albuquerque, USA",
        # South America
        "São Paulo, Brazil",
        "Lima, Peru",
        "Bogotá, Colombia",
        "Rio de Janeiro, Brazil",
        "Santiago, Chile",
        "Buenos Aires, Argentina",
        "Caracas, Venezuela",
        "Brasília, Brazil",
        "Salvador, Brazil",
        "Fortaleza, Brazil",
        "Belo Horizonte, Brazil",
        "Medellín, Colombia",
        "Manaus, Brazil",
        "Curitiba, Brazil",
        "Guayaquil, Ecuador",
        "Recife, Brazil",
        "Cali, Colombia",
        "Santa Cruz de la Sierra, Bolivia",
        "Porto Alegre, Brazil",
        "Goiânia, Brazil",
        "Belém, Brazil",
        "Maracaibo, Venezuela",
        "Quito, Ecuador",
        "Guarulhos, Brazil",
        "Campinas, Brazil",
        "Barranquilla, Colombia",
        "São Luís, Brazil",
        "São Gonçalo, Brazil",
        "Maceió, Brazil",
        "Callao, Peru",
        "Duque de Caxias, Brazil",
        "Córdoba, Argentina",
        "Nova Iguaçu, Brazil",
        "Teresina, Brazil",
        "Campo Grande, Brazil",
        "Rosario, Argentina",
        "ão Bernardo do Campo, Brazil",
        "Natal, Brazil",
        "João Pessoa, Brazil",
        "Santo André, Brazil",
        "Arequipa, Peru",
        "Barquisimeto, Venezuela",
        "Cartagena, Colombia",
        "Trujillo, Peru",
        "Montevideo, Uruguay",
        "Osasco, Brazil",
        "Valencia, Venezuela",
        "La Paz, Bolivia",
        "El Alto, Bolivia",
        "Chiclayo, Peru",
        # Oceania (Australasia)
        "Sydney, Australia",
        "Melbourne, Australia",
        "Brisbane, Australia",
        "Perth, Australia",
        "Auckland, New Zealand",
        "Adelaide, Australia",
        "Gold Coast, Australia",
        "Newcastle, Australia",
        "Canberra, Australia",
        "Wellington, New Zealand",
        "Christchurch, New Zealand",
        "Sunshine Coast, Australia",
        "Wollongong, Australia",
        "Geelong, Australia",
        "Port Moresby, Papua New Guinea",
        "Hobart, Australia",
        "Townsville, Australia",
        "Hamilton, New Zealand",
        "Cairns, Australia",
        "Tauranga, New Zealand",
        "Darwin, Australia",
        "Toowoomba, Australia",
        "Dunedin, New Zealand",
        "Ballarat, Australia",
        "Bendigo, Australia",
        "Lae, Papua New Guinea",
        "Palmerston North, New Zealand",
        "Albury-Wodonga, Australia",
        "Launceston, Australia",
        "Mackay, Australia",
        "Rockhampton, Australia",
        "Bunbury, Australia",
        "Coffs Harbour, Australia",
        "Bundaberg, Australia",
        "Nouméa, New Caledonia",
        "Wagga Wagga, Australia",
        "Hervey Bay, Australia",
        "Rotorua, New Zealand",
        "Whangārei, New Zealand",
        "New Plymouth, New Zealand",
        "Invercargill, New Zealand",
        "Nelson, New Zealand",
        "Suva, Fiji",
        "Hastings, New Zealand",
        "Shepparton, Australia",
        "Mildura, Australia",
        "Port Macquarie, Australia",
        "Gladstone, Australia",
        "Tamworth, Australia",
        "Traralgon, Australia"

    ]
    

    headers = {'User-Agent': USER_AGENT}
    all_city_data = []
    output_filename = "cities_.json"

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
