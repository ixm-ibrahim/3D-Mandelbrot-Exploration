"""Write an actions file for tools/shot.py from a short list and run it.
usage: python out/fix/shaders/mk.py <page-name> <tag> <scenario> [size]
Scenarios are defined below; screenshots go to out/fix/shaders/<tag>-<step>.png"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PRE = "const L = window.squaringLab, $ = id => document.getElementById(id); L.R.warmOn = false; const jul = n => { $('mode-j').click(); [...document.querySelectorAll('#juliaList .plist-item')].find(x => x.textContent === n).click(); }; const Q = (id, o) => { $(id).click(); Object.assign(L.S.q, o || {}); L.syncControls(); L.touch(); }; const type = (id, v) => { const e = $(id); e.value = v; e.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); }; const T0 = performance.now(); const fin = async () => { while (!L.idle()) await new Promise(r => setTimeout(r, 30)); return Math.round(performance.now() - T0); };"
SC = {
 'rabbit': [
  ('bal-rough', "jul('Douady rabbit'); Q('qBal', {de: 0, aa: 4});"),
  ('fast-rough', "Q('qFast', {de: 0});"),
  ('ultra', "Q('qUltra');"),
  ('bal', "Q('qBal', {aa: 4});"),
  ('fine', "Q('qFine', {aa: 4});"),
  ('fine-close', "L.cam.dist = 2.2; Q('qFine', {aa: 4});"),
  ('bal-close', "Q('qBal', {aa: 4});"),
  ('bal-rough-close', "Q('qBal', {aa: 4, de: 0});"),
 ],
}
def main():
    page, tag, sc = sys.argv[1], sys.argv[2], sys.argv[3]
    size = sys.argv[4] if len(sys.argv) > 4 else '1100x800'
    acts = []
    for name, js in SC[sc]:
        acts.append({"js": PRE + js + " return '" + name + " ' + await fin() + ' ms';", "wait": "done", "timeout": 400,
                     "shot": "out/fix/shaders/%s-%s.png" % (tag, name), "clip": "#stage"})
    path = os.path.join(ROOT, 'out', 'fix', 'shaders', '_%s-%s.json' % (tag, sc))
    json.dump(acts, open(path, 'w'), indent=1)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    sys.exit(subprocess.call([sys.executable, os.path.join(ROOT, 'tools', 'shot.py'), '--url', 'dist/%s.html' % page, '--size', size, '--actions', path], env=env, cwd=ROOT))
if __name__ == '__main__':
    main()
