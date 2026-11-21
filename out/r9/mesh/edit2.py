"""Engineer "mesh", round 9: the edit for item 2 (the progress line while the first model of a formula is prepared)."""
p = 'src/js/46-mesh.js'
s = open(p, encoding='utf-8', newline='').read()
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:70])
    s = s.replace(a, b)
rep("""  failed: 'The model could not be built. It may need more memory than the browser gives a page. Try a lower resolution.',
};""", """  failed: 'The model could not be built. It may need more memory than the browser gives a page. Try a lower resolution.',
  prepare: 'Preparing to read this solid. The first model of each formula takes a few seconds longer. The next one starts at once.',
};""")
rep("""    if (!field) job.snap = takeSnapshot();
    MESH.result = await meshRun(job);""", """    if (!field) { job.snap = takeSnapshot(); await meshPrepare(job); }
    MESH.result = await meshRun(job);""")
rep("""// True while the page's graphics are gone. Asked of the canvas itself, so it needs nothing from the renderer.""",
"""// The first model of a formula waits while the browser prepares the program its samples are drawn with (the
// renderer starts that program when a model first asks for it: snapProg in 40-render.js answers 'wait' until it is
// there). That takes a few seconds, and until now the panel said "Starting. 0%." all the while. The progress line
// says in plain words what is going on, for as long as it lasts, and counts the seconds once there are two.
async function meshPrepare(job) {
  if (typeof snapProg !== 'function') return;
  const began = performance.now();
  job.plain = true;   // the line shows the step as it is, without a percentage
  try {
    while (snapProg(job.snap, true) === 'wait') {
      const s = Math.round((performance.now() - began) / 1000);
      await job.turn(MESH_WORDS.prepare + (s >= 2 ? ` ${s} seconds so far.` : ''), 0, true);
      await new Promise(done => setTimeout(done, 60));
    }
  } finally { job.plain = false; }
}
// True while the page's graphics are gone. Asked of the canvas itself, so it needs nothing from the renderer.""")
rep("""  const text = `${job.step}. ${pc}%.${left}`;""", """  const text = job.plain ? job.step : `${job.step}. ${pc}%.${left}`;""")
open(p, 'w', encoding='utf-8', newline='').write(s)
print('edit 2 done')
