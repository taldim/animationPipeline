---
name: setup-pipeline
description: >
  First-time setup and configuration of the picture-to-animation pipeline: choose the art
  AI provider (e.g. grok.com), art style, facing, fps and downloads folder; define the
  animation types the user wants (none ship by default); add a new provider. Use for
  "set up the pipeline", "use <AI> instead", "add a <name> animation", "what animations do
  we have". Not for generating (`generate-animation`) or revising (`animation-feedback`).
---

# Set up the pipeline

`T=pipeline`. Reference: `docs/PIPELINE.md` ("Writing action prompts").

## 1. Config (once, or to switch provider)
Ask the user in one go, offering what exists:
- **Provider:** list `providers/*.json`, with names and URLs.
- **Art style**, e.g. "pixel art".
- **Facing:** right or left.
- **fps:** 12 is a good default for 6 s videos.
- **Downloads folder:** default `~/Downloads`. It must be the downloads folder of the
  browser Claude in Chrome drives, on this machine.

Then: `python $T/setup.py init --provider P --style "S" --facing F --fps N --downloads "D"`.
The user logs in to the provider's site themselves.

## 2. Animation types
Nothing is predefined. Ask which animations they want and, for each:
- what happens
- whether it starts from its own pose or from another action's pose

Prefer `--pose-from` for actions that start in the same stance, so the character matches
across them.

Write generic templates ("the character", "they") with the slots, following "Writing
action prompts". Put character-specific detail in the `{pose}`/`{motion}` slots, not in
the template:
```
python $T/setup.py action <name> --image "..." --video "..."
python $T/setup.py action <name> --pose-from <other> --video "..."
```
Show the user the templates you wrote. They are the main quality lever.

## 3. A new provider
Only if the user wants an AI that has no `providers/<name>.json`.
1. Follow `providers/README.md`.
2. Explore the site with Claude in Chrome to learn:
   - how to upload a reference
   - how to run an image prompt
   - how to make an image into a video
   - the download file names and where their ids come from
3. Write `<name>.json` and `<name>.md`, test one image and one video end to end, then
   `setup.py init --provider <name>`.

## Rules
- Never add animation types the user didn't ask for.
- Never type the user's password. They log in to the provider themselves.
