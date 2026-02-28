# Urban Fashion Mapping Pipeline

Project inspired by meme starterkits, applying data science to urban fashion trends by analyzing street-level imagery and generating 2D semantic embedding spaces.

# Structure
The project follows the standard SvelteKit structure with a focus on modular visualization components: 
* src/routes/: Contains the application pages (about, credits, globe)
* +page.svelte: The interactive landing page 
* globe/+page.svelte: The main fashion data visualization (point cloud)
* src/lib/: Reusable code:  visualization/: Contains StraterKitLayout.svelte and EmbeddingView.svelte for displaying the point cloud
* static/: Static assets (images, icons, and fashion data samples).

## Pipeline Implementation
The pipeline to get the data to display is described in this [data preparation backend](https://github.com/a-rabanus/dataviz_backend).

---

## Frontend & UI

A Svelte 5 application utilizing Cosmos.gl for high-performance WebGL point cloud rendering. 

### Tech Stack

| Library | Version | Note |
| :--- | :--- | :--- |
| `svelte` | 5.46.0 | Uses the new Snippet/Children pattern in layouts. |
| Tailwind CSS + custom app.css | | Styling | 
| Embedding Atlas (`embedding-atlas/svelte`) | | Visualizations: WebGPU-accelerated and provides built-in tooltip and selection callbacks | 
| `vite` | 6.4.1 | Handles the import analysis for the visualization. |
| Python (`generate_feature_matrica.py`) | | pre-processing: Offline script that generates embeddings and produces the coordinate CSVs | 
| .csv files | | processed datapoints for vizualization | 
| app.py | | Flask server, exposes `/api/items` and `/api/outfits` | 
| EmbeddingView.svelte | | holds the logic for the point cloud | 
| StarterKitLayout.svelte | | holds teh layout for the application and embedds teh logic/EmbeddingView.svelte  | 


### Workflow
```
generate_feature_matrica.py

        ↓ (produces CSVs with x/y coords)

app.py  →  /api/items  /api/outfits

        ↓ (JSON)

SvelteKit frontend

        ↓ (converts to typed arrays)

EmbeddingView (Embedding Atlas)


The application works with CSV files that were genererated from generate_feature_matrica.py. To substitute them for different files change the path in the respectful routed in app.py: @app.route("/api/outfits") or @app.route("/api/items")


### Run the development server:
To start the developemt server to test the pointclouds locally. 

If not yet installed: 
```ini
npm install -D vite 'npm run dev
```
Install the install the Embedding View library:
```ini
npm install embedding-atlas
```


We are using flask and flask-cors for connecting backend and frontend to display the Data as point cloud.
To install, run: 

```ini
pip install flask flask-cors
```

Then run the scirpt to start the backend:

```ini
python app.py
```

To start the vite server for teh forntend run:
```ini
npm run dev
```
Open http://localhost:5173/ in the bowser and the website should appear.


---

## Performance and Monitoring

The following tools are used to identify resource-heavy elements and optimize the visualization:

* [rStats](https://spite.github.io/rstats/)
* [stats.js](https://github.com/mrdoob/stats.js)

---

## Environment Configuration

Create a `.env` file in the root directory:

```ini
MAPILLARY_ACCESS_TOKEN="YOUR_TOKEN_HERE"

```

## Database Schema

The system uses `src/db/db_utils.py` for all database interactions. The schema includes:

* `cities`: Geographic boundaries and scan status.
* `images_detected`: Raw Mapillary image metadata.
* `person_detected`: Links cropped images to original sources.
* `clothing_item_detected`: Extracted features and attributes.

---

## References

* [DeepFashion2 Dataset](https://github.com/switchablenorms/DeepFashion2)
* [Figma Design Prototype](https://www.figma.com/design/xWFdUtSlsngfeJKi33LZEx/Portfolio?node-id=0-1&t=JhhHZ7DehM6H0LSy-1)