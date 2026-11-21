"""Compare screenshots numerically, so a regression check does not depend on eyeballing two pictures.

  python notes/shaders_diff.py a.png b.png [c.png d.png ...]     pairs: mean absolute difference and share of pixels that differ
  python notes/shaders_diff.py --stats a.png [b.png ...]         one picture: share of pixels that are not background, mean brightness

Reads 8-bit RGB/RGBA PNGs with the standard library only.
"""
import struct, sys, zlib
import numpy as np


def read_png(path):
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    pos, idat, w = 8, b"", None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR":
            w, h, depth, ctype = struct.unpack(">IIBB", body[:10])
            assert depth == 8 and ctype in (2, 6), "only 8-bit RGB(A)"
            ch = 3 if ctype == 2 else 4
        elif kind == b"IDAT":
            idat += body
        pos += 12 + n
    raw = np.frombuffer(zlib.decompress(idat), dtype=np.uint8).reshape(h, 1 + w * ch)
    out = np.zeros((h, w * ch), dtype=np.int32)
    prev = np.zeros(w * ch, dtype=np.int32)
    for y in range(h):
        ft, line = int(raw[y, 0]), raw[y, 1:].astype(np.int32)
        if ft == 0:
            cur = line
        elif ft == 2:
            cur = (line + prev) & 255
        else:
            cur = np.zeros(w * ch, dtype=np.int32)
            for x in range(w * ch):
                a = cur[x - ch] if x >= ch else 0
                b = prev[x]
                c = prev[x - ch] if x >= ch else 0
                if ft == 1:
                    pr = a
                elif ft == 3:
                    pr = (a + b) >> 1
                else:
                    pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                    pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[x] = (line[x] + pr) & 255
        out[y] = cur
        prev = cur
    return out.reshape(h, w, ch)[:, :, :3]


def main():
    args = sys.argv[1:]
    if args and args[0] == "--stats":
        for p in args[1:]:
            im = read_png(p)
            bg = im[4, 4]
            solid = (np.abs(im - bg).sum(axis=2) > 24).mean()
            print("%s: %dx%d, %.1f%% not background, mean brightness %.1f" % (p, im.shape[1], im.shape[0], 100 * solid, im.mean()))
        return
    for a, b in zip(args[0::2], args[1::2]):
        x, y = read_png(a), read_png(b)
        if x.shape != y.shape:
            print("%s vs %s: sizes differ %s %s" % (a, b, x.shape, y.shape))
            continue
        d = np.abs(x - y)
        print("%s vs %s: mean abs diff %.2f, %.1f%% of pixels differ by more than 24" % (a, b, d.mean(), 100 * (d.max(axis=2) > 24).mean()))


if __name__ == "__main__":
    main()
