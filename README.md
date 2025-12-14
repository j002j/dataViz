A project inspired by the meme starterkits but with connected to data science.
 [Link](https://www.instagram.com/p/CjIG-0EKhWb/?utm_source=ig_web_copy_link)
 [Link](/static/assets/kit_ddorf_wdr.png)

# Urban Fashion Mapping Pipeline

This repository contains a data pipeline that:

1.  Fetches street-level images from **Mapillary** for a given geographic area.
2.  Uses a **YOLOv8** computer vision model to detect people in those images.
3.  Crops the detected people and saves them as new images to the `cropped_people/` folder.
4.  Stores metadata for each detection (file path, location, capture time) in a **PostgreSQL** database.

-----

## Project Structure

  * `.env`: Holds all your secret keys and configuration.
  * `docker-compose.yml`: Manages all services (database, DB init, pipeline).
  * `Dockerfile`: Instructions for building the Python environment.
  * `requirements.txt`: Python package list.
  * `pipelines/`: Contains the main Mapillary pipeline logic.
  * `src/db/`: Contains database utilities and the initial schema setup.
  * `cropped_people/`: (Git-ignored) Where cropped images are saved.


## 🚀 How to Run the Pipeline (Docker)

This is the recommended way to run the project.

### Step 1: Configure Environment (.env)

Before you start, create a file named `.env` in the root of the project. This file holds your secret keys.

```ini
# --- Database Credentials ---
# This host 'postgres' is the service name from docker-compose.yml
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=starterkit_db
POSTGRES_USER=jenny
POSTGRES_PASSWORD=postgres

# --- Mapillary Credentials ---
MAPILLARY_ACCESS_TOKEN="YOUR_TOKEN_HERE"
```

### Step 2: Generate City List (config/cities.json)

The pipeline needs a `config/cities.json` file to know which geographic areas to scan. You can generate a large list automatically or create a small custom list manually.

#### Option A (Recommended): Generate from World Cities List

This project includes a helper script (`cities_generator.py`) that uses a free world cities database to find all cities over a certain population.

1.  **Download City Data:** Download the "Basic" (free) database from [**Simple Maps World Cities**](https://simplemaps.com/data/world-cities).
2.  **Copy CSV:** Unzip the file and place the `worldcities.csv` file in the root of your project.
3.  **(Optional) Adjust Population:** Open `cities_generator.py` and change the `MIN_POPULATION` variable if desired (default is `400000`).
4.  **Run the Script:** Run the generator script in your local Python environment. This will create the `config/cities.json` file for you.
    ```bash
    # Install Python requirements locally first
    pip install -r requirements.txt

    # Run the script
    python cities_generator.py
    ```
5.  **(Optional) Manual Fix:** The script may produce a bad bounding box for a few tricky cities (like Tokyo). If this happens, open `config/cities.json` and manually correct the `bbox` coordinates for that one entry.

#### Option B (Manual): Create a Custom List

Manually create a `config/cities.json` file. This is useful for testing a few small, specific areas.

```json
[
  {
    "name": "New York",
    "bbox": {
      "west": -74.0472,
      "south": 40.6795,
      "east": -73.9712,
      "north": 40.7920
    }
  },
  {
    "name": "Berlin",
    "bbox": {
      "west": 13.0668,
      "south": 52.3271,
      "east": 13.7813,
      "north": 52.6847
    }
  }
]
```

-----

### Step 3: Build and Run Services

With your `.env` and `config/cities.json` files ready, open your terminal in the project root and run these commands in order.

1.  **Start the database:**
    This starts the PostgreSQL server in the background.

    ```bash
    docker compose up -d postgres
    ```

2.  **(First Time) Initialize the database:**
    This runs the `init_db.py` script once to create the database tables.

    ```bash
    docker compose up --build db-init
    ```

3.  **Run the Mapillary Pipeline:**
    This is the main command. It will:

      * Build the Python Docker image.
      * Read the `config/cities.json` file.
      * **Loop through every city** and run the full detection pipeline.
      * Save results to the `mapillary_detections` and `cities` tables.

    <!-- end list -->

    ```bash
    docker compose up --build mapillary-pipeline
    ```

    You will see the pipeline's progress in your terminal as it processes each city. If you stop and restart it, it will skip cities that are already marked as scanned in the database.

-----

## 🔍 Step 4: Inspect the Database (using VS Code)

After the pipeline has run, you can connect directly to the database to see the results.

1.  Open VS Code → SQLTools (in the activity bar) → "Add New Connection".

2.  Select "PostgreSQL" as the connection type.

3.  Use the following settings (since the DB is running in Docker but exposed to your host machine, `localhost` is correct):

      * **Connection Name:** My Docker DB
      * **Host:** `localhost`
      * **Port:** `5432` (or your `POSTGRES_PORT` from `.env`)
      * **Database:** `starterkit_db`
      * **User:** `jenny`
      * **Password:** `postgres`

4.  Click "Test Connection" and then "Save Connection".

5.  You can now expand the connection in the SQLTools panel. Right-click the `mapillary_detections` table and select "Show Table Records" or run your own queries:

    ```sql
    -- See the 10 most recent detections
    SELECT * FROM mapillary_detections
    ORDER BY created_at DESC
    LIMIT 10;

    -- Check which cities are finished
    SELECT * FROM cities
    WHERE scanned = TRUE;
    ```

    # for the Poitcloud
    https://cosmos.gl/?path=/docs/welcome-to-cosmos-gl--docs
    npm install @cosmos.gl/graph

    to test locally, run:    
      npm install -D vite
      npm run dev
    open in browser: http://localhost:5173/

  # for UI / sveltKit:
  install VS-code plug in: "Svelte for VS Code"

  add svelt set up 

install tailwind following: https://tailwindcss.com/docs/installation/framework-guides/sveltekit
  npm install tailwindcss @tailwindcss/vite

  npm install svelte typescript vite @sveltejs/kit@latest --save-dev


    
