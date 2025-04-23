from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import requests, uuid, os
from video_processor import process_anime, process_3d

app = Flask(__name__)
CORS(app)

# Use /tmp on Render for temp storage
UPLOAD_DIR = "/tmp/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/process-video", methods=["POST"])
def process_video():
    data = request.get_json()
    video_url = data["url"]
    style = data["style"]

    filename = f"{style}_{uuid.uuid4()}.mp4"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with requests.get(video_url, stream=True) as r:
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

    if style == "anime":
        output = process_anime(filepath)
    elif style == "3d":
        output = process_3d(filepath)
    else:
        return jsonify({"error": "Invalid style"}), 400

    return jsonify({
        "result_url": f"https://video-stylizer-backend.onrender.com/videos/{os.path.basename(output)}"
    })

@app.route("/videos/<path:filename>")
def serve_file(filename):
    # Serve from /tmp/videos
    return send_from_directory(UPLOAD_DIR, filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
