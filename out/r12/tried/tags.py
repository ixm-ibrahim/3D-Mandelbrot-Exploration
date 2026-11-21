"""One-off: reword the tags of the three tried entries so the line under the name says what was tried and why it failed."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
pairs = [
    ("tag: 'The one-plane rule on several planes through the x-axis, joined by a smooth blend instead of a fold.',",
     "tag: 'Tried: several planes joined by a smooth blend instead of a fold, to get beads without a tear. Failed: one swollen mass, no beads.',"),
    ("tag: 'The quaternion square with the turn around the x-axis multiplied or given a wobble, to break its rings into beads.',",
     "tag: 'Tried: change the turn around the x-axis, to break the rings of the quaternion square into beads. Failed: the rings stay rings.',"),
    ("tag: 'Wrap a flat sheet of triangles around the sphere of directions like a pillow, and multiply the sheet.',",
     "tag: 'Tried: wrap a flat sheet of triangles around the sphere like a pillow, so that no seam is needed. Failed: one lump, or fibres.',"),
]
for a, b in pairs:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('tags reworded')
