import os, uuid, cv2, json
import ffmpeg
from datetime import datetime

OUTPUT_DIR = "videos"
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "upload_log.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

def log_upload(style, filename):
    entry = {
        "id": str(uuid.uuid4()),
        "style": style,
        "filename": filename,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([entry], f, indent=2)
    else:
        with open(LOG_FILE, "r+") as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)

def process_anime(input_path):
    output_path = os.path.join(OUTPUT_DIR, f"anime_{uuid.uuid4()}.mp4")
    temp_dir = f"temp_{uuid.uuid4()}"
    os.makedirs(temp_dir)

    vidcap = cv2.VideoCapture(input_path)
    success, image = vidcap.read()
    count = 0

    while success:
        frame_path = f"{temp_dir}/frame_{count:05}.png"
        styled = apply_anime_filter(image)
        cv2.imwrite(frame_path, styled)
        success, image = vidcap.read()
        count += 1

    (
        ffmpeg
        .input(f'{temp_dir}/frame_%05d.png', framerate=25)
        .output(output_path)
        .run()
    )

    filename = os.path.basename(output_path)
    log_upload("anime", filename)
    return filename

def process_3d(input_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    output_path = os.path.join(OUTPUT_DIR, f"3d_{uuid.uuid4()}.mp4")
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 25, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        styled = cv2.convertScaleAbs(cv2.GaussianBlur(frame, (9, 9), 0), alpha=1.2, beta=30)
        out.write(styled)

    cap.release()
    out.release()

    filename = os.path.basename(output_path)
    log_upload("3d", filename)
    return filename

def apply_anime_filter(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    filtered = cv2.bilateralFilter(frame, 9, 75, 75)
    return cv2.addWeighted(filtered, 0.8, edges, 0.2, 0)
