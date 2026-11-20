# Provider: Grok Imagine (grok.com)

These are the browser steps for each generation, driven through Claude in Chrome (or by
hand). They were tested on the grok.com/imagine UI. If the UI changes, update this file.

## Before you start
- Use the Chrome **on the machine that runs the scripts**, so downloads land in the
  Downloads folder in `config.json`. If downloads never appear, the session is driving
  another machine's Chrome. Connect the right one (`switch_browser`; the user clicks
  Connect in the extension side panel).
- Log in to grok.com in that browser yourself.

## Image (clean / pose)
1. Open `https://grok.com/imagine`.
2. Upload the reference by setting the hidden `input[type=file]` (`find` "file input" +
   `file_upload`). **Never click Upload**: it opens a native dialog.
3. Optional: for poses that need horizontal room (a long reach), open the composer's
   aspect-ratio button and pick **16:9**.
4. Click the prompt box, type one throwaway character, clear it (Ctrl+A, Delete), then
   type the image prompt. The first keystrokes in a fresh box are sometimes dropped.
5. Press Enter and wait about 20 s. The page becomes `.../imagine/post/<post id>?conversation=...`.
6. If the result drifts (wrong angle, extra props, wrong facing), use **Regenerate** once.
7. Download: `find` the Download button in the image toolbar (the one inside the
   "Segments / Precise Edit / ..." bar, **not** "Download All", which gives `segments.zip`).
   The file is `grok-image-<post id>.jpg`.
   `python pipeline/grab.py <char> <action> image <post id>`

## Video
1. On the pose image post: **Make Video** (right panel) > **Add Prompt**.
2. Click the prompt box, type a throwaway character, clear it, then type the video prompt.
3. Check the composer is in **video** mode (camera icon selected, it shows "720p 6s").
   Add Prompt sometimes opens it in image mode, so click the video icon.
4. Click submit (bottom-right of the box) and wait about 30 s.
5. If Grok asks **"Which video do you prefer to keep?"**, compare both mid-motion and
   click "I prefer this" under the better one.
6. Download: `find` "Download" next to "Post to X". The file is
   `grok-video-<conversation id>.mp4`.
   `python pipeline/grab.py <char> <action> video <conversation id>`
   This also writes `pose.jpg` from frame 1 when the image download wasn't kept.

## Reusing a pose for more videos
Note the image post URL (`.../imagine/post/<post id>`) and `navigate` back to it for
each video, then Make Video again. Several videos from one pose share a conversation id,
so grab each before starting the next.

## Gotchas
- Escape closes the post. Don't use it on Grok's survey popup; navigate back instead.
- Regenerate on a video post makes another take of the same prompt. Extend continues a
  video that ends too early.
