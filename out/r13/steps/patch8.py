def sub(p, pairs):
    s = open(p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (s.count(a), a[:70])
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)

sub('src/js/65-learn-steps.js', [
 ("""      + (same ? ` “${A.name}” does exactly this ${where}.`
        : id === 'classic' ? ` “${A.name}” is the one approach in the list that does not keep the flat plane, so ${where} it does not follow this picture.`
        : ` As the power and its dials are set now, “${A.name}” does not follow this picture ${where}.`);""",
  """      + ` With a whole power and the dials at their starting values, every approach in the list does this ${where}. The one exception is “Mandelbulb, classic”, which does not keep the flat picture.`
      + (id === 'classic' ? (same ? ' At this power it happens to.' : '') : same ? '' : ` As the power and its dials are set now, “${A.name}” does not follow it ${where} either.`);"""),
])
sub('out/r13/steps/test.js', [
 (".note.split('numbers.')[1]} | note1: ${learnPlan({ space: 1, id: a.id, n, params: q }).note.split('have.')[1]}`);", ".note.split('flat picture.')[1]} | note1: ${learnPlan({ space: 1, id: a.id, n, params: q }).note.split('flat picture.')[1]}`);"),
 (".note.split('numbers.')[1]} | note1: ${learnPlan({ space: 1, id, n, params: q }).note.split('have.')[1]}`);", ".note.split('flat picture.')[1]} | note1: ${learnPlan({ space: 1, id, n, params: q }).note.split('flat picture.')[1]}`);"),
])
