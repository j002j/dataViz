from flask import Flask, jsonify, send_file
from flask_cors import CORS
import csv
import os

app = Flask(__name__)
CORS(app)

def read_csv(filepath):
    rows = []
    with open(filepath, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            try:
                rows.append({
                    "id": row["id"],
                    "x": float(row["x"]),
                    "y": float(row["y"]),
                    "id_image": row["id_image"],
                    "crop_path": row["crop_path"],
                    "date": row["date"],
                    "time": row["time"],
                    "city": row["city"],
                    "state": row["state"],
                    "category_list": row["category_list"],
                    "color": row["color"]
                })
            except (ValueError, KeyError):
                continue
    return rows

@app.route("/api/items")
def get_items():
    return jsonify(read_csv("data/item_base.csv"))

@app.route("/api/outfits")
def get_outfits():
    return jsonify(read_csv("data/outfit_base.csv"))

@app.route("/image/<path:filepath>")
def get_image(filepath):
    # Resolves paths like 'data/cropped/people/...' relative to script location
    return send_file(os.path.abspath(filepath))

if __name__ == "__main__":
    app.run(debug=True, port=5000)