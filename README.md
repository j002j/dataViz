A project inspired by the meme starterkits but with connected to data science.
 [Link](https://www.instagram.com/p/CjIG-0EKhWb/?utm_source=ig_web_copy_link)

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

-----

## Prerequisites

  * Docker (installed and running)
  * Python 3.x
  * VS Code (Recommended)
  * **VS Code Extensions:**
      * SQLTools
      * SQLTools PostgreSQL Driver

-----

## How to Run the Pipeline (Docker)

This is the recommended way to run the project.

### 1\. Configuration

Before you start, you **must** create a configuration file.

1.  Create a new file named `.env` in the root of the project.
2.  Copy the following content into your new `.env` file.
3.  **Add your Mapillary Access Token** where it says `"YOUR_TOKEN_HERE"`.
4.  (Optional) Change the `TARGET_BBOX` coordinates to a new area.

<!-- end list -->

```ini
# --- Database Credentials ---
# This host 'postgres' is the service name from docker-compose.yml
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=starterkit_db
POSTGRES_USER=jenny
POSTGRES_PASSWORD=postgres

# --- Mapillary Credentials ---
MAPILLARY_ACCESS_TOKEN="YOUR_TOKEN_HERE"

# --- Pipeline Config (Example: San Francisco) ---
TARGET_BBOX_WEST=-122.4206
TARGET_BBOX_SOUTH=37.7722
TARGET_BBOX_EAST=-122.4106
TARGET_BBOX_NORTH=37.7782
```

### 2\. Build and Run Services

Open your terminal in the project root and run these commands in order.

1.  **Start the database:**
    This starts the PostgreSQL server in the background.

    ```bash
    docker compose up -d postgres
    ```

2.  **(First Time) Initialize the database:**
    This runs the `init_db.py` script once to create the original tables from your colleague's `db/starterkit.session.sql` file.

    ```bash
    docker compose up --build db-init
    ```

3.  **Run the Mapillary Pipeline:**
    This is the main command. It will:

      * Build the Python Docker image (installing `requirements.txt`).
      * Connect to the database and create the `mapillary_detections` table (if it doesn't exist).
      * Start fetching and processing images from Mapillary.
      * Save cropped images to the `cropped_people/` folder.
      * Save all metadata to the `mapillary_detections` table.

    <!-- end list -->

    ```bash
    docker compose up --build mapillary-pipeline
    ```

    You will see the pipeline's progress in your terminal.

-----

## 🔍 Inspect the Database (using VS Code)

After the pipeline has run, you can connect directly to the database to see the results.

1.  Open VS Code → SQLTools (in the activity bar) → "Add New Connection".

2.  Select "PostgreSQL" as the connection type.

3.  Use the following settings (since the DB is running in Docker but exposed to your host machine, `localhost` is correct here):

      * **Connection Name:** My Docker DB (or any name)
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
    ```