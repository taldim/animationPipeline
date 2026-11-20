# The pipeline in detail

How a character goes from one picture to sprite animations, and how an animation is
fixed from feedback. Claude Code runs it with three skills:
- `/setup-pipeline`: choose the AI, define your animations, add characters
- `/generate-animation`: make them
- `/animation-feedback`: revise them

Scripts are in `pipeline/`. Each action's output goes in `characters/<char>/<action>/`.

## The flow

```
picture --clean--> reference.png --image prompt--> pose.jpg --video prompt--> video.mp4
(any scene)      (plain/green bg)                (start frame)              (the motion)
video.mp4 --video_to_frames--> frames/ --selection.json + pick--> final/ --export--> export/
                                                                     (transparent PNGs + sheet)
```

1. **Setup** (`setup.py init`): choose the art AI provider (`providers/*.json`; grok.com is
   included), the art style, which way characters face, the frame rate and the Downloads
   folder. This writes `config.json`.
2. **Animations** (`setup.py action`): you define every animation type. None ship by
   default. Each one has:
   - an **image prompt**, the start pose of the video. Or `--pose-from <other action>`
     to reuse that action's pose, so the character looks identical across animations
     that start from the same stance.
   - a **video prompt**: what happens.
3. **Character** (`setup.py character`): one picture.
   - If it has a scene behind it, the built-in `clean` step has the AI redraw the
     character unchanged on a plain background. That becomes `reference.png`.
   - Then `setup.py slots` adds the character's own lines per action (their prop, their
     unique move).
4. **Pose image**: the provider's image mode, with the reference attached and the image
   prompt.
5. **Video**: the provider turns the pose image into a short video using the video prompt.
6. **Frames**: ffmpeg cuts the video at the configured fps.
7. **Selection**: `selection.json` says which frames make the animation. `pick.py` copies
   them, renumbered, to `final/`.
8. **Export**: `export.py` keys out the background and crops every frame to the same box
   so nothing jitters. It can also scale (nearest-neighbour). It writes
   `export/frame_NN.png`, `export/sheet.png` and `export/sheet.json` (frame size, count,
   fps, loop, facing). Import those into any engine.

## Writing action prompts
Templates live in `pipeline/actions.json` and are shared by every character. Slots:
| Slot | Filled from |
|---|---|
| `{pose}` | the character's `pose` line for this action (image prompt) |
| `{motion}` | the character's `motion` line for this action (video prompt) |
| `{background}` | the character's background (green screen by default) |
| `{style}`, `{facing}` | `config.json` |

What worked well:
- **Image prompt:** start with "Same exact character, same {style} style, same colors
  and outfit", give the view ("side view facing {facing}"), the stance, `{pose}`, "full
  body", the framing, then "{background}, no shadow".
- **Video prompt:** describe the motion, then `{motion}`, then pin everything else down:
  - "Camera completely static, the character does not slide across the frame."
  - "Keep {style} style and all details identical."
  - "Background: {background}."
- **Moves that travel** (walking, running): "in place, on a treadmill".
- **Moves with reach:** put the character "in the left half of the frame with empty space
  on the {facing}", and use the provider's wide aspect ratio.
- **One-shot moves:** "starts and ends in the same pose" makes them loopable.

## Rules
- Everything faces one way (`config.json` facing). Flip the sprite in the engine for the
  other side.
- **Background:**
  - Use a green screen (`#00FF00`) whenever the character or an effect has white or
    light parts.
  - White only works for characters with a dark outline.
- **Check the contact sheet every time.** Videos drift: a prop vanishes, an object breaks,
  the character turns toward the camera. That is what the feedback levels are for.

## Files
| File | What |
|---|---|
| `config.json` | Provider, style, facing, fps, downloads folder (written by `setup.py init`). |
| `providers/<name>.json` + `.md` | Download file names, and how to drive that AI's UI. See `providers/README.md` to add one. |
| `pipeline/actions.json` | Your animation types (prompt templates). |
| `characters/characters.json` | Per character: `reference`, `background`, and per action `pose`, `motion`, plus feedback fixes `image_fix` / `video_fix`. |
| `setup.py` | `init`, `action`, `character`, `slots`. |
| `make_prompts.py <char> <action>` | Builds the prompts and saves `prompts.txt`. |
| `grab.py <char> <action> video\|image <id>` | Waits for that exact download, moves it in, then runs frames and review. |
| `video_to_frames.py <char> <action> [fps]` | `video.mp4` -> `frames/`. |
| `review.py <char> <action> [--all]` | Numbered contact sheet plus a preview GIF in `review/`. |
| `pick.py <char> <action>` | `selection.json` -> `final/`. |
| `export.py <char> <action> [--size H]` | `final/` -> transparent `export/` plus a sprite sheet. |
| `frame_edit.py` | Single-frame fixes: replace, blend, erase, put (an AI-edited frame), undo. |
| `versions.py` | Archive, list and restore takes in `history/vNN/`. |

Each action folder holds:
- `pose.jpg`, `video.mp4` and `prompts.txt`
- `frames/`, plus `frames_orig/` (originals of edited frames)
- `selection.json`, `final/`, `export/` and `review/`
- `history/` (past takes)
- `feedback.md` (a log of every piece of feedback and what was done)

`selection.json` keys:
- `start`, `end` (0 means the last frame)
- `step` (2 = every other frame, so twice as fast)
- `drop` (a list of raw frame numbers to skip)
- `hold_last` (repeat the last frame N times)
- `fps`, `loop`

## Feedback: how a note becomes a change
Say what's wrong in plain words ("too slow", "frame 40 has a glitch", "she should spin
first"). Claude picks the cheapest level that fixes it:

| Level | Fixes | How | Cost |
|---|---|---|---|
| 1. Re-cut | Speed, start/end, loop point, hold, stray frames | Edit `selection.json`, run `pick.py` | Seconds, no AI |
| 2. Frame fix | A glitch, stray pixels, one bad frame | `frame_edit.py`, or one frame through the AI's image edit + `put` | Minutes |
| 3. Re-video | Wrong motion, timing inside the motion, drift | `versions.py archive`, add a `video_fix`, new video from the same pose | One video |
| 4. Re-pose | Wrong look, angle, outfit, props | Archive, add an `image_fix`, new pose, then a new video | One image + one video |

Fixes go into `characters.json`, so every later regenerate keeps them. Every take is kept
in `history/`, so "go back to the previous one" is `versions.py restore`. After each change
Claude shows the new contact sheet and GIF, and the loop repeats until you're happy.
