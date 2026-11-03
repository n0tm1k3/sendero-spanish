"""Generate missing Spanish audio clips with Kokoro TTS.

Usage:
  pip install kokoro-onnx soundfile   (and have ffmpeg and node on PATH)
  download kokoro-v1.0.onnx and voices-v1.0.bin from
  https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0 into tools/tts/
  python3 tools/gen_audio.py

Short texts (<= 90 characters) get three voices and go into audio-es-2.json.
Long texts (stories) get one voice and go into audio-es-stories.json, which the page loads on first use.
Clips are mono MP3, 22.05 kHz, 32 kbps, base64, keyed "voice|text".
Keep each JSON file under 16 MB; start an audio-es-3.json (and add it to the page's list) if needed.
"""
import base64, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICES = ['ef_dora', 'em_alex', 'em_santa']
FILES = ['audio-es.json', 'audio-es-2.json', 'audio-es-stories.json']


def main():
    texts = json.loads(subprocess.run(['node', os.path.join(ROOT, 'tools', 'content.js'), 'texts'], capture_output=True, text=True, check=True).stdout)
    have = set()
    data = {}
    for f in FILES:
        p = os.path.join(ROOT, f)
        data[f] = json.load(open(p)) if os.path.exists(p) else {}
        have |= {k.split('|', 1)[1] for k in data[f]}
    todo = [t for t in texts if t not in have]
    print(f'{len(texts)} texts, {len(todo)} missing audio')
    if not todo:
        return
    import soundfile as sf
    from kokoro_onnx import Kokoro
    tts = os.path.join(ROOT, 'tools', 'tts')
    k = Kokoro(os.path.join(tts, 'kokoro-v1.0.onnx'), os.path.join(tts, 'voices-v1.0.bin'))

    def mp3(text, voice):
        s, sr = k.create(text, voice=voice, speed=0.95 if len(text) <= 90 else 0.9, lang='es')
        w = tempfile.mktemp(suffix='.wav')
        sf.write(w, s, sr)
        out = subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', w, '-ac', '1', '-ar', '22050', '-b:a', '32k', '-f', 'mp3', '-'], capture_output=True, check=True).stdout
        os.remove(w)
        return base64.b64encode(out).decode()

    for t in todo:
        if len(t) <= 90:
            for v in VOICES:
                data['audio-es-2.json'][v + '|' + t] = mp3(t, v)
        else:
            data['audio-es-stories.json']['ef_dora|' + t] = mp3(t, 'ef_dora')
        print('  +', t[:60])
    for f in FILES[1:]:
        json.dump(data[f], open(os.path.join(ROOT, f), 'w'), separators=(',', ':'), ensure_ascii=False)
        print(f, round(os.path.getsize(os.path.join(ROOT, f)) / 1e6, 1), 'MB')


if __name__ == '__main__':
    sys.exit(main())
