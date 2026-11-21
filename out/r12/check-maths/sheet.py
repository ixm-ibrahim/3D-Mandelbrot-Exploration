import os
from PIL import Image, ImageDraw
here = os.path.dirname(os.path.abspath(__file__))
rows = ["rough-50-250", "rough-35-300", "smooth-50-100"]; cols = [14, 60, 250]
tw, th = 560, 456
sheet = Image.new("RGB", (tw * 3, th * 3), (0, 0, 0)); d = ImageDraw.Draw(sheet)
for r, name in enumerate(rows):
    for c, it in enumerate(cols):
        im = Image.open(os.path.join(here, "skin-%s-iter%d.png" % (name, it))).convert("RGB").resize((tw, th))
        sheet.paste(im, (c * tw, r * th)); d.text((c * tw + 8, r * th + th - 16), "%s, %d iterations" % (name, it), fill=(255, 255, 255))
sheet.save(os.path.join(here, "sheet-skin.png"))
