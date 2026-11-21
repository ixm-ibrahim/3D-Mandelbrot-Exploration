"""A look at the page's controls: ids of the inputs a hand would use (power, modifiers, dials, reset, Show)."""
import json
from clab import Lab, Log

log = Log("t0b_ids")
with Lab("r26-checka") as lab:
    r = lab.js("""await learnOn();
      const all = [...document.querySelectorAll('input, select, button')].filter(e => e.id).map(e => e.id + ':' + (e.type || e.tagName) + (e.getClientRects().length ? '' : ' (hidden)'));
      return all;""")
    log(json.dumps(r))
    r = lab.js("""return [...document.querySelectorAll('#stage > *')].map(e => e.tagName + '#' + e.id + '.' + e.className + (e.hidden ? ' hidden' : ''));""")
    log(json.dumps(r))
    log.problems(lab)
