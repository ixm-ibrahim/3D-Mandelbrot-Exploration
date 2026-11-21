// Round 28, builder: a saved picture with the neighbours at 150 (the second program). The file is read back in the
// page and compared with the picture on the screen: how much of each is not background.
const out = [];
$('ap-balls').click(); await settle();
S.k.brho = 1 / 3; S.k.bt = 0.5 * (100 / 150 + 1); L.ballsFrame(); go(); await settle();
out.push('on screen: ' + $('status').textContent + ', program ' + String(L.R.sig).replace(/\n/g, '/'));
let saved = null; window.squaringLabSaveHook = (name, blob) => { saved = { name, blob }; };
if (!$('exportStart')) fail('no picture export on this page');
$('exportSize').value = '0'; $('exportSize').dispatchEvent(new Event('change', { bubbles: true }));
$('exportStart').click(); await sleep(300);
for (let i = 0; i < 3000 && L.exportBusy(); i++) await sleep(50);
if (L.exportBusy()) fail('the picture job never ended');
if (vis($('exportSave'))) { $('exportSave').click(); await sleep(500); }
delete window.squaringLabSaveHook;
if (!saved) fail('no file reached the save hook: ' + ($('exportMsg') ? $('exportMsg').textContent : ''));
const bmp = await createImageBitmap(saved.blob), c = document.createElement('canvas'); c.width = bmp.width; c.height = bmp.height;
const g = c.getContext('2d'); g.drawImage(bmp, 0, 0);
const d = g.getImageData(0, 0, c.width, c.height).data; let fg = 0;
for (let i = 0; i < d.length; i += 4) if (Math.abs(d[i] - d[0]) + Math.abs(d[i + 1] - d[1]) + Math.abs(d[i + 2] - d[2]) > 24) fg++;
out.push('saved file ' + saved.name + ', ' + saved.blob.size + ' bytes, ' + c.width + ' x ' + c.height + ', pixels that are not background: ' + fg + ' (' + (100 * fg / (c.width * c.height)).toFixed(1) + ' %)');
out.push('message: ' + ($('exportMsg') ? $('exportMsg').textContent.slice(0, 160) : ''));
return JSON.stringify(out);
