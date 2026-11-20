---
name: animation-feedback
description: >
  Revises a generated character animation from human feedback, in a loop: re-cut frames,
  fix single frames (by hand or with the AI's image edit), regenerate the video, or
  regenerate the pose, keeping every take so any change can be undone. Use when the user
  comments on an animation in characters/ ("too slow", "frame 40 glitches", "she should
  spin first", "go back to the previous one", "make it calmer"). Not for first-time
  generation (`generate-animation`).
---

# Animation feedback loop

Pipeline reference: `docs/PIPELINE.md`. Tools: `T=pipeline`. Folder:
`characters/<char>/<action>/`. Provider UI steps: `providers/<config provider>.md`.

## The loop
1. **Show** what exists.
   - `python $T/review.py <char> <action>` shows the selection; add `--all` for every raw
     frame.
   - Read `review/sheet.png` yourself.
   - Give the user the paths of `review/sheet.png` and `review/preview.gif`, so they can
     look and point at frame numbers.
2. **Classify** the feedback and pick the **cheapest level** that fixes it (below). If it
   is ambiguous ("it looks weird"), ask one question naming the likely levels.
3. **Apply** it. Before level 3 or 4, run
   `python $T/versions.py archive <char> <action> "<feedback>"`.
4. **Log** it: append to `<action>/feedback.md`:
   `- <date> | "<user's words>" | level N: <what you changed> | take vNN`.
5. **Show again** (step 1) with a one-line summary of what changed, and ask if it's right.
   Repeat until the user is happy, then run `python $T/pick.py <char> <action>` and
   `python $T/export.py <char> <action>`.

## Levels
**1. Re-cut (no AI).** Timing and range problems. Edit `selection.json`:
- "too slow": `step: 2` (or raise `fps`).
- "too fast": lower `fps`, or extract more frames
  (`video_to_frames.py <char> <action> 24`, which resets edits).
- "starts too late" or "cut the ending": `start` / `end` (raw frame numbers from the sheet).
- "doesn't loop": choose an `end` frame that matches `start`; check both on the sheet.
- "hold the last pose": `hold_last`.
- "skip those frames": `drop`.

**2. Frame fix.** One or a few bad frames.
- **By hand:** `frame_edit.py <char> <action> replace|blend|erase|undo ...` (see its
  docstring).
  - A glitched frame: replace it with a neighbour, or blend its neighbours.
  - Stray pixels: erase a box (raw pixel coordinates; zoom in with the Read tool on the
    frame).
- **With the AI:** upload that frame PNG in image mode with an edit prompt ("Same image,
  remove the stray spark on the left, change nothing else. Keep the green background."),
  download it, then run `frame_edit.py <char> <action> put <n> <downloaded file>`. Use this
  when the fix needs drawing (a missing hand, a wrong colour on the character).

**3. Re-video.** The motion itself is wrong: it does the wrong thing, slides, turns away,
or the effect is cut off.
1. Add the fix as a short positive instruction to `characters/characters.json` ->
   `<char>.<action>.video_fix` (a list; keep earlier fixes), e.g.
   `"The chair stays in one piece the whole time."`.
2. Run `make_prompts.py`.
3. Open the **same pose image post** (or upload `pose.jpg` in image mode) and make the
   video.
4. `grab.py <char> <action> video <id>`.

If the provider has a Regenerate on the video, it gives another take of the same
prompt; use it when the prompt was fine but the result was unlucky.

**4. Re-pose.** The look is wrong: angle, outfit, props, proportions.
- Add an `image_fix` to the action that owns the pose.
- Actions with `pose_from` that action share the pose, so they all need new videos. Say
  so before doing it.
- Make the new pose, then continue with level 3.

## Undo
For "go back" or "the previous one was better":
1. `versions.py list`, then `versions.py restore <char> <action> vNN` (it archives the
   current take first).
2. Remove the matching `video_fix`/`image_fix` from `characters.json` if the restore undoes
   it, and log it.

## Rules
- Never delete a take; archive it. Never edit `frames/` without `frame_edit.py` (it backs
  up).
- Keep fixes short and positive ("feet stay on the same spot") rather than negative.
- After a level 3 or 4 change, compare against the old take's sheet in
  `history/vNN/review/`.
