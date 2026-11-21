"""Round 26, the fixer: one picture per visible defect, the page as joined on the left (or above), the mended page
beside it. Reads the pictures the lists defects.js, defects_phone.js and panel.js took (before-*.png, after-*.png)
and writes out/r26/fix/pair-<defect>.png.

  python out/r26/fix/pairs.py
"""
import os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))

# defect -> rows of (before, after), with an optional crop (x, y, w, h) and a scale
PAIRS = {
    "W1-first-half-second": [("before-W1-half-second-in", "after-W1-half-second-in", (40, 115, 800, 560), 1.0)],
    "W2-M12-panel-words-2d": [("before-panel-2d-both", "after-panel-2d-both", None, 1.0)],
    "M12-panel-words-3d": [("before-panel-3d-julia", "after-panel-3d-julia", None, 1.0)],
    "M3-M4-3d-julia-hint": [("before-panel-3d-julia-stage", "after-panel-3d-julia-stage", None, 0.9)],
    "E1-step-1-in-3d": [("before-E1-3d-both-00.4", "after-E1-3d-both-00.4", None, 0.9), ("before-E1-3d-m-00.4", "after-E1-3d-m-00.4", None, 0.9),
                        ("before-light-E1-3d-both-00.4", "after-light-E1-3d-both-00.4", None, 0.9)],
    "E2-a-step-under-way-in-3d": [("before-E2-3d-m-02.15", "after-E2-3d-m-02.15", None, 0.7), ("before-E2-3d-m-02.4", "after-E2-3d-m-02.4", None, 0.7),
                                  ("before-E2-3d-m-02.7", "after-E2-3d-m-02.7", None, 0.7), ("before-E2-3d-m-06.4", "after-E2-3d-m-06.4", None, 0.7),
                                  ("before-light-E2-3d-m-02.4", "after-light-E2-3d-m-02.4", None, 0.7), ("before-light-E2-3d-m-06.4", "after-light-E2-3d-m-06.4", None, 0.7)],
    "A1-nothing-left-in-3d": [("before-A1-power1-3d-j-12", "after-A1-power1-3d-j-12", (40, 115, 800, 560), 1.0), ("before-A1-c7-3d-j-02", "after-A1-c7-3d-j-02", (40, 115, 800, 560), 1.0)],
    "A2-4d-slice-words": [("before-A2-quat4-w1.5-m-00.5", "after-A2-quat4-w1.5-m-00.5", (40, 115, 800, 560), 1.0), ("before-A2-quat4-w1.5-j-00", "after-A2-quat4-w1.5-j-00", (40, 115, 800, 560), 1.0)],
    "A5-lone-letter-c": [("before-A5-3d-zoomed-lone-c", "after-A5-3d-zoomed-lone-c", None, 0.9)],
    "M1-late-step-2d": [("before-M1-2d-m-12.4", "after-M1-2d-m-12.4", (40, 115, 800, 560), 1.0)],
    "M1-late-step-3d": [("before-M1-3d-m-12.4", "after-M1-3d-m-12.4", (40, 115, 800, 560), 1.0)],
    "M2-step-16-rough-approaches": [("before-M2-turnalong-16", "after-M2-turnalong-16", (231, 80, 400, 350), 1.6), ("before-M2-fold-16", "after-M2-fold-16", (231, 80, 400, 350), 1.6),
                                    ("before-M2-lathe-16", "after-M2-lathe-16", (231, 80, 400, 350), 1.6), ("before-M2-bulb-16", "after-M2-bulb-16", (231, 80, 400, 350), 1.6)],
    "M5-M7-phone-rows": [("before-phone-M5-after-the-tap", "after-phone-M5-after-the-tap", (0, 0, 390, 640), 1.5)],
    "M6-phone-both": [("before-phone-M6-2d-both-00", "after-phone-M6-2d-both-00", None, 2.0), ("before-phone-M6-2d-both-16", "after-phone-M6-2d-both-16", None, 2.0),
                      ("before-phone-M6-3d-both-05-zoomed", "after-phone-M6-3d-both-05-zoomed", None, 2.0)],
    "M8-axis-numbers": [("before-M8-2d-m-16", "after-M8-2d-m-16", (330, 95, 200, 320), 3.0)],
    "M9-both-names": [("before-M9-2d-both-05", "after-M9-2d-both-05", None, 0.9)],
    "M10-sentence-and-label": [("before-M10-2d-m-00", "after-M10-2d-m-00", (40, 440, 800, 130), 1.0)],
    "M11-3d-as-it-opens": [("before-M11-3d-m-05", "after-M11-3d-m-05", None, 0.8), ("before-M11-3d-m-16", "after-M11-3d-m-16", (50, 127, 862, 511), 0.8)],
}


def load(name, crop, scale):
    im = Image.open(os.path.join(HERE, name + ".png")).convert("RGB")
    if crop:
        im = im.crop((crop[0], crop[1], crop[0] + crop[2], crop[1] + crop[3]))
    return im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)


def main():
    for tag, rows in PAIRS.items():
        tiles, missing = [], []
        for b, a, crop, scale in rows:
            for n in (b, a):
                if not os.path.exists(os.path.join(HERE, n + ".png")):
                    missing.append(n)
            if not missing:
                tiles.append((b, load(b, crop, scale), a, load(a, crop, scale)))
        if missing:
            print("%s: MISSING %s" % (tag, ", ".join(missing))); continue
        bar, gap = 18, 6
        w = max(t[1].width + t[3].width for t in tiles) + 3 * gap
        h = sum(max(t[1].height, t[3].height) + bar + gap for t in tiles) + gap
        big = Image.new("RGB", (w, h), (128, 128, 128))
        d = ImageDraw.Draw(big)
        y = gap
        for b, bi, a, ai in tiles:
            x = gap
            for name, im in ((b, bi), (a, ai)):
                d.rectangle([x, y, x + im.width, y + bar], fill=(255, 255, 255))
                d.text((x + 3, y + 3), ("AS JOINED: " if name.startswith("before") else "MENDED: ") + name + ".png", fill=(0, 0, 0))
                big.paste(im, (x, y + bar))
                x += im.width + gap
            y += max(bi.height, ai.height) + bar + gap
        big.save(os.path.join(HERE, "pair-%s.png" % tag))
        print("wrote out/r26/fix/pair-%s.png (%d x %d)" % (tag, big.width, big.height))


if __name__ == "__main__":
    main()
