# Sendero Spanish

A Spanish course in a single web page, built around what research says works: spaced retrieval, short explicit grammar followed by lots of input, graded reading, and a daily plan split across listening, reading, speaking, writing and focused study.

It's a personal project. Suggestions and pull requests from people and AI assistants are welcome. Start with [AGENTS.md](AGENTS.md).

## What's in it

- **20 units** (A1 to early A2): sounds, survival phrases, ser and estar, the present tense, routines, getting around, food, stem-changing verbs, object pronouns, the preterite and imperfect, por and para. About 500 items with audio from three voices.
- **A daily plan** of 30 to 120 minutes, timed by activity, with a phase roadmap measured in hours (A1 ≈ 100 h, A2 ≈ 200 h, B1 ≈ 400 h).
- **Spaced repetition** with FSRS, difficulty that adapts toward about 85% accuracy, and typed recall rather than just recognition.
- **Reading:** 14 graded stories, plus a daily story written by Claude to the learner's vocabulary (on claude.ai only). Tap any word to see its meaning and add it to your reviews.
- **Quest:** the course as a pixel RPG. Seven towns, a mentor for every unit, and a boss guarding each road. Battles in tall grass are your due reviews, on the same cards, so playing counts as studying.
- **Play:** a daily puzzle where you sort 16 words into four groups, and a 60-second speed round.
- **Speak & write:** shadowing practice, and writing prompts with corrections from Claude (on claude.ai only).
- **Method tab:** each mechanic with the study behind it.

## Use it offline

The live copy at https://n0tm1k3.github.io/sendero-spanish/ installs as an app (in Chrome, Edge or Brave: the install icon in the address bar, or the browser menu). Once installed it works with no internet, audio included. Progress is saved in the browser on that computer.

To move progress between copies (claude.ai, the installed app, another computer), use **Save progress file** and **Load progress file** on the Today tab. Loading merges: for each card, the most recent review wins.

The Claude-powered features (daily story, writing feedback, account sync) only work in the version published on claude.ai.

## Run it locally

```bash
python3 -m http.server
# open http://localhost:8000
```

## Files

- `index.html`: the whole app
- `audio-es.json`, `audio-es-2.json`: word and sentence clips (Kokoro TTS, three voices)
- `audio-es-stories.json`: story narration, loaded on first use
- `manifest.webmanifest`, `sw.js`, `icon-*.png`: makes the page installable and offline-capable
- `tools/`: content checks, audio generation, browser smoke test
