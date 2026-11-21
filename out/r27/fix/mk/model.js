// Round 27, fixer, defect M: what a saved 3D model of Balls on balls says it was made from. A 48-cell model is made,
// the file that would be saved is caught by the page's own hook, and the line "Made from" is read out of it (the
// archive is stored without compression, so the text stands in it as it is).
if (!(S.mode === 'k' && S.k.group === 1)) { L.ballsShow(); await settle(); }
let saved = null; window.squaringLabSaveHook = (name, blob) => { saved = { name, blob }; };
window.squaringLabMeshTest = { cells: 48 };
$('meshStart').click(); await sleep(300);
for (let i = 0; i < 6000 && L.meshBusy(); i++) await sleep(50);
if (L.meshBusy()) fail('the model job never ended');
const shown = id => { const e = $(id); return !!e && e.getBoundingClientRect().width > 0; };
$('secMesh') && ($('secMesh').open = true); await sleep(100);
if (!$('meshSave')) fail('no save button');
$('meshSave').click(); await sleep(800);
delete window.squaringLabMeshTest; delete window.squaringLabSaveHook;
if (!saved) fail('nothing reached the save hook: ' + ($('meshMsg') ? $('meshMsg').textContent : ''));
const bytes = new Uint8Array(await saved.blob.arrayBuffer()), text = new TextDecoder('latin1').decode(bytes.subarray(0, Math.min(bytes.length, 4000000)));
const lines = [...text.matchAll(/Made from[^\r\n]{0,400}/g)].map(m => m[0]);
return JSON.stringify({ file: saved.name, bytes: bytes.length, madeFrom: [...new Set(lines)], saysT: lines.some(l => /\bt = /.test(l)) });
