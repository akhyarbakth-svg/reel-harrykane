# Crop each source photo to a 9:16 full-frame plate. (cx, cy) = focus as fraction, h = crop height fraction.
from PIL import Image, ImageOps, ImageFilter
import sys
SRC, DST = "G:/Game State/reel/images", "G:/Game State/reel/assets/img"
crops = {
    "hook": (0.42, 0.50, 1.00), "scan": (0.52, 0.56, 0.80), "origins": (0.37, 0.50, 1.00),
    "young": (0.50, 0.45, 0.92), "spurs18": (0.29, 0.50, 1.00), "spurs10": (0.38, 0.50, 1.00),
    "eng2018": (0.50, 0.50, 1.00), "england": (0.50, 0.50, 1.00), "locker": (0.50, 0.50, 1.00),
    "bayern": (0.50, 0.50, 1.00), "bayern2": (0.36, 0.50, 1.00), "action": (0.56, 0.48, 0.90),
    "final": (0.50, 0.42, 0.88),
}
W, H = 1080, 1920
pad_top = {"young": 240, "spurs18": 130, "bayern2": 170}
for k, (cx, cy, hf) in crops.items():
    ext = ".png" if k == "x" else ".jpg"
    im = ImageOps.exif_transpose(Image.open(f"{SRC}/{k}{ext}")).convert("RGB")
    ch = im.height * hf
    cw = ch * W / H
    if cw > im.width:
        cw = im.width; ch = cw * H / W
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    out = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch))).resize((W, H), Image.LANCZOS)
    pad = pad_top.get(k, 0)
    if pad:
        # Push the subject down so the header HUD doesn't sit on his face; fill the gap with a blurred stretch.
        bg = out.crop((0, 0, W, H // 3)).resize((W, H)).filter(ImageFilter.GaussianBlur(40))
        fade = Image.linear_gradient("L").resize((W, 140))
        bg.paste(out, (0, pad))
        top = out.crop((0, 0, W, 140))
        bg.paste(bg.crop((0, pad, W, pad + 140)), (0, pad), Image.eval(fade, lambda v: 255 - v))
        out = bg
    out.save(f"{DST}/{k}.jpg", quality=88, optimize=True)
    print(k, im.size, "-> crop", round(cw), "x", round(ch))
