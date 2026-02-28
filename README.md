# Urban Fashion Mapping Pipeline

Project inspired by meme starterkits, applying data science to urban fashion trends by analyzing street-level imagery and generating 2D semantic embedding spaces.

## Run the development server:
**Setup Manual**

### **1. Prerequisites**

* Python 3.10.19
* Node.js v18.19.1

### **2. Data Configuration**

1. Download dataset: [Sharepoint](https://fhd-my.sharepoint.com/:f:/g/personal/anton_rabanus_study_hs-duesseldorf_de/IgAcs-Or3-sNQLxlxcrHztTgARBn437VgafuPHelGraxlbY?e=cNZKEm)
2. Extract archive.
3. Move extracted contents into the `data/` directory at the project root. Create directory if it does not exist.

#### Folder Structure

The application expects the following directory layout to correctly serve datasets and images via the Flask backend:

```text
project_root/
├── .venv/               # Python virtual environment
├── data/                # Primary data directory (must be created)
│   ├── item_base.csv    # Required for /api/items
│   ├── item_loc.csv    # Required for /api/items
│   ├── item_time_loc.csv    # Required for /api/items
│   ├── item_time.csv    # Required for /api/items
│   ├── outfit_base.csv  # Required for /api/outfits
│   ├── outfit_loc.csv  # Required for /api/outfits
│   ├── outfit_time_loc.csv  # Required for /api/outfits
│   ├── outfit_time.csv  # Required for /api/outfits
│   └── cropped_people/  # Directory containing image assets
│       └── [image_files] # Served via /image/<path>
├── src/                 # SvelteKit frontend source
├── app.py               # Flask backend server
├── requirements.txt     # Backend dependencies
├── package.json         # Frontend dependencies
└── .env                 # API tokens

```

#### Path Requirements

* **CSVs**: The backend looks specifically for `data/item_base.csv` and `data/outfit_base.csv`.
* **Images**: All cropped pedestrian images must be placed in `data/cropped_people/` to be accessible at the `/image/` endpoint.

### **3. Backend Setup**
Create and activate virtual environment:

* Linux/macOS: `python -m venv .venv && source .venv/bin/activate`
* Windows: `python -m venv .venv && .venv\Scripts\activate`

Install dependencies:
`pip install -r requirements.txt`


### **4. Frontend Setup**
Install Node dependencies:
`npm install`
*(Note: Covers required packages like vite and embedding-atlas)*

### **5. Execution**
Start backend server:
`python app.py`

Start frontend server (in a separate terminal):
`npm run dev`

### **6. Access**
Open `http://localhost:5173/` in a web browser.


# Workflow
```
generate_feature_matrica.py

        ↓ (produces CSVs with x/y coords)

app.py  →  /api/items  /api/outfits

        ↓ (JSON)

SvelteKit frontend

        ↓ (converts to typed arrays)

EmbeddingView (Embedding Atlas)
```

The application works with CSV files that were genererated from generate_feature_matrica.py. To substitute them for different files change the path in the respectful routed in app.py: @app.route("/api/outfits") or @app.route("/api/items")

## Pipeline Implementation
The pipeline to get the data to display is described in this [data preparation backend](https://github.com/a-rabanus/dataviz_backend).


## Structure
The project follows the standard SvelteKit structure with a focus on modular visualization components: 
* src/routes/: Contains the application pages (about, credits, globe)
* +page.svelte: The interactive landing page 
* globe/+page.svelte: The main fashion data visualization (point cloud)
* src/lib/: Reusable code:  visualization/: Contains StraterKitLayout.svelte and EmbeddingView.svelte for displaying the point cloud
* static/: Static assets (images, icons, and fashion data samples).

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

---

## Performance and Monitoring

The following tools are used to identify resource-heavy elements and optimize the visualization:

* [rStats](https://spite.github.io/rstats/)
* [stats.js](https://github.com/mrdoob/stats.js)

---

## References

* [DeepFashion2 Dataset](https://github.com/switchablenorms/DeepFashion2)
* [Figma Design Prototype](https://www.figma.com/design/xWFdUtSlsngfeJKi33LZEx/Portfolio?node-id=0-1&t=JhhHZ7DehM6H0LSy-1)

