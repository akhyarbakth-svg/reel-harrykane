# Cleans the rembg cut-out of the 2016 Ballon d'Or: the ball gets a fitted anti-aliased circle edge,
# the pyrite base keeps the model mask; mild warm/contrast grade. Writes assets/logos/ballon-dor-real.png.
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
im = Image.open(sys.argv[1]).convert("RGBA")
a = np.asarray(im.getchannel("A")).astype(float) / 255
H, W = a.shape
rows = np.where(a.max(axis=1) > 0.5)[0]; top = rows[0]
# widest extent in the upper 55% of the object is the ball's diameter
best = (0, 0, 0)
for y in range(top, top + int((rows[-1] - top) * 0.55)):
    xs = np.where(a[y] > 0.5)[0]
    if len(xs) and xs[-1] - xs[0] > best[0]: best = (xs[-1] - xs[0], xs[0], xs[-1])
d, l, r = best; R = d / 2; cx = (l + r) / 2; cy = top + R
yy, xx = np.mgrid[0:H, 0:W]
circ = np.clip(R - np.hypot(xx - cx, yy - cy) + 0.5, 0, 1)
ball_zone = yy < cy + R * 0.82
alpha = np.where(ball_zone, circ, np.maximum(a, circ))
out = np.asarray(im).copy(); out[..., 3] = (alpha * 255).astype(np.uint8)
res = Image.fromarray(out)
rgb = res.convert("RGB")
rgb = ImageEnhance.Contrast(rgb).enhance(1.08)
rgb = ImageEnhance.Color(rgb).enhance(1.18)
r_, g_, b_ = [np.asarray(c).astype(float) for c in rgb.split()]
warm = np.dstack([np.clip(r_ * 1.05, 0, 255), np.clip(g_ * 1.0, 0, 255), np.clip(b_ * 0.9, 0, 255)]).astype(np.uint8)
res = Image.fromarray(np.dstack([warm, out[..., 3]]))
res = res.crop(res.getbbox())
res.thumbnail((1000, 1000), Image.LANCZOS)
res.save(sys.argv[2])
print("ball centre", round(cx), round(cy), "R", round(R), "->", res.size)
prev = Image.new("RGBA", res.size, (18, 24, 30, 255)); prev.alpha_composite(res)
prev.convert("RGB").resize((res.width * 700 // res.height, 700)).save(sys.argv[3])
