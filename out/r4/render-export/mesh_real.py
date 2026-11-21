"""The 3D-model job run for real from the page, through the real takeSnapshot / sampleSlice (render-export, round 4).

  python out/r4/render-export/mesh_real.py [dist/r4-render-export.html]

Julia set for c = -1, the default Mandelbrot and the default Kleinian view, each at 128 cells, started with the
panel's own buttons. The zips come back through window.squaringLabSaveHook, are written to
out/r4/render-export/zips/ and read back with zipfile; the STL is parsed and checked with the mesh engineer's own
functions (out/r4/mesh/run_tests.py: read_stl, closed, pieces, volume).
"""
import base64, io, json, os, re, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, 'out', 'r4', 'mesh'))
import run_tests as M   # only its parsing and checking functions are used; nothing of theirs is written

PRE = r"""const L = window.squaringLab, $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const fail = m => { throw new Error(m); };
const tick = (id, on) => { const e = $(id); if (e.checked !== on) e.click(); };
window.got = window.got || [];
window.squaringLabSaveHook = (name, blob) => { window.got.push({ name, blob }); };
const b64 = async blob => { const u = new Uint8Array(await blob.arrayBuffer()); let s = ''; for (let i = 0; i < u.length; i += 0x8000) s += String.fromCharCode.apply(null, u.subarray(i, i + 0x8000)); return btoa(s); };
const model = async (stl, obj, ply) => {
  $('secMesh').open = true;
  if ($('meshDiscard').getBoundingClientRect().width > 0) $('meshDiscard').click();
  if ($('meshCells').options[$('meshCells').selectedIndex].text.indexOf('128') !== 0) fail('the panel does not start at 128 cells');
  tick('meshStl', stl); tick('meshObj', obj); tick('meshPly', ply);
  // count the calls the job makes, to report them
  const t0 = performance.now();
  $('meshStart').click();
  await sleep(20);
  if (!L.meshBusy()) fail('the model job did not start: ' + $('meshMsg').textContent);
  while (L.meshBusy()) await sleep(20);
  const ms = Math.round(performance.now() - t0);
  if (!($('meshSave').getBoundingClientRect().width > 0)) fail('the model job ended without a file: ' + $('meshMsg').textContent);
  const n = window.got.length; $('meshSave').click(); await sleep(300);
  const f = window.got[n]; if (!f) fail('Save the file handed nothing over');
  const facts = [...$('meshFacts').querySelectorAll('dt')].map(dt => dt.textContent + ': ' + dt.nextElementSibling.textContent);
  return { ms, facts, msg: $('meshMsg').textContent, name: f.name, b64: await b64(f.blob) };
};
"""

steps = [
    {"js": PRE + "L.R.warmOn = false; $('mode-j').click(); L.S.c = [-1, 0, 0]; L.S.q.aa = 2; L.syncControls(); L.refresh(false); return 'julia c = -1';", "wait": "done", "timeout": 300,
     "shot": "out/r4/render-export/mesh-julia-picture.png", "clip": "#stage"},
    {"js": PRE + "return await model(true, true, true);"},
    {"js": PRE + "$('mode-m').click(); L.syncControls(); L.refresh(false); return 'mandelbrot default';", "wait": "done", "timeout": 300},
    {"js": PRE + "return await model(true, false, false);"},
    {"js": PRE + "$('mode-k').click(); L.syncControls(); L.refresh(false); return 'kleinian default';", "wait": "done", "timeout": 300},
    {"js": PRE + "return await model(true, false, false);", "shot": "out/r4/render-export/mesh-panel-done.png", "clip": "#secMesh"},
]


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'dist/r4-render-export.html'
    path = os.path.join(HERE, 'mesh_real.steps.json')
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(steps, f)
    env = dict(os.environ, PYTHONIOENCODING='utf-8')
    r = subprocess.run([sys.executable, 'tools/shot.py', '--url', url, '--actions', path], cwd=ROOT, capture_output=True, text=True, encoding='utf-8', env=env)
    res = {}
    for line in (r.stdout + r.stderr).splitlines():
        m = re.match(r'step (\d+) result: (.*)$', line)
        if m: res[int(m.group(1))] = json.loads(m.group(2))
        else: print('   | ' + line[:300])
    print('   shot.py exit code %d' % r.returncode)
    os.makedirs(os.path.join(HERE, 'zips'), exist_ok=True)
    ok = r.returncode == 0
    for i, label in ((2, 'julia'), (4, 'mandelbrot'), (6, 'kleinian')):
        v = res.get(i)
        if not isinstance(v, dict):
            print('== %s: NO RESULT (%r)' % (label, v)); ok = False; continue
        raw = base64.b64decode(v['b64'])
        zpath = os.path.join(HERE, 'zips', label + '-' + v['name'])
        with open(zpath, 'wb') as f: f.write(raw)
        z = zipfile.ZipFile(zpath)
        bad = z.testzip()
        stl = next(n for n in z.namelist() if n.endswith('.stl'))
        pts, tris, badn = M.read_stl(z.read(stl))
        twice, lone = M.closed(tris)
        lo = [min(p[k] for p in pts) for k in range(3)]; hi = [max(p[k] for p in pts) for k in range(3)]
        found = {
            'time, s': round(v['ms'] / 1000, 2), 'panel': v['facts'], 'message': v['msg'],
            'zip': v['name'], 'bytes': len(raw), 'entries': {e.filename: e.file_size for e in z.infolist()},
            'crc': 'all correct' if bad is None else 'BAD: ' + bad,
            'stl triangles': len(tris), 'points after welding': len(pts), 'closed': twice == 0 and lone == 0,
            'pieces': M.pieces(len(pts), tris), 'normals that disagree': badn,
            'size mm': [round(hi[k] - lo[k], 2) for k in range(3)], 'volume mm3': round(M.volume(pts, tris), 1),
        }
        if not found['closed'] or bad is not None: ok = False
        print('== ' + label); print(json.dumps(found, indent=1, ensure_ascii=False))
    print('ALL GOOD' if ok else 'SOMETHING FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
