import os
import json
import sqlite3
from flask import Flask, jsonify, render_template
from src.db.db_utils import get_db_connection

app = Flask(__name__,
            # Tell Flask to look for the HTML file in the root directory
            template_folder='.',
            # Tell Flask to serve static files from the root (if you add any)
            static_folder='.')

@app.route('/')
def index():
    """Serves the main HTML explorer page."""
    return render_template('bbox_exploring.html')

@app.route('/api/cities')
def get_cities_data():
    """API endpoint to get all cities from the SQLite database."""
    conn = None
    cities_list = []
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to database"}), 500
            
        # Use a cursor from the connection
        cursor = conn.cursor()
        
        # 'conn.row_factory = sqlite3.Row' was set in get_db_connection
        # This lets us access columns by name
        cursor.execute("SELECT id, name, bbox, scanned FROM cities ORDER BY name")
        results = cursor.fetchall()
        
        for row in results:
            city_data = dict(row)
            
            # The 'bbox' in the DB is a JSON string,
            # so we parse it back into a dictionary
            if city_data['bbox']:
                city_data['bbox'] = json.loads(city_data['bbox'])
            
            # Convert 0/1 to a real boolean for JavaScript
            city_data['scanned'] = bool(city_data['scanned'])
            
            cities_list.append(city_data)
            
        return jsonify(cities_list)

    except Exception as e:
        print(f"Error fetching cities: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    # Run the server, accessible from outside the Docker container
    app.run(host='0.0.0.0', port=8080, debug=True)