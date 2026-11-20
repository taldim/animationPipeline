"""Move a finished download into an action folder, then cut frames and build the review.

Usage:  python pipeline/grab.py <char> <action> video <id>
        python pipeline/grab.py <char> <action> image <id>
The file name and where to read <id> come from the provider (providers/<name>.json:
image_download / video_download, image_id / video_id).
video: moves it to <action>/video.mp4, runs video_to_frames + review --all, and for
       actions that own a pose (no "pose_from") writes pose.jpg from frame 1 if missing.
image: moves it to <action>/pose.jpg. For `clean` it also writes characters/<char>/reference.png.
Waits for the EXACT file: the download lags the click, and "newest file" grabs the last take.
Downloads folder: config.json "downloads".
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from paths import GENERATED, PIPELINE, args_or_usage, load_config, load_provider

WAIT_SECONDS = 90


def wait_for(path: Path) -> Path:
    deadline = time.time() + WAIT_SECONDS
    while time.time() < deadline:
        if path.exists():
            time.sleep(1)  # let the browser finish closing the file
            return path
        time.sleep(1)
    sys.exit(f"Timed out waiting for {path}")


def run(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(PIPELINE / script), *args], check=True)


def owns_pose(action: str) -> bool:
    actions = json.loads((PIPELINE / "actions.json").read_text(encoding="utf-8"))
    return "pose_from" not in actions.get(action, {})


def main() -> None:
    character, action, kind, result_id = args_or_usage(4, __doc__)[:4]
    if kind not in ("image", "video"):
        sys.exit(__doc__)
    config = load_config()
    provider = load_provider(config)
    downloads = Path(config["downloads"])
    folder = GENERATED / character / action
    folder.mkdir(parents=True, exist_ok=True)
    if kind == "image":
        src = wait_for(downloads / provider["image_download"].format(id=result_id))
        shutil.move(src, folder / "pose.jpg")
        if action == "clean":
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(folder / "pose.jpg"),
                            str(GENERATED / character / "reference.png")], check=True)
        print(f"ok {folder / 'pose.jpg'}")
        return
    src = wait_for(downloads / provider["video_download"].format(id=result_id))
    shutil.move(src, folder / "video.mp4")
    run("video_to_frames.py", character, action)
    if owns_pose(action) and not (folder / "pose.jpg").exists():
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i",
                        str(folder / "frames" / "frame_01.png"), "-q:v", "2",
                        str(folder / "pose.jpg")], check=True)
    run("review.py", character, action, "--all")
    print(f"ok {folder}  (sheet: {folder / 'review' / 'sheet.png'})")


if __name__ == "__main__":
    main()
