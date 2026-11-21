import io, json
PRE = "const L = window.squaringLab, $ = id => document.getElementById(id); const sleep = ms => new Promise(r => setTimeout(r, ms));\n"
def steps(tag, phone):
    s = []
    def st(js, name, wait=None):
        a = {"js": PRE + js, "shot": "out/me/v13/%s-%s.png" % (tag, name)}
        if wait: a["wait"] = wait; a["timeout"] = 240
        s.append(a)
    st("L.R.warmOn = false; await sleep(300); return 'open';", "0-open", "done")
    if phone:
        st("const a = $('secApproach'); a.open = true; a.scrollIntoView({block: 'start'}); await sleep(500); return 'scrolled to approach, scrollY ' + Math.round(scrollY);", "1-scrolled")
        st("window.scrollTo(0, document.querySelector('.dials').getBoundingClientRect().bottom + scrollY - 500); await sleep(500); return 'end of controls';", "2-end")
        st("window.scrollTo(0, 0); await sleep(300); return 'top';", "3-top")
    st("$('mode-l').click(); await sleep(700); return JSON.stringify(L.learn.state()).slice(0, 400);", "4-learn-2d")
    st("L.learn.goto(0, 0.6); await sleep(400); return L.learn.state().sentence;", "5-2d-midturn")
    st("L.learn.set({ space: 1 }); await sleep(400); L.learn.goto(0, 0.5); await sleep(400); return L.learn.state().sentence;", "6-1d-midturn")
    st("L.learn.set({ space: 3 }); await sleep(400); $('ap-lathe').click(); await sleep(500); L.learn.goto(0, 0.6); await sleep(500); return L.learn.state().moves.join(', ') + ' | ' + L.learn.state().sentence;", "7-3d-lathe")
    st("$('ap-tilt').click(); await sleep(500); L.learn.goto(1, 0.5); await sleep(500); return L.learn.state().moves.join(', ') + ' | ' + L.learn.state().sentence;", "8-3d-tilt")
    st("$('ap-mercator').click(); await sleep(500); L.learn.goto(1, 0.6); await sleep(500); return L.learn.state().moves.join(', ') + ' | ' + L.learn.state().sentence;", "9-3d-merc")
    if phone:
        st("const p = $('learnPanel') || document.querySelector('[id^=learn]'); window.scrollTo(0, 700); await sleep(500); return 'learn, scrolled';", "10-learn-scrolled")
    st("$('mode-m').click(); await sleep(500); return 'back to the solid: learn ' + L.S.learn;", "11-back", "done")
    return s
io.open('out/me/v13/look-desk.json', 'w', encoding='utf-8').write(json.dumps(steps('desk', False)))
io.open('out/me/v13/look-phone.json', 'w', encoding='utf-8').write(json.dumps(steps('phone', True)))
