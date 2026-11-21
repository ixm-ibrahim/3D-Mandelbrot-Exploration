import time, json, os
from lab import Lab, HERE, KEYS
lab = Lab(1400, 950, "dark", False, wait_idle=120)
L = "window.squaringLab"
cam = lambda: lab.js("return [+%s.cam.yaw.toFixed(4), +%s.cam.pitch.toFixed(4), +%s.cam.dist.toFixed(4)];" % (L, L, L))
lab.js("document.getElementById('view').focus();")
for k in ("ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"):
    a = cam(); sy = lab.js("return scrollY;")
    kw = dict(key=k, code=k, windowsVirtualKeyCode=KEYS[k])
    lab.p.call("Input.dispatchKeyEvent", type="rawKeyDown", **kw); time.sleep(0.35); lab.p.call("Input.dispatchKeyEvent", type="keyUp", **kw); time.sleep(0.4)
    print(k, "held 0.35 s:", a, "->", cam(), "scrollY", sy, "->", lab.js("return scrollY;"))
for ch, vk, code in (("+", 187, "Equal"), ("-", 189, "Minus")):
    a = cam()
    lab.p.call("Input.dispatchKeyEvent", type="keyDown", key=ch, code=code, windowsVirtualKeyCode=vk, text=ch, unmodifiedText=ch); time.sleep(0.1)
    lab.p.call("Input.dispatchKeyEvent", type="keyUp", key=ch, code=code, windowsVirtualKeyCode=vk); time.sleep(0.6)
    print(repr(ch), "pressed:", a, "->", cam())
print("hint css at 1400:", lab.js("const h = document.querySelector('.hint'); return [getComputedStyle(h).display, h.textContent];"))
lab.size(375, 812, True); time.sleep(0.5)
print("hint css on phone:", lab.js("const h = document.querySelector('.hint'); return [getComputedStyle(h).display, h.checkVisibility()];"))
print("dial-reset css on phone:", lab.js("const b = document.querySelector('.dial-reset'); const cs = getComputedStyle(b); const o = document.getElementById('collapseAll'); return [cs.fontSize, cs.padding, b.getBoundingClientRect().height, getComputedStyle(o).fontSize, o.getBoundingClientRect().height];"))
print(lab.close())
