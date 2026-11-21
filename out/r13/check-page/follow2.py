"""Checker: sideways phone, Learn on, Tab many times with real keys, then tap Mandelbrot. Did the first run's failure repeat?"""
import time
from drive import Session, show
RADIO = "return { checked: [...document.querySelectorAll('input[name=mode]')].filter(r => r.checked).map(r => r.id), learn: L.S.learn, mode: L.S.mode, cls: document.body.className, active: document.activeElement ? (document.activeElement.id || document.activeElement.tagName) : null, y: Math.round(scrollY) };"
with Session("dist/r13-check-page.html", "667x375", "light", mobile=True, name="follow2-667x375") as s:
    s.done()
    m = s.js("const e = document.querySelector('#mode-l + span'); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); return mid(e);")
    s.tap(m[0], m[1]); time.sleep(0.3)
    s.js("go(0); await sleep(100); $('learnCanvas').focus();")
    stops = []
    for i in range(70):
        s.key("Tab"); time.sleep(0.02)
    show("after 70 Tab", s.js(RADIO))
    for i in range(70):
        s.key("Tab", shift=True); time.sleep(0.02)
        if i in (55, 58, 60, 62, 64, 66, 68, 69): stops.append(s.js("return (document.activeElement.id || document.activeElement.tagName) + ' ' + [...document.querySelectorAll('input[name=mode]')].filter(r => r.checked).map(r => r.id).join() + ' learn=' + L.S.learn;"))
    show("Shift+Tab stops near the end", stops)
    show("after 70 Shift+Tab", s.js(RADIO))
    m = s.js("const e = document.querySelector('#mode-m + span'); e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(200); const p = mid(e), t = document.elementFromPoint(p[0], p[1]); return [p[0], p[1], t ? (t.id || t.className || t.tagName) + ':' + t.textContent.slice(0, 20) : null];")
    show("before the tap on Mandelbrot", [m, s.js(RADIO)])
    s.tap(m[0], m[1]); time.sleep(0.4)
    show("after the tap on Mandelbrot", s.js(RADIO))
    s.shot("follow2-land-after-tap.png")
