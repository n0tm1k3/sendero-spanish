# Working on Sendero (guide for AI assistants)

Sendero is a Spanish course for one adult English speaker (Latin American Spanish, starting from zero, aiming for 1–2 hours of study a day). Everything is in `index.html`: content, styles and logic, no build step. Read this file before changing anything.

## Ground rules

1. **Don't break saved progress.** Progress is stored by item id (`S.cards['hola:r']`). Never rename or delete an item id, never reuse one, and never change a unit's `n`. To retire an item, leave it in place. New units go at the end of `UNITS` with `n` equal to their position.
2. **Every mechanic needs a reason.** The course is built on published research; the Method tab lists the sources. If you add or change a mechanic, add an entry to `REFS` with a real, working link, or say in your PR that the evidence is thin.
3. **Spanish must be correct.** Neutral Latin American Spanish, with Spain variants noted where they differ. If you're not sure of a form or a usage, leave it out.
4. **Small, reviewable changes.** One idea per pull request. Describe what changed for the learner, not just the code.
5. **Keep it one file.** No frameworks, no build tools, no external scripts. Fonts come from Google Fonts; everything else is inline.
6. **Run the checks** (below) before you open a PR.

## How the page is organised (`index.html`)

| Section (search for the comment) | What it holds |
|---|---|
| `Sendero curriculum content` | `UNITS`: each unit has `id`, `n`, `title`, `es`, `why`, `lesson` notes and `items`. Then `ROADMAP` (locked future units) and `STORIES` (graded readers). |
| `FSRS` | The spaced-repetition scheduler (FSRS-6 default weights). |
| `text normalisation` | Answer checking: accents, articles, typos, slash answers like "el profesor / la profesora". |
| `Voice` | Plays pre-generated clips from the `audio-*.json` files, falling back to the device's Spanish voice. |
| `registry` / `state` | Turns items into cards; the saved state `S` and its migration (`migrate()`). |
| `learning model` / `buildSession` | Picks reviews and new cards, adapts difficulty toward ~85% accuracy. |
| `daily plan` | Minutes per activity, the phase roadmap, listening log and resources. |
| `reading` / `Claude:` | Past-tense recognition for coverage, tap-to-gloss, today's story, word lookups, writing feedback. |
| `play` | The daily grouping puzzle (`CATS`) and the 60-second speed round. |
| `speak & write` | Shadowing rounds and writing prompts (`WRITE_PROMPTS`). |
| `Sendero Quest` | The Quest tab: a pixel RPG on top of the same cards. `TOWNS` (maps, mentors, bosses, signs), then drawing, movement, dialogue, battles and the menu. |
| `views`, `session`, `events` | Rendering and click handling. |

### Item kinds

```js
W(id, 'el libro', ['book'], { noun: 'm', forms: ['libro', 'libros'], note, ex: [es, en], cog, ff })  // word: two cards, Spanish→English and English→Spanish
C(id, 'Yo ___ estudiante.', ['soy'], 'I am a student.', 'ser', 'yo → soy')                            // cloze: type the missing form
P(id, 'Soy de Vancouver.', PERSONS, 0, 'I’m from Vancouver.', 'soy can only be yo.')                    // structured input: choose who / what it means
M(id, 'María ___ de Perú.', ['es', 'está'], 0, 'Origin → ser.', 'María es de Perú.')                  // multiple choice (first option is not always right: set the index)
D(id, '¿Dónde vives?', 'Where do you live?')                                                           // dictation: hear it, type it (needs an audio clip)
```

`forms` lists every inflected form a learner will meet; story coverage and tap-to-gloss depend on it. Stories (`STORIES`) take `after` (unit number), `free` (names and cognates that count as known) and optional `gl` (glosses for the few words not taught yet). Aim for at least 95% known words at the unit the story unlocks.

### Runs in two places

- **On claude.ai** (the published artifact): progress syncs to the learner's account (`db` + `user` capabilities), and Claude writes the daily story and writing feedback (`sample` capability), all through `window.claude.use(...)`.
- **Anywhere else** (a local server, GitHub Pages, the installed offline app): `window.claude` is missing, so progress stays in the browser's localStorage and the Claude features show a message instead. The page then registers `sw.js` for offline use. Keep both paths working.
- **Progress files** (`mergeState`) move progress between copies. If you add a field to the saved state `S`, add it to `DEFAULT()` and decide how `mergeState` combines it.
- **Offline cache:** bump `VERSION` in `sw.js` whenever an audio file changes, or installed copies keep the old clips. New files the page needs offline go in `CORE` or `AUDIO` there.

### Sendero Quest (the Quest tab)

The game runs on the course's own cards: a battle is a review graded exactly like a session (`bAnswer` mirrors `answer`), so it updates `S.cards`, XP, the log, the streak and the Cards minutes. Its own state is `S.quest` (current town, position, flags, taught-but-untested cards, the learner's name).

- **One town per few units, in course order.** Each unit has exactly one mentor (`npcs[].unit`). Each town has a boss whose `focus` lists the units whose grammar it interleaves with vocabulary; beating it opens the east gate (`>`).
- **Maps are built in code** with `rect`, `at` and `house` on a 30×22 grid. The tile legend is at the top of `TOWNS`. Every character, sign, door, gate and patch of tall grass must be reachable on foot; check new maps for that.
- **Ids are saved.** Flags are keyed by town, NPC and boss ids (`met_luz`, `boss_espejo`, `visit_puerto`). Don't rename them.
- **Dialogue Spanish follows rule 3**, and should use words the learner has met by that unit. Unknown words are underlined and the English stays visible.
- New units need a mentor in the right town; a new town goes at the end of `TOWNS` and gets the previous town's east gate.
- **Buildings lead into the course.** `DOOR_ROOMS` maps each door to a room in `ROOMS` (stories, today's story, games, shadowing, writing, listening, the plan, the Diccionario). A room hands off to the course with `startBlock`, and a banner on the course page leads back. Every door must have a room.
- **The Diccionario** records each item the learner has beaten in battle (`S.quest.caught`). Creatures are drawn from the item id and grow with the card's stage, the same stages as the Garden.
- **Music** is generated with Web Audio (`MUSIC`): an original short loop per town plus battle and boss themes. It starts only after the learner presses Start on the title screen, stops when they leave the tab, and has an on/off switch (`S.quest.musicOn`).
- `window.senderoQuestDebug` exposes the game's state to browser tests.

## Checks

```bash
node tools/check.js          # content: ids, unit numbering, story coverage
python3 tools/gen_audio.py   # adds clips for any new Spanish text (see the script for setup)
node tools/smoke.js          # browser test of every tab; needs Playwright
```

Open the page locally with `python3 -m http.server` and go to http://localhost:8000. Opening the file directly won't load audio.

## Getting changes into the live app

The learner uses the copy published on claude.ai. After a change is merged here, the owner asks Claude to publish the repo's `index.html` and audio files to the Sendero Spanish artifact. Don't try to publish it yourself.
