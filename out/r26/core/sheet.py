"""Put pictures side by side on one sheet, each with its file name over it.
  python out/r26/core/sheet.py OUT.png COLUMNS SCALE picture1.png picture2.png ...   (paths relative to out/r26/core/)
"""
import os, sys
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out, cols, scale = sys.argv[1], int(sys.argv[2]), float(sys.argv[3])
    names = sys.argv[4:]
    ims = []
    for n in names:
        im = Image.open(os.path.join(HERE, n)).convert("RGB")
        if scale != 1:
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        ims.append(im)
    w = max(i.width for i in ims); h = max(i.height for i in ims) + 16
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w + (cols + 1) * 6, rows * h + (rows + 1) * 6), (40, 40, 44))
    d = ImageDraw.Draw(sheet)
    for k, im in enumerate(ims):
        x = 6 + (k % cols) * (w + 6); y = 6 + (k // cols) * (h + 6)
        d.text((x + 2, y + 2), names[k], fill=(230, 230, 230))
        sheet.paste(im, (x, y + 16))
    sheet.save(os.path.join(HERE, out))
    print("wrote", out, sheet.size)


if __name__ == "__main__":
    main()
