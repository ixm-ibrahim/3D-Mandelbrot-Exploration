"""Checker: where does the held picture let go, and why? Usage: python out/r13/check-page/probe1.py SIZE [mobile] [URL]"""
import sys, time
from drive import Session, show
size = sys.argv[1]
mobile = len(sys.argv) > 2 and sys.argv[2] == "mobile"
url = sys.argv[3] if len(sys.argv) > 3 else "dist/r13-check-page.html"
with Session(url, size, "light", mobile=mobile, name="probe1-" + size) as s:
    s.done()
    show("boxes in the page (document y)", s.js(r"""
      const d = e => { const r = e.getBoundingClientRect(); return [Math.round(r.top + scrollY), Math.round(r.bottom + scrollY)]; };
      const bench = document.querySelector('.bench'), main = document.querySelector('.bench-main'), dials = document.querySelector('.dials'), secs = $('sections');
      const ctl = [...document.querySelectorAll('.dials input, .dials select, .dials button, .dials summary')].filter(vis);
      const last = ctl[ctl.length - 1];
      return { bench: d(bench), benchDisplay: getComputedStyle(bench).display, main: d(main), dials: d(dials), sections: d(secs),
        lastControl: [(last.id || last.textContent).trim().slice(0, 30), d(last), last.closest('details') ? last.closest('details').id : null, last.parentElement.className],
        dialsKids: [...dials.children].map(k => [(k.id || k.className), d(k)]),
        benchKids: [...bench.children].map(k => [(k.id || k.className), d(k), getComputedStyle(k).flex, getComputedStyle(k).overflow]),
        secs: [...secs.children].filter(vis).map(k => [k.id, d(k), k.open]), doc: document.documentElement.scrollHeight };
    """))
    show("try to scroll to the last control", s.js(r"""
      const ctl = [...document.querySelectorAll('.dials input, .dials select, .dials button, .dials summary')].filter(vis), e = ctl[ctl.length - 1];
      const y0 = scrollY; e.scrollIntoView({ block: 'center', behavior: 'instant' }); await sleep(300); const y1 = scrollY;
      go(4500); await sleep(300); const y2 = scrollY;
      const main = document.querySelector('.bench-main');
      return [y0, y1, y2, rect(main), rect(e), getComputedStyle(document.documentElement).scrollBehavior, getComputedStyle(e).scrollMarginTop];
    """))
    s.shot("probe1-%s-%s-at4500.png" % (size, "m" if mobile else "d"))
