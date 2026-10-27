import sys, glob, os
from PIL import Image, ImageDraw
src, prefix, per = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8
fs = sorted(glob.glob(src + "/*.jpg"))
w, h, cols = 360, 640, 4
for s in range(0, len(fs), per):
    chunk = fs[s:s + per]; rows = (len(chunk) + cols - 1) // cols
    sh = Image.new("RGB", (cols * w, rows * (h + 22)), (25, 25, 25)); d = ImageDraw.Draw(sh)
    for i, f in enumerate(chunk):
        x, y = (i % cols) * w, (i // cols) * (h + 22)
        sh.paste(Image.open(f).resize((w, h)), (x, y)); d.text((x + 4, y + h + 4), os.path.basename(f), fill=(200, 255, 60))
    sh.save(f"{prefix}{s // per}.jpg", quality=88)
    print(f"{prefix}{s // per}.jpg")
