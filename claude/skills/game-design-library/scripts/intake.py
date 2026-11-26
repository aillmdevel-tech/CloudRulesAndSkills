"""Intake of Alex's game recordings (video + voice) for DesignLibrary.
  python3 intake.py prep VIDEO OUTDIR [--lang ru] [--every 5]   # info + transcript + frames + sheets + voice moments
  python3 intake.py transcribe VIDEO OUT.json [--lang ru]
  python3 intake.py moments OUT.json                             # Alex's key phrases with timecodes
Transcription backends (first found): mlx_whisper (Apple Silicon), faster_whisper, whisper-cli (whisper.cpp, WHISPER_MODEL=path).
None installed -> prints the install command; the rest of prep still runs (frames, sheets)."""
import json, os, re, shutil, subprocess, sys

VF = os.path.expanduser('~/.claude/skills/game-reference-analysis/scripts/video_frames.py')
KEYS = {'фантазия': r'думаю.{0,20}(про|это)|игра про|хочу', 'понял': r'понял|понятно|надо (теперь|сделать)',
        'застрял': r'не понима|непонятн|где |что делать|застрял', 'результат': r'поменял|приятн|кайф|сочн|круто',
        'скучно': r'скучн|долго|надоел|ничего не (происход|почувств)', 'цель': r'на час|на неделю|сейчас хочу|дальше хочу|цель',
        'ui': r'кнопк|hud|худ|табло|окно|интерфейс|иконк|взять себе', 'хук': r'зацепил|чуть не вышел|затягива|вернусь',
        'деньги': r'купить|донат|реклам|робакс|ускор|платн'}


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def transcribe(video, out, lang='ru'):
    wav = out + '.wav'
    sh(['ffmpeg', '-y', '-v', 'error', '-i', video, '-vn', '-ac', '1', '-ar', '16000', wav])
    segs = None
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(wav, language=lang, path_or_hf_repo=os.environ.get('MLX_WHISPER_MODEL', 'mlx-community/whisper-large-v3-turbo'))
        segs = [dict(s=round(x['start'], 1), e=round(x['end'], 1), text=x['text'].strip()) for x in r['segments']]
    except ImportError:
        pass
    if segs is None:
        try:
            from faster_whisper import WhisperModel
            m = WhisperModel(os.environ.get('FW_MODEL', 'small'), compute_type='int8')
            segs = [dict(s=round(x.start, 1), e=round(x.end, 1), text=x.text.strip()) for x in m.transcribe(wav, language=lang)[0]]
        except ImportError:
            pass
    if segs is None and shutil.which('whisper-cli') and os.environ.get('WHISPER_MODEL'):
        r = sh(['whisper-cli', '-m', os.environ['WHISPER_MODEL'], '-l', lang, '-oj', '-of', out[:-5], wav])
        j = json.load(open(out[:-5] + '.json'))
        to_s = lambda t: sum(float(x) * k for x, k in zip(t.replace(',', '.').split(':'), (3600, 60, 1)))
        segs = [dict(s=round(to_s(x['timestamps']['from']), 1), e=round(to_s(x['timestamps']['to']), 1), text=x['text'].strip()) for x in j['transcription']]
    os.remove(wav) if os.path.exists(wav) else None
    if segs is None:
        print('NO TRANSCRIBER. Install one (after Alex OK):\n  /usr/local/bin/python3 -m pip install --user mlx-whisper   # Apple Silicon, model ~1.6 GB on first run\n'
              '  or: brew install whisper-cpp + model file, WHISPER_MODEL=/path/ggml-*.bin\n  or ask Alex for notes.md instead of voice.')
        return None
    json.dump(segs, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    open(out[:-5] + '.txt', 'w', encoding='utf-8').write('\n'.join(f"[{int(x['s'] // 60):02d}:{x['s'] % 60:04.1f}] {x['text']}" for x in segs))
    print('transcript:', out, len(segs), 'segments')
    return segs


def moments(segs):
    res = []
    for x in segs:
        tags = [k for k, rx in KEYS.items() if re.search(rx, x['text'].lower())]
        if tags: res.append(dict(t=x['s'], tags=tags, text=x['text']))
    return res


def main():
    a = sys.argv[1:]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    cmd = a[0] if a else ''
    if cmd == 'transcribe': transcribe(a[1], a[2], opt('--lang', 'ru'))
    elif cmd == 'moments':
        for m in moments(json.load(open(a[1]))): print(f"{m['t']:7.1f}s {','.join(m['tags']):20s} {m['text'][:110]}")
    elif cmd == 'prep':
        video, out = a[1], a[2]; os.makedirs(out, exist_ok=True)
        print(sh([sys.executable, VF, 'info', video]).stdout.strip())
        segs = transcribe(video, os.path.join(out, 'transcript.json'), opt('--lang', 'ru'))
        fr = os.path.join(out, 'frames'); sh([sys.executable, VF, 'sample', video, fr, '--every', opt('--every', '5'), '--width', '640'])
        r = sh([sys.executable, VF, 'sheet', fr, os.path.join(out, 'sheet.jpg'), '--cols', '6', '--thumb', '320'])
        print(r.stdout.strip()[-300:] or r.stderr.strip()[-300:])
        r = sh([sys.executable, VF, 'sample', video, os.path.join(out, 'first2min'), '--every', '3', '--end', '120', '--width', '640'])
        sh([sys.executable, VF, 'sheet', os.path.join(out, 'first2min'), os.path.join(out, 'first2min.jpg'), '--cols', '5', '--thumb', '384'])
        if segs:
            ms = moments(segs); json.dump(ms, open(os.path.join(out, 'moments.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
            print(f'voice moments: {len(ms)} → moments.json')
        print('ready:', out)
    else:
        print(__doc__)


main()
