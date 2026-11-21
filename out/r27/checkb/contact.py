"""Put several screenshots side by side with their names, for looking at many at once.

  python out/r27/checkb/contact.py OUT.png COLS TILEWIDTH file1.png file2.png ...
Paths are relative to out/r27/checkb/shots/ unless they contain a slash.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    files = sys.argv[4:]
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    tiles = []
    for f in files:
        p = f if ("/" in f or "\\" in f) else os.path.join(HERE, "shots", f)
        im = Image.open(p).convert("RGB")
        th = round(im.height * tw / im.width)
        tiles.append((os.path.basename(f), im.resize((tw, th), Image.LANCZOS)))
    th = max(t[1].height for t in tiles)
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 8) + 8, rows * (th + 30) + 8), (40, 40, 40))
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(tiles):
        x, y = 8 + (i % cols) * (tw + 8), 8 + (i // cols) * (th + 30)
        d.text((x, y), name.replace(".png", ""), fill=(255, 255, 255), font=font)
        sheet.paste(im, (x, y + 20))
    p = out if ("/" in out or "\\" in out) else os.path.join(HERE, "shots", out)
    sheet.save(p)
    print("wrote", p, sheet.size)


if __name__ == "__main__":
    main()
