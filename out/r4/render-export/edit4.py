import io
p='src/js/45-export.js'
s=io.open(p,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a,s.count(a))
    s=s.replace(a,b)
rep("""        // as the piece before. The cost is taken from the GPU's own count where it arrives (the dearest piece counts
        // for a part of the tile, the average for whole passes), else from the clock, which is not allowed to push a
        // piece below a sixteenth of the tile (see bgPiece in 40-render.js).
        const est = { wall: 0, gMax: 0, gMs: 0, gPx: 0 };""","""        // as the piece before. The cost is taken from the GPU's own count where it arrives (for a part of the tile
        // the dearest piece of the first pass counts, for whole passes the average), else from the clock. Neither is
        // allowed to push a piece below a sixteenth of the tile: one slow reading, with the GPU busy elsewhere, must
        // not turn the rest of the tile into single rows (see bgPiece in 40-render.js).
        const est = { wall: 0, g0: 0, gMs: 0, gPx: 0 };""")
rep("""          const target = bgTarget(), first = clear, part = est.gMax || est.wall;""","""          const target = bgTarget(), first = clear, part = est.g0 || est.wall;""")
rep("""            else rows = Math.min(rows, Math.max(Math.round(fit), est.gMax ? 1 : Math.ceil(th / 16)));""","""            else rows = Math.min(rows, Math.max(Math.round(fit), Math.ceil(th / 16)));""")
rep("""          }, null, ms => { est.gMax = Math.max(est.gMax, ms / px); est.gMs += ms; est.gPx += px; }));""","""          }, null, ms => { if (s0 === 0) est.g0 = Math.max(est.g0, ms / px); est.gMs += ms; est.gPx += px; }));""")
rep("""  // the outline of the 2D view is a width in pixels: it keeps its weight in the larger picture
  if (typeof snap.S.colour.edge === 'number') snap.S.colour.edge *= scale;
""","""  // the outline of the 2D view and the glow beside it are widths in pixels: they keep their weight in the larger picture
  for (const key of ['edge', 'edgeGlow']) if (typeof snap.S.colour[key] === 'number') snap.S.colour[key] *= scale;
""")
io.open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')
