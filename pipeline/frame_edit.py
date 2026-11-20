"""Small fixes to single raw frames. The first edit of a frame backs it up to
frames_orig/, so `undo` always returns to what the video gave.

Usage:  python pipeline/frame_edit.py <char> <action> <op> <frame> [args]
  replace <n> <src>            frame n becomes a copy of frame src (glitched frame)
  blend <n> <a> <b>            frame n becomes a 50/50 mix of frames a and b
  erase <n> <x0> <y0> <x1> <y1> paint the box with the background colour (stray pixels)
  put <n> <image>              frame n becomes <image>, resized to fit (an AI-edited frame)
  undo <n>                     restore the original frame
Coordinates are in raw frame pixels (the video's size, e.g. 1280x720).
"""
import shutil
import sys

from PIL import Image

from paths import action_dir, args_or_usage, frame_path

BACKGROUND_SAMPLE = (2, 2)  # a corner pixel is always background


def backup(folder, path) -> None:
    orig = folder / "frames_orig"
    orig.mkdir(exist_ok=True)
    if not (orig / path.name).exists():
        shutil.copyfile(path, orig / path.name)


def main() -> None:
    args = args_or_usage(4, __doc__)
    character, action, op, n = args[0], args[1], args[2], int(args[3])
    rest = args[4:]
    folder = action_dir(character, action)
    target = frame_path(folder, n)
    if op == "undo":
        orig = folder / "frames_orig" / target.name
        if not orig.exists():
            sys.exit(f"Frame {n} was never edited.")
        shutil.copyfile(orig, target)
        print(f"frame {n} restored")
        return
    backup(folder, target)
    if op == "replace":
        Image.open(frame_path(folder, int(rest[0]))).save(target)
    elif op == "blend":
        a = Image.open(frame_path(folder, int(rest[0]))).convert("RGB")
        b = Image.open(frame_path(folder, int(rest[1]))).convert("RGB")
        Image.blend(a, b, 0.5).save(target)
    elif op == "erase":
        img = Image.open(target).convert("RGB")
        colour = img.getpixel(BACKGROUND_SAMPLE)
        x0, y0, x1, y1 = (int(v) for v in rest[:4])
        img.paste(colour, (x0, y0, x1, y1))
        img.save(target)
    elif op == "put":
        size = Image.open(target).size
        Image.open(rest[0]).convert("RGB").resize(size).save(target)
    else:
        sys.exit(__doc__)
    print(f"frame {n}: {op} done")


if __name__ == "__main__":
    main()
