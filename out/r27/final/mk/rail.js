// Round 27, final: why do the two marks on the zoom rail stand one pixel apart on the two pages as they open?
// Everything that could place them: the view limits, the camera, the boxes of the rail and of each thing on it,
// the scroll position, the size of the page.
await settle();
const box = e => { const b = e.getBoundingClientRect(); return [+b.left.toFixed(3), +b.top.toFixed(3), +b.width.toFixed(3), +b.height.toFixed(3)]; };
const stage = $('stage'), out = { scroll: [scrollX, scrollY], doc: [document.documentElement.scrollWidth, document.documentElement.scrollHeight], win: [innerWidth, innerHeight], dpr: devicePixelRatio,
  stage: box(stage), view: { zmin: S.view.zmin, zmax: S.view.zmax, bound: S.view.bound, fov: S.view.fov }, cam: { dist: L.cam.dist, yaw: L.cam.yaw, pitch: L.cam.pitch }, over: [] };
for (const e of stage.querySelectorAll('*')) { const b = e.getBoundingClientRect(); if (b.width && b.left > stage.getBoundingClientRect().left + 760) out.over.push([e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ').join('.') : ''), box(e), e.style.cssText.slice(0, 80)]); }
return JSON.stringify(out);
