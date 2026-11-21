import io
p='src/js/45-export.js'
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b)
rep("""const EXPORT_TILE = 512;      // tiles are this many pixels square
""","""const EXPORT_TILE = 512;      // tiles are this many pixels square
const EXPORT_MAX = 1e8;       // pixels in all: three times an 8K picture. Beyond it a browser may run out of memory instead of saying no.
""")
rep("""  const o = { ...EXPORT.opt }, snap = takeSnapshot(), [W, H] = exportDims(o, snap.stage);
  const big = exportCanvas(W, H);
  if (!big) {
    releaseSnapshot(snap);
    exportSay(`This browser cannot hold a picture of ${W} × ${H} pixels. Choose a smaller size.`);
    return;
  }
""","""  const o = { ...EXPORT.opt }, [pw, ph] = stagePixels(), [W, H] = exportDims(o, { pw, ph });
  const big = W * H <= EXPORT_MAX ? exportCanvas(W, H) : null;
  if (!big) {
    exportSay(`This browser cannot hold a picture of ${W} × ${H} pixels. Choose a smaller size.`);
    return;
  }
  const snap = takeSnapshot();
""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)

p='out/r4/render-export/t.py'
s=io.open(p,encoding='utf-8').read()
a="""

def main():"""
s=s.replace(a,r'''
# ---- 8K: the whole job to the end (one pass, to keep it short), and a size that is refused in plain words
TESTS['big'] = [
    step("""
L.R.warmOn = false; L.S.q.aa = 1; L.syncControls(); L.touch(); await idle();
const t0 = performance.now();
await startJob('7680', 'As on screen', 'JPG');
const { f, bm } = await saveJob();
const out = { size: bm.width + 'x' + bm.height, bytes: f.blob.size, type: f.blob.type, seconds: +((performance.now() - t0) / 1000).toFixed(1), facts: $('exportFacts').textContent, preview: $('exportPreview').width + 'x' + $('exportPreview').height };
if (bm.width !== 7680 || bm.height !== 4320) fail('not 8K: ' + out.size);
return out;
""", shot='panel-8k-done.png', clip='#secExport'),
    step("""
$('exportDiscard').click(); L.setExtreme(true); L.syncControls();
await startJob('Typed', 'As on screen', 'PNG', 16384, 16384); await sleep(200);
const out = { busy: L.exportBusy(), msg: $('exportMsg').textContent, note: $('exportSizeNote').textContent };
L.setExtreme(false); L.syncControls();
out.afterExtremeOff = [$('exportWNum').value, $('exportHNum').value];
$('resetAll').click(); await sleep(100); await idle();
return out;
"""),
]

# ---- Fine at twice the size against the screen (the default settings of the panel), to look at
TESTS['fine'] = [
    step("""
L.R.warmOn = false; await idle();
const cv = $('view'), W = cv.width, H = cv.height;
const t0 = performance.now();
await startJob('Twice', 'Fine', 'PNG');
const { bm } = await saveJob(); const secs = +((performance.now() - t0) / 1000).toFixed(1);
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return Object.assign({ seconds: secs }, d);
""", shot='fine-default.png', clip='#cmp'),
    step("""
$('cmp').remove(); $('mode-j').click(); await idle();
const cv = $('view'), W = cv.width, H = cv.height;
await startJob('Twice', 'Fine', 'PNG');
const { bm } = await saveJob();
const live = await liveShot(), keep = document.createElement('canvas'); keep.width = W; keep.height = H; keep.getContext('2d').drawImage(live, 0, 0);
const d = diff(await pixelsOf(bm, W, H), await pixelsOf(keep, W, H));
show(keep, bm); $('exportDiscard').click();
return d;
""", shot='fine-julia.png', clip='#cmp'),
]
'''+a,1)
s=s.replace("""rows.push([Math.round(performance.now() - t0), $('exportStep').textContent.replace(/^.*pixels\\. /, ''),""","""rows.push([Math.round(performance.now() - t0), $('exportStep').textContent.replace(/^.*pixels[.] /, ''),""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')
