# Cuts the trophy out of its museum background with rembg; writes RGBA previews on a dark slate.
import sys
from PIL import Image
from rembg import remove, new_session
src, dst = sys.argv[1], sys.argv[2]
for model in ["isnet-general-use", "u2net"]:
    sess = new_session(model)
    for name in ["cr7_2016", "campnou"]:
        im = Image.open(f"{src}/{name}.jpg").convert("RGB"); im.thumbnail((1400, 1800))
        cut = remove(im, session=sess, post_process_mask=True)
        cut = cut.crop(cut.getbbox())
        cut.save(f"{dst}/{name}_{model}.png")
        prev = Image.new("RGBA", cut.size, (18, 24, 30, 255)); prev.alpha_composite(cut)
        prev.convert("RGB").resize((cut.width * 600 // cut.height, 600)).save(f"{dst}/{name}_{model}_prev.jpg")
        print(name, model, cut.size)
