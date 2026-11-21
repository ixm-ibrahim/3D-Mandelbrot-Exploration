import sys, os, time
sys.argv = [sys.argv[0]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drive
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
print("started", time.strftime("%H:%M:%S"), flush=True)
try:
    drive.t_busy2()
except Exception:
    import traceback; traceback.print_exc()
print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)), flush=True)
print("ended", time.strftime("%H:%M:%S"), flush=True)
