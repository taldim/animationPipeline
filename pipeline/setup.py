"""Set up the pipeline: choose the art AI, define your animations, add characters.

  python pipeline/setup.py init [--provider P] [--style S] [--facing F] [--fps N] [--downloads DIR]
      Writes config.json. Missing options are asked interactively.
      Providers are the providers/*.json files (e.g. grok).
  python pipeline/setup.py action <name> [--image TEXT] [--video TEXT] [--pose-from ACTION]
      Adds or replaces an animation type in pipeline/actions.json. Templates may use
      {pose} {motion} {background} {style} {facing}. Give --image (a start pose) or
      --pose-from (reuse another action's pose), and --video (the motion).
  python pipeline/setup.py character <name> <picture> [--background TEXT] [--isolated]
      Copies the picture to characters/<name>/ (source.*, or reference.png with
      --isolated when it already has a plain background) and adds the character.
  python pipeline/setup.py slots <name> <action> [--pose TEXT] [--motion TEXT]
      The character's own lines for one action ({pose} into the image prompt,
      {motion} into the video prompt). Run once per action the character needs.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

from paths import CONFIG, GENERATED, PIPELINE, PROVIDERS

GREEN = "plain flat solid bright green (#00FF00) chroma key background"
WHITE = "plain flat solid white background"
CHARACTERS = GENERATED / "characters.json"
ACTIONS = PIPELINE / "actions.json"
CHAR_COMMENT = ("One entry per character: 'reference' (repo-relative master look), "
                "'background', and per action 'pose'/'motion' lines plus optional "
                "'image_fix'/'video_fix' feedback lists.")


def read(path: Path, default: dict) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else dict(default)


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ask(label: str, current, choices=None):
    if current is not None:
        return current
    hint = f" ({'/'.join(choices)})" if choices else ""
    while True:
        answer = input(f"{label}{hint}: ").strip()
        if answer and (not choices or answer in choices):
            return answer


def cmd_init(args) -> None:
    providers = sorted(p.stem for p in PROVIDERS.glob("*.json"))
    if not providers:
        sys.exit("No providers/*.json found.")
    if args.provider and args.provider not in providers:
        sys.exit(f"Unknown provider '{args.provider}'. Available: {providers}")
    config = read(CONFIG, {})
    config["provider"] = ask("Art AI provider", args.provider, providers)
    config["style"] = ask("Art style (e.g. pixel art, hand-drawn cartoon)", args.style)
    config["facing"] = ask("Direction characters face and attack", args.facing,
                           ["right", "left"])
    config["fps"] = int(ask("Frames per second to cut videos at", args.fps))
    config["downloads"] = ask("Folder the browser downloads into",
                              args.downloads or str(Path.home() / "Downloads"))
    write(CONFIG, config)
    if not CHARACTERS.exists():
        write(CHARACTERS, {"_comment": CHAR_COMMENT})
    provider = json.loads((PROVIDERS / f"{config['provider']}.json").read_text("utf-8"))
    print(f"config.json written. Provider: {provider['name']} ({provider['url']}), "
          f"steps in {provider['steps']}.")


def cmd_action(args) -> None:
    if not args.video:
        sys.exit("An animation needs --video (what happens in it).")
    if bool(args.image) == bool(args.pose_from):
        sys.exit("Give exactly one of --image (own start pose) or --pose-from ACTION.")
    actions = read(ACTIONS, {})
    if args.pose_from and args.pose_from not in actions:
        sys.exit(f"--pose-from '{args.pose_from}' is not an action yet; add it first.")
    entry = {"video": args.video}
    if args.image:
        entry["image"] = args.image
    else:
        entry["pose_from"] = args.pose_from
    actions[args.name] = entry
    write(ACTIONS, actions)
    print(f"Action '{args.name}' saved in {ACTIONS}.")


def cmd_character(args) -> None:
    picture = Path(args.picture)
    if not picture.exists():
        sys.exit(f"No file {picture}")
    if " " in args.name:
        sys.exit("Use a character name without spaces.")
    folder = GENERATED / args.name
    folder.mkdir(parents=True, exist_ok=True)
    if args.isolated:
        target = folder / "reference.png"
        if picture.suffix.lower() == ".png":
            shutil.copyfile(picture, target)
        else:
            from PIL import Image
            Image.open(picture).save(target)
    else:
        target = folder / f"source{picture.suffix.lower()}"
        shutil.copyfile(picture, target)
    background = {"green": GREEN, "white": WHITE}.get(args.background, args.background)
    chars = read(CHARACTERS, {"_comment": CHAR_COMMENT})
    entry = chars.get(args.name, {})
    entry.update({"reference": f"characters/{args.name}/reference.png",
                  "background": background})
    entry.setdefault("clean", {})
    chars[args.name] = entry
    write(CHARACTERS, chars)
    step = "" if args.isolated else " Next: the `clean` step makes reference.png."
    print(f"Character '{args.name}' added ({target}).{step}")


def cmd_slots(args) -> None:
    chars = read(CHARACTERS, {})
    if args.name not in chars:
        sys.exit(f"No character '{args.name}': run `setup.py character` first.")
    if args.action not in read(ACTIONS, {}):
        sys.exit(f"No action '{args.action}': run `setup.py action` first.")
    slots = chars[args.name].setdefault(args.action, {})
    slots["pose"] = args.pose if args.pose is not None else slots.get("pose", "")
    slots["motion"] = args.motion if args.motion is not None else slots.get("motion", "")
    write(CHARACTERS, chars)
    print(f"{args.name}.{args.action}: pose={slots['pose']!r} motion={slots['motion']!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    for opt in ("provider", "style", "facing", "fps", "downloads"):
        p.add_argument(f"--{opt}")
    p.set_defaults(run=cmd_init)
    p = sub.add_parser("action")
    p.add_argument("name")
    p.add_argument("--image")
    p.add_argument("--video")
    p.add_argument("--pose-from")
    p.set_defaults(run=cmd_action)
    p = sub.add_parser("character")
    p.add_argument("name")
    p.add_argument("picture")
    p.add_argument("--background", default="green",
                   help="green (default, safe with white parts), white, or your own text")
    p.add_argument("--isolated", action="store_true")
    p.set_defaults(run=cmd_character)
    p = sub.add_parser("slots")
    p.add_argument("name")
    p.add_argument("action")
    p.add_argument("--pose")
    p.add_argument("--motion")
    p.set_defaults(run=cmd_slots)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
