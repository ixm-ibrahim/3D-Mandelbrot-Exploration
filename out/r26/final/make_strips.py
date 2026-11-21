"""The final look: the four pictures for the user, put together from screenshots of the real page.

  python out/r26/final/make_strips.py

Reads out/r26/final/strip/*.png (taken by strips.js at 1100x1000 and strips_both.js at 1400x950: each one the stage
of dist/r26-final.html, clip #stage) and writes

  out/r26/final/user-a-circle-to-mandelbrot-2d.png     six screenshots: Mandelbrot shape, 2D, steps 0, 1, 2, 3, 5, 16
  out/r26/final/user-b-ball-to-mandelbrot-3d.png       the same in 3D
  out/r26/final/user-c-both-rabbit-2d.png              Both in 2D for the rabbit, steps 0, 2, 5, 16
  out/r26/final/user-d-julia-ball-3d.png               Julia shape in 3D for c = -1, steps 0, 2, 5, 16

Nothing is drawn into a screenshot. Each is cut at the bottom just above the stage's hint line (the same line in
every one: 30 pixels of 550, or 33 of 513 for the pairs), set side by side in reading order, and one or two sentences are written underneath.
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
STRIP = os.path.join(HERE, "strip")
BG = (8, 12, 17)          # the stage colour of the dark theme (--stage: #080c11)
INK = (226, 232, 238)     # --ink
GAP = 10


def font(px):
    for name in ("segoeui.ttf", "arial.ttf"):
        p = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, px)
    return ImageFont.load_default()


def wrap(d, text, f, width):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if d.textlength(t, font=f) <= width or not cur:
                cur = t
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    return lines


def sheet(out, names, cols, cut_bottom, caption, scale=1.0):
    tiles = []
    for n in names:
        im = Image.open(os.path.join(STRIP, n)).convert("RGB")
        im = im.crop((0, 0, im.width, im.height - cut_bottom))
        if scale != 1.0:
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
        tiles.append(im)
    tw, th = tiles[0].size
    rows = (len(tiles) + cols - 1) // cols
    W = cols * tw + (cols + 1) * GAP
    f = font(max(22, round(W / 62)))
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lines = wrap(probe, caption, f, W - 2 * GAP - 20)
    lh = round(f.size * 1.42)
    cap_h = len(lines) * lh + 34
    H = rows * th + (rows + 1) * GAP + cap_h
    big = Image.new("RGB", (W, H), BG)
    for i, im in enumerate(tiles):
        big.paste(im, (GAP + (i % cols) * (tw + GAP), GAP + (i // cols) * (th + GAP)))
    d = ImageDraw.Draw(big)
    y = rows * th + (rows + 1) * GAP + 10
    for ln in lines:
        d.text((GAP + 10, y), ln, font=f, fill=INK)
        y += lh
    big.save(os.path.join(HERE, out))
    print("wrote out/r26/final/%s  %d x %d  (%d screenshots of %d x %d, %d lines of words)" % (out, W, H, len(tiles), tw, th, len(lines)))


def main():
    cut1 = int(os.environ.get("CUT_SINGLE", "30"))
    cut2 = int(os.environ.get("CUT_BOTH", "33"))
    sheet("user-a-circle-to-mandelbrot-2d.png", ["a-2d-m-%02d.png" % i for i in range(6)], 3, cut1,
          "Each step throws out the points that have just landed outside the big circle; the first step throws out none. "
          "The start, then what is left after 1, 2, 3, 5 and 16 steps: after endlessly many steps this becomes the Mandelbrot set.")
    sheet("user-b-ball-to-mandelbrot-3d.png", ["b-3d-m-%02d.png" % i for i in range(6)], 3, cut1,
          "The same in 3D: a see-through ball at the start, then what is left of it after 1, 2, 3, 5 and 16 steps. "
          "The grey glass round the shape is the shape one step before.")
    sheet("user-c-both-rabbit-2d.png", ["c-2d-both-%02d.png" % i for i in range(4)], 2, cut2,
          "Left the Mandelbrot shape with the diamond at c, right the Julia shape for that c, here the rabbit. "
          "The start, then what is left after 2, 5 and 16 steps.")
    sheet("user-d-julia-ball-3d.png", ["d-3d-j-%02d.png" % i for i in range(4)], 2, cut1,
          "The Julia shape in 3D for c at x \u22121, y 0 (the basilica): the big ball at the start, "
          "then what is left after 2, 5 and 16 steps.")


if __name__ == "__main__":
    main()
