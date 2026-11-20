# animationPipeline

**One picture of a character in, sprite animations out.**

An art AI (chosen at setup; [Grok Imagine](https://grok.com/imagine) is included) redraws
the character in a start pose, then turns that pose into a short video. The pipeline cuts
the video into frames, lets you pick and fix them, and exports transparent PNGs plus a
sprite sheet for any engine.

It is built to be run by [Claude Code](https://claude.com/claude-code) with Claude in
Chrome driving the AI's website. Every step is also a plain script you can run by hand.

```
picture -> clean (remove background) -> pose image -> video -> frames -> pick -> export
```

## Requirements
- Python 3.10+ and `pip install -r requirements.txt` (Pillow)
- [ffmpeg](https://ffmpeg.org) on PATH
- An account with the art AI (e.g. grok.com), logged in, in Chrome
- For the automated flow: Claude Code with the Claude in Chrome extension, connected to
  the Chrome on the same machine (so downloads land where the scripts look)

## Quick start (with Claude Code)
Open this folder in Claude Code and say:
1. **"Set up the pipeline"** (`/setup-pipeline`). It asks:
   - which AI to use, your art style, facing direction, fps and Downloads folder
   - which animations you want
   
   **No animation types are built in.** You define each one (what happens, and which pose
   it starts from).
2. **"Run the pipeline on `<picture>`, call it `<name>`"** (`/generate-animation`).
   Claude removes the background, makes each pose and video, cuts the frames and shows you
   a numbered contact sheet per animation.
3. **Give feedback in plain words** (`/animation-feedback`), e.g.:
   - "too slow"
   - "frame 40 glitches"
   - "the chair should stay in one piece"
   - "go back to the previous one"

   Claude picks the cheapest fix:

   | Level | Fix | Uses the AI? |
   |---|---|---|
   | 1 | Re-cut the frames | No |
   | 2 | Repair single frames | Optional |
   | 3 | Regenerate the video | Yes |
   | 4 | Regenerate the pose | Yes |

   Every take is kept, so any change can be undone.
4. **"Export it"**: transparent frames and `sheet.png` + `sheet.json` in
   `characters/<name>/<action>/export/`.

## By hand
```
python pipeline/setup.py init --provider grok --style "pixel art" --facing right --fps 12
python pipeline/setup.py action <action> --image "<pose prompt>" --video "<motion prompt>"
python pipeline/setup.py character <name> <picture>
python pipeline/setup.py slots <name> <action> --pose "..." --motion "..."
python pipeline/make_prompts.py <name> clean      # paste into the AI, download
python pipeline/grab.py <name> clean image <id>
python pipeline/make_prompts.py <name> <action>   # pose image, then video, download
python pipeline/grab.py <name> <action> video <id>
python pipeline/pick.py <name> <action>           # after editing selection.json
python pipeline/export.py <name> <action> --size 160
```
The provider's UI steps and where `<id>` comes from: `providers/<provider>.md`.

## Layout
| Path | What |
|---|---|
| `pipeline/` | Scripts and `actions.json` (your animation types) |
| `providers/` | One `.json` + `.md` per art AI. `providers/README.md` explains how to add one |
| `characters/` | Your characters and all generated output (git-ignored) |
| `docs/PIPELINE.md` | The full reference: flow, prompt-writing tips, files, feedback levels |
| `.claude/skills/` | The three Claude Code skills |
