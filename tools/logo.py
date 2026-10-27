# Lifts the Game State lockup (G mark + wordmark) off the channel banner into a transparent PNG.
from PIL import Image
import numpy as np
b = np.asarray(Image.open("G:/Game State/channel-banner.jpg").convert("RGB")).astype(float)
crop = b[44:112, 330:815]
bg = np.array([8, 9, 13], float)
mx = crop.max(axis=2)
a = np.clip((mx - 55) / (225 - 55), 0, 1)              # dim pitch lines fall below the floor
rgb = np.where(a[..., None] > 0, (crop - bg * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
rgb = np.clip(rgb, 0, 255)
out = np.dstack([rgb, a * 255]).astype(np.uint8)
im = Image.fromarray(out)
im = im.crop(im.getbbox())
im = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)  # canvas draws it ~0.6x, so oversample
im.save("G:/Game State/reel/assets/logos/gamestate-lockup.png")
print(im.size)
