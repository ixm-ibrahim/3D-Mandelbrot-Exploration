"""Classic Julia constants for z^2 + c: derive the ones that have a definition, and check every one.

  python notes/julia_classics.py            prints a table
  python notes/julia_classics.py --json     prints the same facts as JSON (used by notes/julia_build.py)

Derived values
  centre of a period-p part of the Mandelbrot set: the c for which 0 comes back to 0 after p steps,
      found by Newton's method on g(c) = f_c^p(0), with g' carried along by d -> 2 z d + 1.
  a point of the main cardioid with rotation number t: c = L/2 - L^2/4 with L = exp(2 pi i t)
      (the fixed point of z^2 + c then has multiplier L). t = golden mean gives the Siegel disc,
      t = 1/3 the root of the rabbit's part ("fat rabbit"), t = 1/2 gives -3/4 and t = 0 gives 1/4.

Check, for every constant: follow the critical orbit (the orbit of 0). Either it escapes (the Julia set is
dust; the step at which it passes |z| = 2 says how thick the dust looks), or it settles on a cycle
(we report its period and the size of its multiplier: 0 = centre, below 1 = attracting, 1 = parabolic),
or it does neither (Siegel disc, or a dendrite whose critical orbit lands on a repelling cycle).
"""
import cmath, json, math, sys

PHI = (1 + math.sqrt(5)) / 2


def centre(c0, p, steps=60):
    c = complex(c0)
    for _ in range(steps):
        z, d = 0j, 0j
        for _ in range(p):
            d = 2 * z * d + 1
            z = z * z + c
        if d == 0:
            break
        c -= z / d
    z = 0j
    for _ in range(p):
        z = z * z + c
    return c, abs(z)


def cardioid(t):
    L = cmath.exp(2j * math.pi * t)
    return L / 2 - L * L / 4


def classify(c, burn=400000, maxp=600):
    """-> dict(kind=..., ...) describing the critical orbit of z^2 + c."""
    z = 0j
    for k in range(1, 20001):
        z = z * z + c
        if abs(z) > 2:
            return {"kind": "escapes", "step": k}
    for _ in range(burn):
        z = z * z + c
    orbit = [z]
    for _ in range(2 * maxp):
        orbit.append(orbit[-1] * orbit[-1] + c)
    best = None
    for p in range(1, maxp + 1):
        err = max(abs(orbit[i + p] - orbit[i]) for i in range(0, maxp, max(1, maxp // 8)))
        if err < 1e-7:
            best = p
            break
    if best is None:
        return {"kind": "bounded, no cycle found"}
    mult = 1 + 0j
    for i in range(best):
        mult *= 2 * orbit[i]
    return {"kind": "cycle", "period": best, "multiplier": abs(mult)}


def table():
    rabbit, e1 = centre(-0.12 + 0.75j, 3)
    airplane, e2 = centre(-1.75, 3)
    kokopelli, e3 = centre(-0.16 + 1.03j, 4)
    siegel = cardioid((math.sqrt(5) - 1) / 2)
    fat_rabbit = cardioid(1 / 3)
    rows = [
        # key, value, how we know it
        ("basilica", -1 + 0j, "classic: centre of the period-2 disc"),
        ("san marco", -0.75 + 0j, "classic: where the period-2 disc touches the cardioid (cardioid point with t = 1/2: %s)" % fmt(cardioid(0.5))),
        ("cauliflower", 0.25 + 0j, "classic: the cusp of the cardioid (cardioid point with t = 0: %s)" % fmt(cardioid(0.0))),
        ("airplane", airplane, "computed: real period-3 centre, Newton from -1.75, residual %.1e" % e2),
        ("golden ratio", (1 - PHI) + 0j, "classic: c = 1 - phi"),
        ("feigenbaum", -1.401155189092 + 0j, "classic: the limit of the period doublings on the real axis"),
        ("0.285", 0.285 + 0j, "classic, frequently shown"),
        ("rabbit", rabbit, "computed: period-3 centre, Newton from -0.12 + 0.75i, residual %.1e" % e1),
        ("fat rabbit", fat_rabbit, "computed: cardioid point with t = 1/3, the root of the rabbit's part"),
        ("siegel", siegel, "computed: cardioid point with t = golden mean (sqrt 5 - 1)/2"),
        ("dendrite", 1j, "classic: c = i"),
        ("kokopelli", kokopelli, "computed: period-4 centre, Newton from -0.16 + 1.03i, residual %.1e" % e3),
        ("-0.8+0.156i", -0.8 + 0.156j, "classic, frequently shown"),
        ("0.285+0.01i", 0.285 + 0.01j, "classic, frequently shown"),
        ("-0.4+0.6i", -0.4 + 0.6j, "classic, frequently shown"),
        ("-0.70176-0.3842i", -0.70176 - 0.3842j, "classic, frequently shown"),
        ("-0.835-0.2321i", -0.835 - 0.2321j, "classic, frequently shown"),
        ("-0.7269+0.1889i", -0.7269 + 0.1889j, "classic, frequently shown"),
        ("0.45+0.1428i", 0.45 + 0.1428j, "classic, frequently shown"),
        ("phi-2 + (phi-1)i", (PHI - 2) + (PHI - 1) * 1j, "classic, frequently shown"),
        ("segment", -2 + 0j, "classic: the tip of the Mandelbrot set; the Julia set is the segment from -2 to 2"),
    ]
    out = []
    for key, c, how in rows:
        info = classify(c)
        out.append({"key": key, "c": [c.real, c.imag], "how": how, **info})
    return out


def fmt(c):
    return "%.12g %s %.12gi" % (c.real, "+" if c.imag >= 0 else "-", abs(c.imag))


def main():
    rows = table()
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return
    # the airplane and the rabbit are both roots of c^3 + 2c^2 + c + 1 (period-3 centres)
    for r in rows:
        c = complex(*r["c"])
        if r["kind"] == "escapes":
            what = "critical orbit escapes at step %d" % r["step"]
        elif r["kind"] == "cycle":
            what = "cycle of period %d, |multiplier| = %.6f" % (r["period"], r["multiplier"])
        else:
            what = r["kind"]
        print("%-18s c = %-36s %s\n%18s   %s" % (r["key"], fmt(c), what, "", r["how"]))
    c = complex(*next(r for r in rows if r["key"] == "rabbit")["c"])
    print("check: rabbit in c^3 + 2c^2 + c + 1 ->", abs(c ** 3 + 2 * c ** 2 + c + 1))
    c = complex(*next(r for r in rows if r["key"] == "airplane")["c"])
    print("check: airplane in c^3 + 2c^2 + c + 1 ->", abs(c ** 3 + 2 * c ** 2 + c + 1))
    c = complex(*next(r for r in rows if r["key"] == "kokopelli")["c"])
    print("check: kokopelli in c^6 + 3c^5 + 3c^4 + 3c^3 + 2c^2 + 1 ->", abs(c ** 6 + 3 * c ** 5 + 3 * c ** 4 + 3 * c ** 3 + 2 * c ** 2 + 1))
    c = complex(*next(r for r in rows if r["key"] == "siegel")["c"])
    z = (1 - cmath.sqrt(1 - 4 * c)) / 2
    print("check: Siegel fixed point multiplier 2z = %s, |2z| = %.15f, angle/2pi = %.12f (golden mean %.12f)"
          % (fmt(2 * z), abs(2 * z), (cmath.phase(2 * z) / (2 * math.pi)) % 1, (math.sqrt(5) - 1) / 2))
    c = complex(*next(r for r in rows if r["key"] == "dendrite")["c"])
    z, seen = 0j, []
    for _ in range(6):
        z = z * z + c
        seen.append(fmt(z))
    print("check: critical orbit of c = i:", " -> ".join(seen))


if __name__ == "__main__":
    main()
