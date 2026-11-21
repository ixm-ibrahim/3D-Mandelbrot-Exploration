"""Round 12, tried rules: the starting values of the new entries' dials as the page holds them, and their element ids. -> params.txt"""
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run as R
code, text = R.shot(R.PAGE, [{'wait': 'window.squaringLab && window.squaringLab.idle()', 'timeout': 180}, {'js': io.open(os.path.join(HERE, 'params.js'), encoding='utf-8').read()}], 'params-steps')
R.write('params.txt', text)
print(text)
sys.exit(code)
