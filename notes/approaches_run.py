"""Run page JavaScript through tools/shot.py and save what it returns as readable UTF-8 text.

  python notes/approaches_run.py <url> <out.txt> "<javascript>"        one step
  python notes/approaches_run.py <url> <out.txt> --actions steps.json  several steps

shot.py prints each step's return value as one JSON string; on a Windows console that cannot show the
maths glyphs. This wrapper captures the output, decodes those strings and writes plain text.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
url, out, rest = sys.argv[1], sys.argv[2], sys.argv[3:]
cmd = [sys.executable, os.path.join(ROOT, "tools", "shot.py"), "--url", url]
cmd += rest if rest[0] == "--actions" else ["--js", rest[0]] + rest[1:]
env = dict(os.environ, PYTHONIOENCODING="utf-8")
p = subprocess.run(cmd, capture_output=True, env=env, cwd=ROOT)
text = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
lines = []
for line in text.splitlines():
    m = re.match(r"(step \d+ result: )(\".*\")$", line)
    if m:
        try:
            lines.append(m.group(1)); lines.append(json.loads(m.group(2))); continue
        except ValueError:
            pass
    lines.append(line)
with open(os.path.join(ROOT, out), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("exit code %d, wrote %s (%d lines)" % (p.returncode, out, sum(l.count("\n") + 1 for l in lines)))
sys.exit(p.returncode)
