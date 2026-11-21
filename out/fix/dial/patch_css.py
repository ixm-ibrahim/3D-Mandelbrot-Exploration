"""One-off edit of src/css/70-dial.css for the fix round (kept for the record; it refuses to run twice)."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, "src", "css", "70-dial.css")
s = io.open(p, encoding="utf-8").read()
old = "/* play: sweeps the value */\n"
new = ("/* extreme values are on and this dial has its wider range: a small tag in front of the box cluster */\n"
       ".dial-wide {\n"
       "  flex: none; align-self: center; font-family: var(--f-cond); font-weight: 600; font-size: 10.5px; line-height: 1;\n"
       "  letter-spacing: .09em; text-transform: uppercase; color: var(--brass); cursor: default; user-select: none; -webkit-user-select: none;\n"
       "}\n"
       ".dial-wide[hidden] { display: none; }\n\n")
assert s.count(old) == 1 and ".dial-wide" not in s
s = s.replace(old, new + old)
old2 = "  .dial-play { width: 34px; }\n"
assert s.count(old2) == 1
s = s.replace(old2, old2 + "  .dial-wide { font-size: 11.5px; }\n")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("css ok")
