# Picture-to-animation pipeline - Claude Code guide

Turns one picture of a character into sprite animations with an art AI driven through
Claude in Chrome (the provider is chosen at setup; grok.com is included).

- Skills: `setup-pipeline` (config, provider, animation types), `generate-animation`
  (make them), `animation-feedback` (revise from human feedback).
- Source of truth: `docs/PIPELINE.md`. Provider UI steps: `providers/<provider>.md`.
- Python 3.10+ with Pillow, and ffmpeg on PATH. Scripts run from the repo root:
  `python pipeline/<script>.py ...`.

## Rules
- No animation types are built in. Only add the ones the user defines (`setup.py action`).
- Prompt templates stay generic; character detail goes in characters.json slots.
- Move downloads only with `pipeline/grab.py` (waits for the exact file).
- Never delete a take (`versions.py archive`); never edit frames without `frame_edit.py`.
- The user logs in to the provider themselves; never type their password.
