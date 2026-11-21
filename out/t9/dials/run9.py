"""Tester "dials", second check: run the first check's own tests (out/t6/controls/drive.py) on dist/v8.html.

  python out/t9/dials/run9.py dials resets extreme

The first tester's code runs unchanged; only the page and the folder for its pictures are swapped (out/t9/dials/t6run/).
"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "out", "t6", "controls"))
import drive  # noqa: E402

drive.URL = "dist/v8.html"
drive.HERE = os.path.join(HERE, "t6run")
os.makedirs(drive.HERE, exist_ok=True)

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try: stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception: pass
    print("page %s, started %s" % (drive.URL, time.strftime("%H:%M:%S")), flush=True)
    for name in sys.argv[1:]:
        print("===== " + name, flush=True)
        before = len(drive.results)
        try:
            drive.TESTS[name]()
        except Exception as ex:
            import traceback
            traceback.print_exc()
            drive.ok("%s ran to its end" % name, False, repr(ex)[:400])
        part = drive.results[before:]
        print("%s: %d passed, %d failed" % (name, part.count(True), part.count(False)), flush=True)
    print("%d passed, %d failed" % (drive.results.count(True), drive.results.count(False)), flush=True)
    print("ended", time.strftime("%H:%M:%S"), flush=True)
