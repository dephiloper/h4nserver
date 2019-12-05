#!/usr/bin/python3
from flask import Flask, abort, jsonify, send_from_directory
import os
import uuid
import time
from multiprocessing import Manager

# bounds germany
MAP_BOUNDS = {"north": 55.09916098, "west": 5.86631529, "south": 47.27011137, "east": 15.04193189}
MIN_ZOOM = 0
MAX_ZOOM = 16
STYLE = "https://h4nsolo.f4.htw-berlin.de/styles/klokantech-basic/style.json"
DOWNLOAD_DIR = "offline-maps"

app = Flask(__name__, static_folder="offline-maps")
manager = Manager()
generated_files = manager.dict()


@app.route("/offline/<float:north>/<float:west>/<float:south>/<float:east>", defaults={"min_zoom": 0, "max_zoom": 14})
@app.route("/offline/<float:north>/<float:west>/<float:south>/<float:east>/<int:min_zoom>/<int:max_zoom>")
def request_offline_data(north: float, west: float, south: float, east: float, min_zoom: int, max_zoom: int):
    if not within_map_bounds(north, west, south, east):
        abort(400, f"The requested area is not within the map bounds: {MAP_BOUNDS}")
    if not zoom_valid(min_zoom, max_zoom):
        abort(400, f"The requested zoom is not valid. The zoom bounds should be within {MIN_ZOOM}-{MAX_ZOOM}.")
    file_name = f"{north}_{west}_{south}_{east}_{min_zoom}_{max_zoom}.db"

    if not os.path.isfile(f"{DOWNLOAD_DIR}/{file_name}"):
        os.system(f"./mbgl-offline --style {STYLE} --north={north} --west={west} --south={south} --east={east}"
                  f" --minZoom=0 --maxZoom=14 --output {DOWNLOAD_DIR}/{file_name}")

    file_id = uuid.uuid4().hex
    generated_files[file_id] = {"file_name": file_name, "timestamp": time.time()}
    return jsonify(id=file_id, file_size=get_file_size(f"{DOWNLOAD_DIR}/{file_name}"),
                   north=north, west=west, south=south, east=east, min_zoom=min_zoom, max_zoom=max_zoom)


@app.route("/download/<file_id>")
def get_offline_data(file_id: str):
    if file_id not in generated_files:
        abort(404, f"The requested with the id {file_id} can't be found.")

    file_name = generated_files[file_id]['file_name']
    return send_from_directory(f"{DOWNLOAD_DIR}", filename=file_name, as_attachment=True,
                               attachment_filename=f"{file_id}.db")


def within_map_bounds(north: float, west: float, south: float, east: float):
    return north < MAP_BOUNDS["north"] and \
           west > MAP_BOUNDS["west"] and \
           south > MAP_BOUNDS["south"] and \
           east < MAP_BOUNDS["east"]


def zoom_valid(min_zoom: int, max_zoom: int):
    return min_zoom >= MIN_ZOOM and max_zoom <= MAX_ZOOM


def get_file_size(path: str):
    size = os.path.getsize(path) / 1e6
    return f"{size} mb"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
