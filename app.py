from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests, uuid, os
from video_processor import process_anime, process_3d

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = 'uploads'
OUTPUT_DIR = 'videos'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/process-video", methods=["POST"])
def process_video():
    data = request.get_json()
    video_url = data["url"]
    style = data["style"]

    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with requests.get(video_url, stream=True) as r:
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

    if style == "anime":
        output_filename = process_anime(filepath)
    elif style == "3d":
        output_filename = process_3d(filepath)
    else:
        return jsonify({"error": "Invalid style"}), 400

    return jsonify({"result_url": f"https://video-stylizer-backend.onrender.com/videos/{output_filename}"})

@app.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
