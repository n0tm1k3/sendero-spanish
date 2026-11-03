// Content checks. Run: node tools/check.js
// - duplicate item ids (ids are the keys of saved progress, so they must be unique and never renamed)
// - unit numbers must equal their position in UNITS
// - malformed cloze / choice items
// - graded stories: share of words known by the time the story unlocks (target >= 95%)
const { load } = require('./content');
const { UNITS, STORIES } = load();
let problems = 0;
const fail = m => { problems++; console.log('PROBLEM:', m); };

const ids = new Set();
UNITS.forEach((u, i) => {
  if (u.n !== i) fail(`unit ${u.id} has n=${u.n} but sits at position ${i}`);
  u.items.forEach(it => {
    if (ids.has(it.id)) fail(`duplicate item id ${it.id}`);
    ids.add(it.id);
    if (it.kind === 'c' && !it.q.includes('___')) fail(`cloze ${it.id} has no ___ gap`);
    if ((it.kind === 'mc' || it.kind === 'pi') && !(it.a >= 0 && it.a < it.opts.length)) fail(`${it.id} answer index out of range`);
    if (it.kind === 'w' && !(it.en && it.en.length)) fail(`${it.id} has no English meanings`);
  });
});
console.log(`${UNITS.length} units, ${ids.size} items`);

const norm = x => x.toLowerCase().replace(/[¿?¡!.,;:…"“”«»—–-]/g, ' ').replace(/\s+/g, ' ').trim();
STORIES.forEach(st => {
  const known = new Set();
  UNITS.filter(u => u.n <= st.after).forEach(u => u.items.forEach(it => (it.forms || []).forEach(f => known.add(f))));
  const toks = norm(st.text).split(' ');
  const unk = toks.filter(t => !known.has(t) && !(st.free || []).includes(t));
  const pct = 100 * (1 - unk.length / toks.length);
  console.log(`${st.id} (after unit ${st.after}): ${pct.toFixed(1)}% known${unk.length ? ' · unknown: ' + [...new Set(unk)].join(' ') : ''}`);
});
console.log('Note: past-tense forms of known verbs count as known in the app once Units 17/18 are reached, so st13 reads higher there.');
process.exit(problems ? 1 : 0);
