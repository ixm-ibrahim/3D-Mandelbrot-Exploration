// What is on the page: the approaches, and every word the feature puts in the panel and the transport.
//@
return { opens: LAB.APPROACHES[S.approach].id, list: LAB.APPROACHES.map(a => a.id + ' = ' + a.name) };
//@
await openLearn(); await pickShape(); L.shape.pause(); L.shape.goto(0);
const panel = $('learnFollow').closest('details');
const vis = e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
const texts = [...panel.querySelectorAll('summary, legend, .seg span, p, button, .label, label')].filter(vis).map(e => e.tagName + (e.id ? '#' + e.id : '') + ': ' + e.textContent.trim().replace(/\s+/g, ' '));
return texts;
//@
const bar = $('learnShapeBar');
const vis = e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0; };
return { bar: [...bar.querySelectorAll('span, p, button, option, legend, input')].map(e => e.tagName + (e.id ? '#' + e.id : '') + ': ' + (e.textContent.trim() || '') + (e.title ? ' [title: ' + e.title + ']' : '') + (e.getAttribute('aria-label') ? ' [aria: ' + e.getAttribute('aria-label') + ']' : '')),
  titles: [...bar.querySelectorAll('label[title]')].map(e => e.title), hint: $('learnHint') ? $('learnHint').textContent : [...document.querySelectorAll('.learn-hint')].map(e => e.textContent),
  canvasAria: $('learnShapeCanvas').getAttribute('aria-label') };
