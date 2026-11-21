import sys, os
from PIL import Image, ImageDraw
def sheet(out, paths, cols=4, w=460, labels=None):
    ims = []
    for p in paths:
        if not os.path.exists(p): continue
        im = Image.open(p).convert("RGB"); h = int(im.height * w / im.width); ims.append((p, im.resize((w, h), Image.LANCZOS)))
    if not ims: print("none"); return
    h = max(i.height for _, i in ims); rows = (len(ims) + cols - 1) // cols
    S = Image.new("RGB", (cols * w, rows * (h + 18)), (30, 30, 30)); d = ImageDraw.Draw(S)
    for k, (p, im) in enumerate(ims):
        x, y = (k % cols) * w, (k // cols) * (h + 18)
        S.paste(im, (x, y + 18)); d.text((x + 4, y + 3), os.path.basename(p)[:-4], fill=(255, 255, 120))
    S.save(out); print(out, S.size)
if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[3:], cols=int(sys.argv[2]))
