import json, os, re
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, "harness.json"), encoding="utf-8"))
pat = re.compile(r"general ([\d.e+-]+) \((\d+) of (\d+) over 2e-3.*?\); z=0 ([\d.e+-]+) \((\d+) over\), leaves plane by ([\d.e+-]+); y=0 ([\d.e+-]+) \((\d+) of 256 over\)(.*)")
for k, rows in d.items():
    if isinstance(rows, str): print(k, rows); continue
    W = dict(gen=0, over=0, z0=0, z0over=0, leak=0, y0=0, y0over=0); bad = []
    for t, r in rows.items():
        m = pat.match(r)
        if not m: print("  ?", t, r); continue
        g, ov, n, z0, z0o, leak, y0, y0o, rest = m.groups()
        g, z0, leak, y0 = float(g), float(z0), float(leak), float(y0); ov, z0o, y0o = int(ov), int(z0o), int(y0o)
        W["gen"] = max(W["gen"], g); W["over"] += ov; W["z0"] = max(W["z0"], z0); W["z0over"] += z0o; W["y0"] = max(W["y0"], y0); W["y0over"] += y0o
        if "cmap" not in t and not (k == "pillow" and '"layout": 1' in t.replace('":', '": ')): W["leak"] = max(W["leak"], leak)
        if ov or z0o or y0o or rest.strip(): bad.append("    %s -> %s" % (t, r))
    print("%-9s %3d runs: general points worst %.1e, over 2e-3: %d;  z=0 points worst %.1e, over: %d, leak out of the plane (pw, sqr) %.1e;  y=0 points worst %.1e, over: %d" % (k, len(rows), W["gen"], W["over"], W["z0"], W["z0over"], W["leak"], W["y0"], W["y0over"]))
    for b in bad[:14]: print(b[:420])
    if len(bad) > 14: print("    ... %d rows in all" % len(bad))
