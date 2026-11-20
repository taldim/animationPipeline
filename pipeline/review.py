"""Numbered contact sheet + preview GIF, so a human can point at frames.

Usage:  python pipeline/review.py <char> <action> [--all]
Default shows the current selection (selection.json); --all shows every raw frame.
Writes <action>/review/sheet.png (labels = raw frame numbers) and preview.gif
(plays at the selection's fps, loops if "loop" is true).
"""
import sys

from PIL import Image, ImageDraw, ImageFont

from paths import action_dir, args_or_usage, load_selection, raw_frames, selected_frames

THUMB_W = 220
COLUMNS = 8
GIF_W = 360
LABEL_SIZE = 22


def number_of(path) -> int:
    return int(path.stem.split("_")[1])


def contact_sheet(paths: list, out) -> None:
    first = Image.open(paths[0])
    thumb_h = round(first.height * THUMB_W / first.width)
    rows = (len(paths) + COLUMNS - 1) // COLUMNS
    sheet = Image.new("RGB", (COLUMNS * THUMB_W, rows * thumb_h), "black")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=LABEL_SIZE)
    for i, path in enumerate(paths):
        x, y = (i % COLUMNS) * THUMB_W, (i // COLUMNS) * thumb_h
        sheet.paste(Image.open(path).convert("RGB").resize((THUMB_W, thumb_h)), (x, y))
        draw.rectangle((x, y, x + 44, y + LABEL_SIZE + 6), fill="black")
        draw.text((x + 4, y + 2), str(number_of(path)), fill="white", font=font)
    sheet.save(out)


def preview_gif(paths: list, fps: int, loop: bool, out) -> None:
    images = []
    for path in paths:
        img = Image.open(path).convert("RGB")
        images.append(img.resize((GIF_W, round(img.height * GIF_W / img.width))))
    extra = {"loop": 0} if loop else {}
    images[0].save(out, save_all=True, append_images=images[1:],
                   duration=round(1000 / fps), **extra)


def main() -> None:
    character, action = args_or_usage(2, __doc__)[:2]
    folder = action_dir(character, action)
    show_all = "--all" in sys.argv
    paths = raw_frames(folder) if show_all else selected_frames(folder)
    if not paths:
        sys.exit("No frames: run video_to_frames.py first.")
    sel = load_selection(folder)
    review = folder / "review"
    review.mkdir(exist_ok=True)
    contact_sheet(paths, review / "sheet.png")
    preview_gif(paths, sel["fps"], sel["loop"], review / "preview.gif")
    print(f"{len(paths)} frames -> {review / 'sheet.png'} and preview.gif")


if __name__ == "__main__":
    main()
