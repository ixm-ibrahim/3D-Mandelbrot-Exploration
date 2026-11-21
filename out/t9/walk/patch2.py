"""One-off: turns the copies of the first check's drv.py and walk.py into the second check's versions (part 2)."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
d = open(os.path.join(HERE, 'drv.py'), encoding='utf-8').read()
a = "      exp: L.exportBusy ? L.exportBusy() : null, mesh: L.meshBusy ? L.meshBusy() : null,"
if 'expStep' not in d:
    assert a in d
    d = d.replace(a, a + "\n      expStep: ($('exportStep') || {}).textContent || '', meshStep: ($('meshStep') || {}).textContent || '', expMsg: ($('exportMsg') || {}).textContent || '', meshMsg: ($('meshMsg') || {}).textContent || '',")
    open(os.path.join(HERE, 'drv.py'), 'w', encoding='utf-8').write(d)

s = open(os.path.join(HERE, 'walk.py'), encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90])
    s = s.replace(a, b)


rep('''        self.n_fail = {}
        self.last_blank_step = -99''', '''        self.n_fail = {}
        self.last_blank_step = -99
        self.blank_run = 0
        self.pics = {"checked": 0, "shown": 0, "blank": 0, "masked": 0}
        self.job_seen = {}''')
rep('''        if chk["sw"] > chk["iw"] + 1:''', '''        if chk.get("nf"):
            self.fail(step, "nan-state", chk["nf"], shot=False)
        for k in ("exp", "mesh"):
            if chk.get(k):
                txt = chk.get(k + "Step", "")
                seen = self.job_seen.get(k)
                if not seen or seen[0] != txt:
                    self.job_seen[k] = (txt, time.time(), False)
                elif time.time() - seen[1] > 100 and not seen[2]:
                    self.job_seen[k] = (txt, seen[1], True)
                    self.fail(step, "job-no-progress", {"job": k, "text": txt, "seconds": round(time.time() - seen[1])}, shot=False)
            else:
                self.job_seen.pop(k, None)
        if chk["sw"] > chk["iw"] + 1:''')
a = s.index('    def blank_check(self, step, chk, log):')
b = s.index('def walk(args):')
s = s[:a] + '''    def blank_check(self, step, chk, log):
        lab = self.lab
        st = lab.picture_stats()
        self.pics["checked"] += 1
        if st is None or st.get("other") is None:
            self.pics["masked"] += 1
            return st
        if st["other"] >= 0.004:
            self.pics["shown"] += 1
            self.blank_run = 0
            return st
        self.pics["blank"] += 1
        expected = [k for k in ("eqErr", "note", "glfail", "kwarn") if chk.get(k)]
        state = lab.js("return __w.state();")
        if expected:
            self.fail(step, "blank-expected", {"why": expected, "stats": st}, shot=False)
            return st
        # keep the proof before anything is touched
        try:
            with open(os.path.join(self.folder, "b%04d-seen.png" % step), "wb") as f:
                f.write(lab.shot_png())
        except Exception:
            pass
        # is it only the camera? Reset view is itself a logged action.
        a = {"op": "click", "sel": "#reset", "name": "Reset view", "probe": True, "wait": "idle"}
        log(a)
        perform(lab, a)
        lab.wait_idle(120)
        st2 = lab.picture_stats()
        if st2 is not None and st2.get("other") is not None and st2["other"] < 0.004:
            self.blank_run += 1
            self.fail(step, "BLANK", {"stats": st, "after_reset_view": st2, "state": state, "check": chk})
            if self.blank_run >= 2:
                a = {"op": "click", "sel": "#resetAll", "name": "Reset everything", "probe": True, "wait": "idle"}
                log(a)
                how = perform(lab, a)
                lab.wait_idle(120)
                st3 = lab.picture_stats()
                if st3 is not None and st3.get("other") is not None and st3["other"] < 0.004:
                    self.fail(step, "BLANK-HARD", {"after_reset_everything": st3, "how": how, "check": lab.check()})
                else:
                    self.blank_run = 0
        else:
            self.blank_run = 0
            self.fail(step, "blank-camera", {"stats": st, "cam": state.get("cam"), "flat": chk["flat"], "mode": chk["mode"]}, shot=False)
        return st2


''' + s[b:]
rep('''    folder = os.path.join(HERE, "run%s" % args.seed)''', '''    folder = os.path.join(HERE, "run%s%s" % (args.seed, args.tag))''')
rep('''    n_idle_waits = n_slow = 0
    force = None''', '''    n_idle_waits = n_slow = 0
    force = []
    used = {}
    jobs_started = {"exp": 0, "mesh": 0}''')
rep('''            if force:
                a, force = force, None
            elif chk0["playing"]''', '''            if args.jobs and not force and s % 9 == 1 and not chk0["exp"] and not chk0["mesh"]:
                # keep a job running: open the panel if it is shut, choose a size, press Start (all logged, all real input)
                which = "exp" if jobs_started["exp"] <= jobs_started["mesh"] else "mesh"
                sec, start = ("#secExport", "#exportStart") if which == "exp" else ("#secMesh", "#meshStart")
                if not lab.js("return document.querySelector('%s').open;" % sec):
                    force.append({"op": "click", "sel": sec + " > summary", "name": "open the panel"})
                if which == "exp":
                    force.append({"op": "select", "sel": "#exportSize", "name": "Size", "index": rng.choice([2, 3, 4, 5])})
                    force.append({"op": "select", "sel": "#exportQuality", "name": "Quality", "index": rng.choice([0, 1, 2])})
                else:
                    force.append({"op": "select", "sel": "#meshCells", "name": "Resolution, cells", "index": rng.choice([0, 1, 2])})
                force.append({"op": "click", "sel": start, "name": "start a job"})
                jobs_started[which] += 1
            if force:
                a = force.pop(0)
            elif chk0["playing"]''')
rep('''            log(a)
            how = perform(lab, a)
            waited = False''', '''            log(a)
            how = perform(lab, a)
            key = a.get("sel") or a["op"]
            if a["op"] in ("wheel", "drag", "dbl", "key"): key = "picture:" + a["op"]
            used[key] = used.get(key, 0) + (1 if how not in ("gone", "no option") else 0)
            if chk0["exp"] or chk0["mesh"]: used["(actions while a job ran)"] = used.get("(actions while a job ran)", 0) + 1
            waited = False''')
rep('''        lab.js("document.querySelectorAll('.dial.is-playing button[aria-pressed=true]').forEach(b => b.click());")
        t = lab.wait_idle(240)''', '''        lab.js("document.querySelectorAll('.dial.is-playing button[aria-pressed=true]').forEach(b => b.click());")
        c0 = lab.check()
        if c0["exp"] or c0["mesh"]:
            # a job still runs: press its Cancel for real and see that it stops
            for panel, k in (("#exportPanel", "exp"), ("#meshPanel", "mesh")):
                if c0[k]:
                    sel = lab.js("const b = [...document.querySelectorAll('%s button')].find(b => /^Cancel/.test(b.textContent.trim())); if (!b) return null; b.closest('details').open = true; return __w.sel(b);" % panel)
                    how = lab.click(sel) if sel else "no cancel button"
                    tc = time.time()
                    while time.time() - tc < 40 and lab.check()[k]:
                        time.sleep(0.3)
                    c1 = lab.check()
                    print("seed %s end: job %s still running, Cancel pressed (%s): busy afterwards %s after %.1f s, step text %r, message %r" % (args.seed, k, how, c1[k], time.time() - tc, c1[k + "Step"], c1[k + "Msg"]), flush=True)
                    if c1[k]:
                        run.fail(step[0] + 1, "job-cancel-stuck", {"job": k, "check": c1})
        t = lab.wait_idle(240)''')
rep('''        with open(os.path.join(folder, "end.png"), "wb") as f:
            f.write(png)''', '''        with open(os.path.join(folder, "end.png"), "wb") as f:
            f.write(png)
        end_state = lab.js("return __w.state();")
        with open(os.path.join(folder, "end-state.json"), "w", encoding="utf-8") as f:
            json.dump(end_state, f)
        # does Reset everything bring a picture back, whatever state the walk ended in?
        how = lab.click("#resetAll")
        t2 = lab.wait_idle(240)
        st = lab.picture_stats(os.path.join(folder, "end-reset-pic.png"))
        c2 = run.after(step[0] + 2, None, True)
        print("seed %s after Reset everything (%s): idle after %s s, picture %s, status %r, mode %s, flat %s" % (args.seed, how, t2 and round(t2, 1), st, c2["status"], c2["mode"], c2["flat"]), flush=True)
        if t2 is None:
            run.fail(step[0] + 2, "STUCK", {"at": "after Reset everything", "check": c2})
        if st is None or st.get("other") is None or st["other"] < 0.004:
            run.fail(step[0] + 2, "BLANK-HARD", {"at": "after Reset everything at the end", "stats": st, "check": c2})
        print("seed %s pictures checked: %s" % (args.seed, json.dumps(run.pics)))
        print("seed %s jobs forced: %s" % (args.seed, json.dumps(jobs_started)))
        focus = ["#trapExamples", "#col-reach", "#col-reachNum", "#col-solid", "#col-trap", "#twinMerc", "#twinLathe", "#twinBulb", "#twinOff", "#fig4Show", "#fig4Back",
                 "#juliaPreset", "#kleinPreset", "#exportStart", "#meshStart", "#resetAll", "#flat", "#extreme", "#mode-m", "#mode-j", "#mode-k", "(actions while a job ran)"]
        print("seed %s uses: %s" % (args.seed, json.dumps({k: used.get(k, 0) for k in focus})))
        with open(os.path.join(folder, "used.json"), "w", encoding="utf-8") as f:
            json.dump(used, f, indent=0)''')
open(os.path.join(HERE, 'walk.py'), 'w', encoding='utf-8').write(s)
print('patched')
