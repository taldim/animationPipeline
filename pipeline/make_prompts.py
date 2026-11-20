"""Print the image + video prompts for one character action.

Usage:  python pipeline/make_prompts.py <character> <action>
Writes them to characters/<character>/<action>/prompts.txt too, so the
prompts used for each output are kept next to it.
"""
import json
import sys

from paths import GENERATED, PIPELINE as HERE, load_config


def build(character: str, action: str) -> dict:
    actions = json.loads((HERE / "actions.json").read_text(encoding="utf-8"))
    chars_file = GENERATED / "characters.json"
    if not chars_file.exists():
        sys.exit("No characters/characters.json: run `python pipeline/setup.py` first.")
    chars = json.loads(chars_file.read_text(encoding="utf-8"))
    config = load_config()
    if action not in actions:
        known = [a for a in actions if a[0] != "_"]
        sys.exit(f"Unknown action '{action}'. Known: {known}. Add it with setup.py action.")
    if character not in chars:
        sys.exit(f"Unknown character '{character}'. Add it to characters/characters.json.")
    char = chars[character]
    slots = char.get(action)
    if slots is None:
        sys.exit(f"characters.json has no '{action}' entry for '{character}'.")
    fill = {"background": char["background"], "style": config["style"],
            "facing": config["facing"], **slots}
    out = {key: " ".join(text.format(**fill).split())
           for key, text in actions[action].items() if key != "pose_from"}
    # Human feedback, kept per character/action so a regenerate keeps every past fix.
    for key in ("image", "video"):
        fixes = slots.get(f"{key}_fix", [])
        if fixes and key in out:
            out[key] += " " + " ".join(fixes)
    pose_from = actions[action].get("pose_from")
    if pose_from:
        # Shares another action's pose image, so the character matches across them.
        out["image"] = f"(none: reuse characters/{character}/{pose_from}/pose.jpg)"
    out["reference"] = char["reference"]
    return out


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    character, action = sys.argv[1], sys.argv[2]
    prompts = build(character, action)
    text = (
        f"reference: {prompts['reference']}\n\n"
        f"IMAGE PROMPT:\n{prompts.get('image', '(none)')}\n\n"
        f"VIDEO PROMPT:\n{prompts.get('video', '(none)')}\n"
    )
    out_dir = GENERATED / character / action
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompts.txt").write_text(text, encoding="utf-8")
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
