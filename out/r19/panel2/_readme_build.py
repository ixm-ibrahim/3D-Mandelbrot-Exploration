"""Builds README.md from README.src.md: puts the old and the new grid and the verdict-moves table in."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'README.src.md'), encoding='utf-8').read()
tab = open(os.path.join(HERE, 'table.txt'), encoding='utf-8').read().split('=== ')[0].rstrip()
mv = open(os.path.join(HERE, 'moves.txt'), encoding='utf-8').read().rstrip()
NL = chr(10)
grid = ('F: = the lines it fails there. pie = one piece, sta = the solid stays, bod = bodies, d3 = truly 3D, cle = clean close up.' + NL + NL
        + '```' + NL + tab + NL + '```' + NL + NL
        + 'How the skin verdict moves with where one looks (`moves.txt`; thin and film are the worst tile; "old 12" = the new number on the old' + NL
        + 'panel\'s 12 tile places only; the last column is the chance of a pass if only ONE half-plane and ONE skin point were cut):' + NL + NL
        + '```' + NL + mv + NL + '```')
open(os.path.join(HERE, 'README.md'), 'w', encoding='utf-8').write(src.replace('<<GRID>>', grid))
print('README.md written', len(src), len(grid))
