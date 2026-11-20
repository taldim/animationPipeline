---
name: generate-animation
description: >
  Generates a character's sprite animations from one picture with the configured art AI
  (config.json provider, e.g. grok.com) through Claude in Chrome: background removal
  (clean), pose image, image-to-video, frame extraction, review sheet, export. Use for
  "make the <action> animation for <character>", "run the pipeline on this picture", or
  a new character. Not for first-time setup or defining animations (`setup-pipeline`)
  or changing an existing animation from feedback (`animation-feedback`).
---

# Generate animations

Read `docs/PIPELINE.md` first: it is the source of truth for the flow, files and rules.
`T=pipeline` below. Outputs: `characters/<char>/<action>/`.

## 0. Preconditions
- `config.json` exists and the requested actions exist in `$T/actions.json`. If not, run
  the `setup-pipeline` skill first. Never invent animation types the user didn't define.
- Read `providers/<provider>.json` and the steps file it names (`providers/<provider>.md`).
  Follow those UI steps exactly. They hold the provider's gotchas.

## 1. Character
- **New picture:** `python $T/setup.py character <char> <picture>`.
  - Add `--isolated` if it's already on a plain background.
  - Use `--background white` only for dark-outlined characters with no white parts.
- **Per action the character needs:**
  `python $T/setup.py slots <char> <action> --pose "..." --motion "..."`, written with the
  character's own props and pronoun.
  - If the user gave a unique move for an action (e.g. their attack), it goes in
    `--motion`.
  - If an action needs a character-specific move and the user didn't say what, ask.
- `python $T/make_prompts.py <char> <action>` for each action. Paste the prompts exactly.

## 2. Generate (order matters)
1. **`clean`** (skip it with `--isolated`): give the AI the source picture and the clean
   prompt, then `python $T/grab.py <char> clean image <id>` (this also writes
   `reference.png`). Check that the character is unchanged and alone on the plain
   background.
2. **Actions with their own pose** (an `image` template) come before the actions that use
   `pose_from` them. For each:
   - upload `reference.png` and run the image prompt
   - check the pose: facing, look, framing
   - make the video from that image post
3. **`pose_from` actions:** go back to the source action's image post (note its URL) and
   make each video from it.
4. **After each video download:** `python $T/grab.py <char> <action> video <id>`. Never
   move files by "newest in Downloads".

## 3. Review
`grab.py` builds `review/sheet.png` (every frame, numbered). Read it and check:
- it faces the configured direction and stays in place
- the motion matches the action
- the look matches the reference, with no props vanishing or morphing
- the effect isn't cut off at the frame edge

If a take is wrong, use the `animation-feedback` levels (regenerating is level 3 or 4,
after `versions.py archive`).

## 4. Report
For each action, give:
- what happens
- anything off, with frame numbers from the sheet
- the folder

Then offer:
- pick frames (`selection.json` + `pick.py`) and export (`export.py <char> <action>
  [--size H]`)
- or run the feedback loop
