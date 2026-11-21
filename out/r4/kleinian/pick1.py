"""First selection from cands.json (find.py): a spread of groups and kinds of centre, written to try1.json."""
import json

c = json.load(open("out/r4/kleinian/cands.json"))
want = [("0/1", (1, 1, 0.7)), ("0/1", (1, 0.45, 0)), ("0/1", (0.55, 1, 0)), ("0/1", (0.42, 0.5, 0.3)), ("0/1", (1, 0.3, 0.5)),
        ("0/1x3", (1, 1, 1)), ("0/1x3", (0, 1, 1)), ("0/1x3", (1, 1.55, 1)), ("0/1x3", (1, 0.5, 0)), ("0/1x3", (0.5, 1, 1)), ("0/1x3", (1, 1, 0.5)),
        ("1/2", (-1, 0.5774, 0.6)), ("1/2", (0, 1.1547, 0)), ("1/2", (0, 0.5774, 0.6)), ("1/2", (-1, 0.3, 0)), ("1/2", (0.8707, 0.2015, 0.0)),
        ("1/3x3", (0.2906, 0.8469, 1)), ("1/3", (-1.0, 0.4726, 0.0)), ("1/3", (-0.418, 1.2213, 0.0)), ("1/3", (0.997, 0.7236, 0.0)), ("1/3", (0.2906, 0.8469, 0.5)),
        ("1/4", (-1.0, 0.448, 0.0)), ("1/4", (0.3527, 0.6928, 0.0)), ("1/4", (-0.647, 1.2734, 0.5)),
        ("2/5", (-1.0, 0.3638, 0.0)), ("2/5", (0.6174, 0.8202, 0.0)), ("2/5", (1.3833, 0.8211, 0.5)),
        ("1/15", (0.9823, 0.4457, 0.0)), ("1/15", (-0.994, 0.9806, 0.0)), ("1/15", (-1, 0.4894, 0.5)),
        ("lean30", (1, 0.866, 0.5)), ("lean30", (0.851, 1.0582, 0.0)), ("lean30", (-0.3611, 1.1166, 0.0)),
        ("lean30x3", (0, 0.866, 1)), ("lean30x3", (1, 0.866, 0.5)), ("stretch", (1, 1, 2)), ("stretch", (0, 1, 2))]
out = []
for g, C in want:
    m = [x for x in c if x["group"] == g and abs(x["k"]["cx"] - C[0]) < 1e-3 and abs(x["k"]["cy"] - C[1]) < 1e-3 and abs(x["k"]["cz"] - C[2]) < 1e-3]
    if not m:
        print("not in the list (rejected by the model):", g, C)
        continue
    x = dict(m[0])
    three = x["k"]["three"]
    flat = C[2] == 0 and not three and x["k"]["mz"] == 0
    x["cam"] = dict(yaw=-1.35, pitch=1.0, dist=6.4) if flat else dict(yaw=0.5, pitch=0.45, dist=6.4) if three else dict(yaw=-1.2, pitch=0.6, dist=6.4)
    x["name"] = "%s %s" % (g, C)
    out.append(x)
json.dump(out, open("out/r4/kleinian/try1.json", "w"), indent=1)
print(len(out), "to render")
