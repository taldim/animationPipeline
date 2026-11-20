"""Copy the selected frames (selection.json) to <action>/final/, renumbered.

Usage:  python pipeline/pick.py <char> <action>
final/ is the chosen animation; export.py turns it into transparent PNGs + a sheet.
selection.json keys: start, end (0 = last), step (2 = every other frame, so twice as
fast), drop (list of raw frame numbers), hold_last (repeat the last frame N times),
fps, loop. Edit it, then re-run this and review.py.
"""
import shutil

from paths import action_dir, args_or_usage, selected_frames


def main() -> None:
    character, action = args_or_usage(2, __doc__)[:2]
    folder = action_dir(character, action)
    picked = selected_frames(folder)
    final = folder / "final"
    if final.exists():
        shutil.rmtree(final)
    final.mkdir()
    for i, path in enumerate(picked, start=1):
        shutil.copyfile(path, final / f"frame_{i:02d}.png")
    print(f"{len(picked)} frames -> {final}")


if __name__ == "__main__":
    main()
