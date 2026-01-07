from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB_PATH = "data/pipeline.db"
IMAGE_FOLDER = "" #add path to flash stick 

def get_db_connection ():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    return conn

@app.route("/test/point")
def get_detetction():
    conn = get_db_connection()
    #query = "SEELCT cropped_file FROM mapillary_detections WHERE id=1"
    query = "SELECT id, original_image_id, captured_at, city_id FROM mapillary_detections" #LIMIT 500
    rows= conn.execute(query).fetchall()
    conn.close()

    output = []
    for row in rows:
        try:
            date_obj = datetime.strptime(row["captured_at"].split(".")[0], "%Y-%m-%d %H:%M:%S")
            x=date_obj.year
            y=date_obj.timetuple().tm_yday
            output.append({
                "id": row["id"], 
                "city_id": row["city_id"],
                "original_image_id": row["original_image_id"], 
                "x_year": x, 
                "y_day": y,                 
            })
        except:
            continue #to skip rows with broken dates 
    return jsonify(output)



@app.route("/test/total")
def get_data_count():
    conn = get_db_connection()
    #query = "SEELCT cropped_file FROM mapillary_detections WHERE id=1"
    query = "SELECT id, original_image_id, captured_at, city_id FROM mapillary_detections LIMIT 500" #LIMIT 500
    rows= conn.execute(query).fetchall()
    conn.close()

    output = []
    for row in rows:
        try:
            date_obj = datetime.strptime(row["captured_at"].split(".")[0], "%Y-%m-%d %H:%M:%S")
            x=date_obj.year
            y=date_obj.timetuple().tm_yday
            output.append({
                "id": row["id"], 
                "city_id": row["city_id"],
                "original_image_id": row["original_image_id"], 
                "x_year": x, 
                "y_day": y,                 
            })
        except:
            continue #to skip rows with broken dates 
    return jsonify( {
        "count": len(output), #count all rows but may miss "broken" data 
        #"data": output
    })


@app.route("/image")
def get_images():
    return 

if __name__ == "__main__":
    app.run(debug=True, port=5000)