"""Round 12, tried rules: every equation preset, other powers, Julia, Kleinian and the 2D view under each new entry. -> eq.txt"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R
steps = [{'wait': 'window.squaringLab && window.squaringLab.idle()', 'timeout': 180},
         {'js': io.open(os.path.join(HERE, 'eq.js'), encoding='utf-8').read(), 'wait': 'window.__t.done', 'timeout': 900},
         {'js': "if (/[1-9][0-9]* failed/.test(window.__t.text)) console.error(window.__t.text); return window.__t.text;"}]
code, text = R.shot(R.PAGE, steps, 'eq-steps')
R.write('eq.txt', text)
print(text)
sys.exit(code)
