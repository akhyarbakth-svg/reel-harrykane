# Harry Kane · Ballon d'Or 2026 — Game State reel

Source for a 48.5 s vertical Short (1080×1920, 30 fps) made for the **Game State** YouTube channel ([@GameState365](https://www.youtube.com/@GameState365)).
The whole video is a single deterministic canvas animation (`render(t)`) that is rendered frame-by-frame in headless Chrome and encoded with ffmpeg, with a synthesised sound-effects track.

## Layout

| Path | What it does |
| --- | --- |
| `reel.html` | The animation: photo plates + transitions, HUD, chapter overlays, post FX. Open it in a browser to scrub/preview. |
| `tools/render.mjs` | Serves the folder locally, drives Chrome via puppeteer-core, pipes frames into ffmpeg. `stills` and `video` modes. |
| `tools/sfx.py` | Builds `out/sfx.wav` (whooshes, hits, glitches, ticks) cue-synced to the timeline. No music bed. |
| `tools/commons_list.py`, `tools/contact.py`, `tools/fetch_images.py` | Find, preview and download the Wikimedia Commons photos. |
| `tools/crop.py` | Crops each photo to a 9:16 full-frame plate in `assets/img/`. |
| `tools/logo.py` | Lifts the Game State lockup off the channel banner into `assets/logos/gamestate-lockup.png`. |
| `tools/cutout.py`, `tools/trophy_clean.py` | Removes the background from the Ballon d'Or photo (rembg) and cleans the edge. |
| `tools/sheet.py` | Tiles rendered stills into review contact sheets. |
| `images/CREDITS.txt` | Photo credits and licences. |

## Media is not in this repo

Photos, crests, the channel logo and rendered videos are git-ignored. To rebuild them:

1. `python -I tools/fetch_images.py images` — downloads the Commons photos and writes `images/CREDITS.txt`.
2. `python -I tools/crop.py` — makes the plates in `assets/img/`.
3. Put the club/competition crests (700×700 PNGs from football-logos.cc) in `assets/logos/`, and run `python -I tools/logo.py` with `channel-banner.jpg` one folder up.
4. For the trophy: download `File:2016 Ballon dOr CR7Museum.jpg` to `images/trophy_src/cr7_2016.jpg`, run `tools/cutout.py` in a venv with `rembg[cpu]`, then `tools/trophy_clean.py` to write `assets/logos/ballon-dor-real.png`.

Optional: `assets/img/trophy.jpg` (a photo of the player holding the trophy) replaces the final plate after the reveal.

## Render

```bash
cd tools
npm install
python -I sfx.py ../out/sfx.wav
node render.mjs video ../out/reel.mp4 ../out/sfx.wav
node render.mjs stills ../out/stills 1.5,12.8,42.6
```

Needs Node 18+, Google Chrome (path set in `render.mjs`), and Python with `numpy`, `pillow` and `imageio-ffmpeg` (which provides the ffmpeg binary). Paths in the Python helpers point at `G:/Game State/reel`; adjust them if you move the project.

## Credits

Photos via Wikimedia Commons under CC BY / CC BY-SA licences; see `images/CREDITS.txt`. They were cropped, colour-graded and (trophy) cut out from their backgrounds.
Fonts: Unbounded, JetBrains Mono, Chakra Petch (Google Fonts).
