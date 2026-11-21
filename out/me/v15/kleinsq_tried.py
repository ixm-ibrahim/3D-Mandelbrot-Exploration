"""Move the two Kleinian squaring entries to the group 'tried' (the user called them wrong, 2026-11-18) and say why
in their tags. python out/me/v15/kleinsq_tried.py <dir>   patches <dir>/js/10-approaches.js; safe to run again."""
import io, os, sys
p = os.path.join(sys.argv[1], 'js', '10-approaches.js')
t = io.open(p, encoding='utf-8', newline='').read()
pairs = [
 ("id: 'kleinsq', name: 'Kleinian squaring, one plane', group: 'kleinian',", "id: 'kleinsq', name: 'Kleinian squaring, one plane', group: 'tried',"),
 ("id: 'kleinsq2', name: 'Kleinian squaring, two planes', group: 'kleinian',", "id: 'kleinsq2', name: 'Kleinian squaring, two planes', group: 'tried',"),
 ("const KQ_TAG = 'Squaring rebuilt from sphere inversions, a different one in each region of the sphere of directions: a reading of the first construction in Kučera’s paper. Its slice at z = 0 is a cousin of the flat set, not the flat set.';",
  "const KQ_TAG = 'Tried: squaring rebuilt from sphere inversions, a different one in each region of the sphere of directions (a reading of the first construction in Kučera’s paper). Failed: its slice at z = 0 is a cousin of the flat set, not the flat set.';"),
 ("const KQ2_TAG = 'The same caps round two circles: a reading of the second construction in Kučera’s paper (its Figure 4). Whole only for a Julia set with c on the x-axis. Everywhere else it tears where the two families of caps meet.';",
  "const KQ2_TAG = 'Tried: the same caps round two circles (a reading of the second construction in Kučera’s paper, its Figure 4). Failed: the slice at z = 0 is not the flat set, the number of buds follows the number of planes and not the power, and away from the x-axis it tears into shards.';"),
]
for old, new in pairs:
    if new in t: print('already:', new[:60]); continue
    assert t.count(old) == 1, old[:70]
    t = t.replace(old, new); print('patched:', new[:60])
io.open(p, 'w', encoding='utf-8', newline='').write(t)
