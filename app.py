from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

import requests, uuid, os
from video_processor import process_anime, process_3d

app = Flask(__name__)
UPLOAD_DIR = 'videos'
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        output = process_anime(filepath)
    elif style == "3d":
        output = process_3d(filepath)
    else:
        return jsonify({"error": "Invalid style"}), 400

    return jsonify({"result_url": f"https://inspired555.pythonanywhere.com/{output}"})

@app.route("/videos/<path:filename>")
def serve_file(filename):
    return app.send_static_file(f"videos/{filename}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
