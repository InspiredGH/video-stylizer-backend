import os, uuid, cv2
import ffmpeg

VIDEOS_DIR = "videos"
os.makedirs(VIDEOS_DIR, exist_ok=True)

def process_anime(input_path):
    output_path = os.path.join(VIDEOS_DIR, f"anime_{uuid.uuid4()}.mp4")
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

    # Cleanup
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, f))
    os.rmdir(temp_dir)

    return os.path.basename(output_path)

def process_3d(input_path):
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(3))
    height = int(cap.get(4))
    out_path = os.path.join(VIDEOS_DIR, f"3d_{uuid.uuid4()}.mp4")

    out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), 25, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        styled = cv2.convertScaleAbs(cv2.GaussianBlur(frame, (9, 9), 0), alpha=1.2, beta=30)
        out.write(styled)

    cap.release()
    out.release()
    return os.path.basename(out_path)

def apply_anime_filter(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    filtered = cv2.bilateralFilter(frame, 9, 75, 75)
    return cv2.addWeighted(filtered, 0.8, edges, 0.2, 0)
