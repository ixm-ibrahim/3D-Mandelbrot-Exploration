"""Put out/r14/rules/texts.js between the two R14-TEXTS marks of src/js/10-approaches.js. Run from the project root."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
p = os.path.join(ROOT, 'src', 'js', '10-approaches.js')
s = io.open(p, encoding='utf-8').read()
t = io.open(os.path.join(ROOT, 'out', 'r14', 'rules', 'texts.js'), encoding='utf-8').read()
a, b = s.index('// R14-TEXTS-BEGIN'), s.index('// R14-TEXTS-END')
s = s[:a] + '// R14-TEXTS-BEGIN\n' + t + s[b:]
io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
print('texts in place; PROVISIONAL left: %d; long dashes in the block: %d' % (s.count('PROVISIONAL'), t.count('—') + t.count('–')))
