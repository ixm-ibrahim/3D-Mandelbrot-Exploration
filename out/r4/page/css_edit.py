"""One-off edit of src/css/00-base.css for round 4 (kept as a record of what changed)."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'css', '00-base.css')
s = io.open(p, encoding='utf-8').read()

def rep(old, new, count=1):
    global s
    if old not in s:
        raise SystemExit('not found: ' + old[:70])
    s = s.replace(old, new, count)

rep(""".toprow { display: flex; justify-content: space-between; align-items: center; gap: 8px 12px; flex-wrap: wrap; }
""", """/* The top row stays in reach while the long column scrolls. Each tick box has a line of its own and both buttons
   share one width, so nothing in it moves when a label changes ("Collapse all" / "Expand all", the slice height). */
.toprow { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: var(--paper); display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 6px 12px; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--line); }
.toprow-checks, .toprow-btns { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.toprow-btns .btn { width: 100%; white-space: nowrap; }
.flat-z { color: var(--ink-2); font-size: 13px; white-space: nowrap; }
#extremeNote { margin-top: -8px; }
/* what the browser scrolls a focused control to must clear the sticky row */
.dials .sec > summary, .dials .dial, .dials .field, .dials .check, .dials .btn { scroll-margin-top: 96px; }
""")
rep(""".btn:hover { border-color: var(--ink-2); }
""", """.btn:hover { border-color: var(--ink-2); }
/* a button that shows a state: the quality preset in use */
.btn.is-on { background: var(--ink); color: var(--paper); border-color: var(--ink); }
""")
rep(""".sec-body { display: flex; flex-direction: column; gap: 14px; padding-bottom: 14px; }
""", """.sec-body { display: flex; flex-direction: column; gap: 14px; padding-bottom: 14px; }
.sec-inner { display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.sec-inner:empty { display: none; }
""")
a = s.index('/* lists of points to jump to (Julia panel)')
b = s.index('/* lower: one step + scorecard */')
s = s[:a] + """/* a drop-down of entries to jump to, with its "Frame it" button, and the row that saves the current point */
.pick-row { display: flex; gap: 6px; align-items: flex-end; }
.pick-list { flex: 1 1 auto; min-width: 0; }
.pick-row > .btn { flex: none; }
.save-row { display: flex; gap: 6px; flex-wrap: wrap; }
.save-row input { flex: 1 1 9em; min-width: 0; font-family: var(--f-mono); font-size: 13.5px; padding: 6px 8px; color: var(--ink); background: var(--panel); border: 1px solid var(--line); border-radius: 0; }
.save-row input:focus-visible { outline: 2px solid var(--brass); outline-offset: 1px; }
@media (pointer: coarse) { .save-row input { font-size: 16px; } }
.warn-note { color: var(--warn); }
/* a sentence on the stage for the cases where there is nothing to draw */
.stage-note { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: max-content; max-width: min(36ch, 80%); text-align: center; font-size: 14px; color: var(--ink); background: var(--stage); border: 1px solid var(--line); padding: 8px 12px; pointer-events: none; }
/* the copy of the stage hint that narrow screens show under the picture */
.hint-below { display: none; font-size: 12.5px; color: var(--ink-2); }

""" + s[b:]
rep(""".why h2:not(:first-child) { margin-top: 18px; }
""", """.why h2:not(:first-child) { margin-top: 18px; }
.why h3 { margin: 8px 0 0; font-family: var(--f-body); font-weight: 600; font-size: 15.5px; line-height: 1.35; color: var(--ink); text-wrap: balance; }
""")
rep("""  .hint { display: none; }
  .stage-bar { justify-content: flex-end; }
""", """  .hint { display: none; }
  .hint-below { display: block; }
  .stage-bar { justify-content: flex-end; }
  /* short enough that the top row of the controls is on the first screen of a phone */
  .stage { height: clamp(300px, 44vh, 560px); }
""")
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('00-base.css edited,', len(s), 'bytes')
