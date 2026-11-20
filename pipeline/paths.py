"""Shared paths, config and frame selection for the pipeline tools."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "pipeline"
GENERATED = ROOT / "characters"
PROVIDERS = ROOT / "providers"
CONFIG = ROOT / "config.json"
DEFAULT_SELECTION = {"start": 1, "end": 0, "step": 1, "drop": [], "hold_last": 0,
                     "fps": 12, "loop": True}


def load_config() -> dict:
    """config.json, written by setup.py: provider, style, facing, fps, downloads."""
    if not CONFIG.exists():
        sys.exit("No config.json: run `python pipeline/setup.py` first.")
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def load_provider(config: dict) -> dict:
    path = PROVIDERS / f"{config['provider']}.json"
    if not path.exists():
        sys.exit(f"No provider file {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def action_dir(character: str, action: str) -> Path:
    folder = GENERATED / character / action
    if not folder.exists():
        sys.exit(f"No folder {folder}")
    return folder


def raw_frames(folder: Path) -> list:
    return sorted((folder / "frames").glob("frame_*.png"))


def frame_path(folder: Path, number: int) -> Path:
    path = folder / "frames" / f"frame_{number:02d}.png"
    if not path.exists():
        sys.exit(f"No frame {number} in {folder / 'frames'}")
    return path


def load_selection(folder: Path) -> dict:
    """selection.json: which raw frames make the animation. end 0 = last frame."""
    path = folder / "selection.json"
    selection = dict(DEFAULT_SELECTION)
    if CONFIG.exists():
        selection["fps"] = load_config().get("fps", selection["fps"])
    if path.exists():
        selection.update(json.loads(path.read_text(encoding="utf-8")))
    else:
        path.write_text(json.dumps(selection, indent=2), encoding="utf-8")
    return selection


def selected_frames(folder: Path) -> list:
    """Raw frame paths in play order, after start/end/step/drop/hold_last."""
    frames = raw_frames(folder)
    sel = load_selection(folder)
    end = sel["end"] or len(frames)
    numbers = [n for n in range(sel["start"], end + 1, max(1, sel["step"]))
               if n not in sel["drop"] and n <= len(frames)]
    picked = [frames[n - 1] for n in numbers]
    if picked and sel["hold_last"]:
        picked += [picked[-1]] * sel["hold_last"]
    return picked


def args_or_usage(count: int, doc: str) -> list:
    if len(sys.argv) < count + 1:
        sys.exit(doc)
    return sys.argv[1:]
