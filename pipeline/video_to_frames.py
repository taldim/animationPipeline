"""Cut a generated video into numbered PNG frames (needs ffmpeg on PATH).

Usage:  python pipeline/video_to_frames.py <character> <action> [fps]
Reads   characters/<character>/<action>/video.mp4
Writes  characters/<character>/<action>/frames/frame_01.png ...
fps defaults to config.json's fps (12 if unset). Then review.py (look), pick.py (frames to keep -> final/),
and export.py (transparent PNGs + sprite sheet).
"""
import shutil
import subprocess
import sys

from paths import CONFIG, GENERATED, load_config

DEFAULT_FPS = 12


def main() -> None:
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    character, action = sys.argv[1], sys.argv[2]
    default = load_config().get("fps", DEFAULT_FPS) if CONFIG.exists() else DEFAULT_FPS
    fps = int(sys.argv[3]) if len(sys.argv) == 4 else default
    folder = GENERATED / character / action
    video = folder / "video.mp4"
    if not video.exists():
        sys.exit(f"No video at {video}")
    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found (winget install Gyan.FFmpeg)")
    frames = folder / "frames"
    # Old frames, frame edits and picks belong to the previous cut; drop them.
    for stale in (frames, folder / "frames_orig", folder / "final"):
        if stale.exists():
            shutil.rmtree(stale)
    frames.mkdir()
    subprocess.run(
        ["ffmpeg", "-loglevel", "error", "-i", str(video), "-vf", f"fps={fps}",
         str(frames / "frame_%02d.png")],
        check=True,
    )
    count = len(list(frames.glob("frame_*.png")))
    print(f"{count} frames -> {frames}")


if __name__ == "__main__":
    main()
