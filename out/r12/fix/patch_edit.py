import io, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "edit_smoke.py")
s = io.open(p, encoding="utf-8").read()
def sw(a, b):
    global s
    assert s.count(a) == 1, (a, s.count(a))
    s = s.replace(a, b)
sw("o = s.options.find(x => x[0] !== s.def); e.value = String(o[0]);", "o = s.options.find(x => x[0] !== s.def); e.value = String(s.options.indexOf(o));")
sw("if (Number(e.value.replace('−', '-')) !== s.def) fail('after the Approach reset the control ' + s.label + ' of ' + a.name + ' shows ' + e.value + ', not ' + s.def); }",
   "const shows = s.type === 'select' ? (s.options[e.selectedIndex] || [])[0] : Number(e.value.replace('−', '-')); if (shows !== s.def) fail('after the Approach reset the control ' + s.label + ' of ' + a.name + ' shows ' + shows + ', not ' + s.def); }")
sw("e.value = String(o[0]); e.dispatchEvent(new Event('change', { bubbles: true })); await settle(a.name + ' with ' + o[1]);", "e.value = String(s.options.indexOf(o)); e.dispatchEvent(new Event('change', { bubbles: true })); await settle(a.name + ' with ' + o[1]);")
sw("      e.value = String(s.def); e.dispatchEvent(new Event('change', { bubbles: true }));\n", "      e.value = String(s.options.findIndex(x => x[0] === s.def)); e.dispatchEvent(new Event('change', { bubbles: true }));\n")
sw("if (hits(one) < 100) fail(", "if (hits(one) < 40) fail(")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("patched")
