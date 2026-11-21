import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair.js")
s = io.open(p, encoding="utf-8").read()
i = s.index("// every pair of entries in Julia mode")
s = s[:i] + "return out.join('\n');\n"
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
