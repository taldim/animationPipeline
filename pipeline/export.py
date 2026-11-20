"""Turn final/ (green-screen frames) into transparent sprites, ready for any engine.

Usage:  python pipeline/export.py <char> <action> [--size H] [--tolerance T]
Reads   characters/<char>/<action>/final/frame_*.png   (run pick.py first)
Writes  characters/<char>/<action>/export/frame_01.png ...  transparent, trimmed to the
        union bounding box of all frames (so the character doesn't jitter), optionally
        scaled to height H with nearest-neighbour (pixel art), plus
        export/sheet.png (one row) and export/sheet.json (frame size, count, fps, loop).
Keying: pixels close to the background colour (sampled at a corner) become transparent,
and green spill on edges is pulled toward neutral. Raise --tolerance if a green fringe
remains; lower it if parts of the character disappear.
"""
import argparse
import json

from PIL import Image

from paths import CONFIG, action_dir, load_config, load_selection

DEFAULT_TOLERANCE = 90
PAD = 2


def key(img: Image.Image, tolerance: int) -> Image.Image:
    img = img.convert("RGBA")
    bg = img.getpixel((2, 2))[:3]
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, _ = pixels[x, y]
            dist = abs(r - bg[0]) + abs(g - bg[1]) + abs(b - bg[2])
            if dist < tolerance:
                pixels[x, y] = (0, 0, 0, 0)
            elif g > r and g > b:  # green spill on edges
                pixels[x, y] = (r, max(r, b), b, 255)
    return img


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("character")
    parser.add_argument("action")
    parser.add_argument("--size", type=int, default=0, help="output height in px (0 = keep)")
    parser.add_argument("--tolerance", type=int, default=DEFAULT_TOLERANCE)
    args = parser.parse_args()

    folder = action_dir(args.character, args.action)
    frames = sorted((folder / "final").glob("frame_*.png"))
    if not frames:
        raise SystemExit(f"No frames in {folder / 'final'}: run pick.py first")
    keyed = [key(Image.open(f), args.tolerance) for f in frames]

    boxes = [im.getbbox() for im in keyed if im.getbbox()]
    left = max(0, min(b[0] for b in boxes) - PAD)
    top = max(0, min(b[1] for b in boxes) - PAD)
    right = min(keyed[0].width, max(b[2] for b in boxes) + PAD)
    bottom = min(keyed[0].height, max(b[3] for b in boxes) + PAD)
    cropped = [im.crop((left, top, right, bottom)) for im in keyed]
    if args.size:
        w = round(cropped[0].width * args.size / cropped[0].height)
        cropped = [im.resize((w, args.size), Image.NEAREST) for im in cropped]

    out = folder / "export"
    out.mkdir(exist_ok=True)
    for old in out.glob("*"):
        old.unlink()
    for i, im in enumerate(cropped, start=1):
        im.save(out / f"frame_{i:02d}.png")
    fw, fh = cropped[0].size
    sheet = Image.new("RGBA", (fw * len(cropped), fh), (0, 0, 0, 0))
    for i, im in enumerate(cropped):
        sheet.paste(im, (i * fw, 0))
    sheet.save(out / "sheet.png")
    sel = load_selection(folder)
    facing = load_config()["facing"] if CONFIG.exists() else "right"
    meta = {"frame_width": fw, "frame_height": fh, "frames": len(cropped),
            "fps": sel["fps"], "loop": sel["loop"], "facing": facing}
    (out / "sheet.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"{len(cropped)} frames {fw}x{fh} -> {out}")


if __name__ == "__main__":
    main()
