import json, sys, time, io, urllib.request
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")
UA = {"User-Agent": "GameStateReel/1.0 (https://www.youtube.com/@GameState365) python-urllib"}
d = json.load(open(sys.argv[1], encoding="utf-8"))
pats = [l.strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()]
sel = [k for p in pats for k in d if p in k]
sel = list(dict.fromkeys(sel))
cw, ch, cols = 300, 400, 6
rows = (len(sel) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw, rows * (ch + 24)), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
for i, k in enumerate(sel):
    th = d[k][4]
    for a in range(5):
        try:
            time.sleep(0.5)
            data = urllib.request.urlopen(urllib.request.Request(th, headers=UA)).read(); break
        except Exception as e:
            time.sleep(4 * (a + 1))
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((cw, ch))
    x, y = (i % cols) * cw, (i // cols) * (ch + 24)
    sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
    dr.text((x + 4, y + ch + 4), f"{i}", fill=(200, 255, 60))
    print(i, k)
sheet.save(sys.argv[3], quality=85)
