"""Keep every take of an action, so a regenerate can be undone.

Usage:  python pipeline/versions.py archive <char> <action> [note...]
        python pipeline/versions.py list <char> <action>
        python pipeline/versions.py restore <char> <action> <vNN>
archive: moves video, frames, edits, selection, final and review into
  history/vNN/ (pose.jpg and prompts.txt are copied, so they stay for the next take).
  Run it BEFORE regenerating. restore archives the current take first, then brings vNN back.
"""
import shutil
import sys

from paths import action_dir

MOVED = ["video.mp4", "frames", "frames_orig", "selection.json", "final", "review"]
COPIED = ["pose.jpg", "prompts.txt"]


def history(folder):
    path = folder / "history"
    path.mkdir(exist_ok=True)
    return path


def archive(folder, note: str) -> str:
    if not (folder / "video.mp4").exists():
        return ""
    taken = sorted(history(folder).glob("v*"))
    version = f"v{len(taken) + 1:02d}"
    dest = history(folder) / version
    dest.mkdir()
    for name in MOVED:
        if (folder / name).exists():
            shutil.move(str(folder / name), str(dest / name))
    for name in COPIED:
        if (folder / name).exists():
            shutil.copyfile(folder / name, dest / name)
    (dest / "note.txt").write_text(note or "-", encoding="utf-8")
    return version


def restore(folder, version: str) -> None:
    src = history(folder) / version
    if not src.exists():
        sys.exit(f"No {src}")
    saved = archive(folder, f"auto-archived before restoring {version}")
    for name in MOVED + COPIED:
        if (src / name).is_dir():
            shutil.copytree(src / name, folder / name)
        elif (src / name).exists():
            shutil.copyfile(src / name, folder / name)
    print(f"restored {version}" + (f" (current take saved as {saved})" if saved else ""))


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    op, character, action = sys.argv[1:4]
    folder = action_dir(character, action)
    if op == "archive":
        version = archive(folder, " ".join(sys.argv[4:]))
        print(f"archived as {version}" if version else "nothing to archive")
    elif op == "list":
        for path in sorted(history(folder).glob("v*")):
            print(path.name, "-", (path / "note.txt").read_text(encoding="utf-8").strip())
    elif op == "restore" and len(sys.argv) > 4:
        restore(folder, sys.argv[4])
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
