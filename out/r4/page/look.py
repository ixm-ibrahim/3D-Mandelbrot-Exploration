"""Write the action lists for the look-over screenshots and run them: python out/r4/page/look.py <tag> <size> <theme> [url]"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
tag, size, theme = sys.argv[1], sys.argv[2], sys.argv[3]
url = sys.argv[4] if len(sys.argv) > 4 else 'dist/r4-page.html'
out = 'out/r4/page/look-%s-' % tag
pre = "const L = window.squaringLab, $ = id => document.getElementById(id); const sleep = ms => new Promise(r => setTimeout(r, ms)); const top = sel => { const e = document.querySelector(sel); window.scrollTo(0, e.getBoundingClientRect().top + window.scrollY - 4); }; "
acts = [
    {"js": pre + "L.R.warmOn = false; L.S.q.aa = 2; L.touch(); document.querySelectorAll('details.sec').forEach(d => { d.open = true; }); top('.dials'); await sleep(200); return [document.documentElement.scrollWidth, window.innerWidth, document.querySelector('.dials').getBoundingClientRect().height];", "wait": "done", "timeout": 300, "shot": out + "m-top.png"},
    {"js": pre + "top('#secEq'); await sleep(200); return 1;", "shot": out + "m-eq.png"},
    {"js": pre + "top('#secColour'); await sleep(200); return 1;", "shot": out + "m-colour.png"},
    {"js": pre + "top('#secQuality'); await sleep(200); return 1;", "shot": out + "m-quality.png"},
    {"js": pre + "$('mode-j').click(); await sleep(300); top('.dials'); await sleep(200); return 1;", "wait": "done", "timeout": 300, "shot": out + "j-top.png"},
    {"js": pre + "$('mode-k').click(); await sleep(300); top('.dials'); await sleep(200); return 1;", "wait": "done", "timeout": 300, "shot": out + "k-top.png"},
    {"js": pre + "$('mode-m').click(); await sleep(300); top('footer.why'); await sleep(200); return 1;", "shot": out + "footer.png"},
    {"js": pre + "top('.lower'); await sleep(200); return 1;", "wait": "done", "timeout": 300, "shot": out + "lower.png"},
]
path = os.path.join(ROOT, 'out', 'r4', 'page', 'look-%s.json' % tag)
json.dump(acts, open(path, 'w', encoding='utf-8'), indent=1)
env = dict(os.environ, PYTHONIOENCODING='utf-8')
sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', url, '--size', size, '--theme', theme, '--actions', path], cwd=ROOT, env=env))
