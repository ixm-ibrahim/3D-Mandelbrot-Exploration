"""Compare two PNG files pixel by pixel (no extra packages: a small PNG reader for 8-bit RGB/RGBA, no interlace)."""
import sys, zlib, struct, hashlib

def read(path):
    with open(path, "rb") as f:
        data = f.read()
    pos, chunks, head = 8, [], None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        if kind == b"IHDR": head = struct.unpack(">IIBBBBB", body)
        if kind == b"IDAT": chunks.append(body)
        pos += 12 + n
    w, h, depth, ctype = head[0], head[1], head[2], head[3]
    bpp = {2: 3, 6: 4}[ctype]
    raw = zlib.decompress(b"".join(chunks))
    stride, out, prev = w * bpp, bytearray(), bytearray(w * bpp)
    for y in range(h):
        ft = raw[y * (stride + 1)]
        line = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if ft == 1: line[i] = (line[i] + a) & 255
            elif ft == 2: line[i] = (line[i] + b) & 255
            elif ft == 3: line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif ft == 4:
                p = a + b - c; pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        out += line; prev = line
    return w, h, bpp, bytes(out)

a, b = read(sys.argv[1]), read(sys.argv[2])
print("sizes", a[:3], b[:3])
if a[:3] != b[:3]:
    print("DIFFERENT SIZE"); sys.exit(1)
diff = sum(1 for i in range(0, len(a[3]), a[2]) if a[3][i:i + 3] != b[3][i:i + 3])
big = max((abs(x - y) for x, y in zip(a[3], b[3])), default=0)
print("pixels that differ:", diff, "of", a[0] * a[1], "| largest channel difference:", big)
print("sha", hashlib.sha1(a[3]).hexdigest()[:12], hashlib.sha1(b[3]).hexdigest()[:12])
