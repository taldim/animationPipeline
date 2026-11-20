# Providers

A provider is the AI service that makes the art. The pipeline needs two things from it:
1. **image from a reference + prompt**: background removal and pose images
2. **video from an image + prompt**: the animation

`setup.py` asks which provider to use and stores it in `config.json`.

To add a provider, create two files named after it (e.g. `myai.json` + `myai.md`):

`<name>.json`
| key | meaning |
|---|---|
| `name`, `url` | display name and the page where you generate |
| `steps` | path to the `.md` with the step-by-step UI instructions |
| `image_download`, `video_download` | downloaded file names, with `{id}` where the per-result id goes |
| `image_id`, `video_id` | where to read that id (usually from the result page URL) |
| `video_seconds`, `video_resolution`, `wide_aspect` | what one video gives, and the wide aspect ratio option |

`<name>.md`: how to upload a reference, run an image prompt, turn an image into a
video, and download each result, plus the provider's gotchas. See `grok.md`.

If the provider has no per-result id in its file names, use `{id}` for the whole
varying part. `grab.py` waits for that exact file, so stale downloads are never used.
