"""One-off: make slice-de0.py from slice.py: the same slices with the distance estimate switched off (Quality, S.q.de = 0)."""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(HERE, 'slice.py'), encoding='utf-8').read()
for a, b in [("S.cutOn = false; S.flat = true;", "S.q.de = 0; S.cutOn = false; S.flat = true;"), ("'s-%s-%s' % (mode, name)", "'s0-%s-%s' % (mode, name)"),
             ("'s-%s-mercator' % mode", "'s0-%s-mercator' % mode"), ("'slice-steps'", "'slice-de0-steps'"), ("'slice.txt'", "'slice-de0.txt'")]:
    assert a in s, a
    s = s.replace(a, b)
io.open(os.path.join(HERE, 'slice-de0.py'), 'w', encoding='utf-8', newline='\n').write(s)
