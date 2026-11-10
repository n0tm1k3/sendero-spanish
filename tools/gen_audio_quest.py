"""Generate audio for the Quest's dialogue lines and for single words you can tap.

Usage: same setup as gen_audio.py, then
  python3 tools/gen_audio_quest.py texts.json
where texts.json is {"lines": [...], "words": [...]}. Lines get all three voices (characters
pick their own); single words get one voice. Output: audio-es-quest.json, which the page
loads the first time the Quest tab or a word tap needs it.
"""
import base64, json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'audio-es-quest.json')

def main():
    src = json.load(open(sys.argv[1]))
    data = json.load(open(OUT)) if os.path.exists(OUT) else {}
    import soundfile as sf
    from kokoro_onnx import Kokoro
    tts = os.path.join(ROOT, 'tools', 'tts')
    k = Kokoro(os.path.join(tts, 'kokoro-v1.0.onnx'), os.path.join(tts, 'voices-v1.0.bin'))
    def mp3(text, voice):
        s, sr = k.create(text, voice=voice, speed=0.95, lang='es')
        w = tempfile.mktemp(suffix='.wav'); sf.write(w, s, sr)
        out = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', w, '-ac', '1', '-ar', '22050', '-b:a', '32k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
        os.remove(w); return base64.b64encode(out).decode()
    jobs = [(v, t) for t in src['lines'] for v in ('ef_dora', 'em_alex', 'em_santa')] + [('ef_dora', t) for t in src['words']]
    for i, (v, t) in enumerate(jobs):
        if v + '|' + t in data: continue
        data[v + '|' + t] = mp3(t, v)
        if i % 100 == 0:
            print(i, '/', len(jobs), flush=True); json.dump(data, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    json.dump(data, open(OUT, 'w'), separators=(',', ':'), ensure_ascii=False)
    print('done', len(data), 'clips', round(os.path.getsize(OUT) / 1e6, 1), 'MB')

if __name__ == '__main__':
    main()
