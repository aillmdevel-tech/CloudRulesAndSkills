#!/usr/bin/env python3
"""Build the curated UIFX sound library from sources/ (Kenney CC0 packs + synth_sounds.py output).

usage: python3 tools/build_sounds.py            (run from UIFX/)
Writes sounds/<id>.ogg (Opus) + sounds/<id>.mp3, sounds/sounds.json (runtime manifest)
and SOUND_CREDITS.md. Each file: leading silence trimmed, peak-normalised to -1 dBFS, mono.
Loudness balance between sounds lives in the manifest `volume`, not in the files.
To add a sound: add a row to SOUNDS, re-run. Only add sounds whose licence you have verified.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
OUT = os.path.join(ROOT, "sounds")

LIC = {
    "kenney_interface-sounds": ("Kenney — Interface Sounds 1.0", "https://kenney.nl/assets/interface-sounds"),
    "kenney_ui-audio": ("Kenney — UI Audio (UI SFX Set)", "https://kenney.nl/assets/ui-audio"),
    "kenney_digital-audio": ("Kenney — Digital Audio", "https://kenney.nl/assets/digital-audio"),
    "synth": ("GameFactory synth (tools/synth_sounds.py)", "original"),
}

# id, category, source pack, file, default volume (0..1), pitch variation (+-semitones), description
SOUNDS = [
    ("hover", "ui", "kenney_ui-audio", "rollover2.ogg", 0.35, 1.0, "короткий мягкий hover"),
    ("hover_alt", "ui", "kenney_interface-sounds", "select_001.ogg", 0.3, 1.0, "hover, более 'цифровой'"),
    ("hover_bubble", "ui", "synth", "bubble_hover.wav", 0.35, 1.5, "пузырьковый hover (мультяшный)"),
    ("click", "ui", "kenney_interface-sounds", "click_003.ogg", 0.6, 0.8, "сухой клик"),
    ("click_alt", "ui", "kenney_interface-sounds", "click_004.ogg", 0.6, 0.8, "клик, вариант"),
    ("click_soft", "ui", "kenney_ui-audio", "click1.ogg", 0.7, 0.8, "мягкий клик"),
    ("jelly_click", "ui", "synth", "jelly_click.wav", 0.55, 1.0, "желейное 'боинг'-нажатие"),
    ("jelly_release", "ui", "synth", "jelly_release.wav", 0.4, 1.0, "отпускание желейной кнопки"),
    ("squish", "ui", "synth", "squish.wav", 0.55, 1.5, "резиновое сжатие (squash)"),
    ("select", "ui", "kenney_interface-sounds", "select_002.ogg", 0.5, 0.5, "выбор пункта"),
    ("toggle_on", "ui", "kenney_interface-sounds", "toggle_001.ogg", 0.55, 0, "переключатель вкл"),
    ("toggle_off", "ui", "kenney_interface-sounds", "toggle_002.ogg", 0.5, 0, "переключатель выкл"),
    ("tick", "ui", "kenney_interface-sounds", "tick_002.ogg", 0.4, 1.0, "тик (слайдер, скролл)"),
    ("tick_soft", "ui", "synth", "tick_soft.wav", 0.35, 1.0, "мягкий тик"),
    ("back", "ui", "kenney_interface-sounds", "back_001.ogg", 0.6, 0, "назад"),
    ("open", "window", "kenney_interface-sounds", "maximize_008.ogg", 0.5, 0, "открытие окна"),
    ("close", "window", "kenney_interface-sounds", "minimize_008.ogg", 0.5, 0, "закрытие окна"),
    ("open_alt", "window", "kenney_interface-sounds", "open_001.ogg", 0.5, 0, "открытие, коротко"),
    ("close_alt", "window", "kenney_interface-sounds", "close_001.ogg", 0.5, 0, "закрытие, коротко"),
    ("pop", "window", "synth", "pop.wav", 0.5, 1.5, "pop для Pop In"),
    ("whoosh_in", "window", "synth", "whoosh_in.wav", 0.45, 1.0, "whoosh — вылет панели"),
    ("whoosh_out", "window", "synth", "whoosh_out.wav", 0.4, 1.0, "whoosh — уход панели"),
    ("drop", "window", "kenney_interface-sounds", "drop_002.ogg", 0.55, 1.0, "drop / упало в слот"),
    ("notify", "feedback", "kenney_interface-sounds", "bong_001.ogg", 0.55, 0, "уведомление"),
    ("notify_chime", "feedback", "synth", "notify_chime.wav", 0.45, 0, "уведомление-колокольчик"),
    ("notify_glass", "feedback", "kenney_interface-sounds", "glass_002.ogg", 0.5, 0, "стеклянный дзынь"),
    ("success", "feedback", "kenney_interface-sounds", "confirmation_001.ogg", 0.55, 0, "успех"),
    ("success_chime", "feedback", "synth", "success_chime.wav", 0.5, 0, "успех, колокольчик"),
    ("success_big", "feedback", "kenney_interface-sounds", "confirmation_004.ogg", 0.55, 0, "успех, длиннее"),
    ("error", "feedback", "kenney_interface-sounds", "error_004.ogg", 0.5, 0, "ошибка, коротко"),
    ("error_soft", "feedback", "synth", "error_soft.wav", 0.5, 0, "мультяшное 'не-а'"),
    ("error_buzz", "feedback", "kenney_interface-sounds", "error_007.ogg", 0.45, 0, "ошибка, жужжание"),
    ("question", "feedback", "kenney_interface-sounds", "question_001.ogg", 0.5, 0, "вопрос / подтверждение"),
    ("coin", "reward", "synth", "coin.wav", 0.45, 0.5, "монета"),
    ("counter_tick", "reward", "synth", "counter_tick.wav", 0.3, 0.3, "тик счётчика при накрутке цифр"),
    ("reward", "reward", "synth", "reward.wav", 0.5, 0, "награда, арпеджио"),
    ("reward_alt", "reward", "kenney_digital-audio", "powerUp7.ogg", 0.45, 0, "награда, ретро power-up"),
    ("sparkle", "reward", "synth", "sparkle.wav", 0.4, 0, "блёстки"),
    ("confetti", "reward", "synth", "confetti.wav", 0.5, 0, "хлопушка + блёстки"),
    ("level_up", "reward", "synth", "level_up.wav", 0.55, 0, "повышение уровня"),
    ("level_up_alt", "reward", "kenney_digital-audio", "powerUp11.ogg", 0.45, 0, "level up, ретро"),
    ("level_up_retro", "reward", "kenney_digital-audio", "threeTone1.ogg", 0.45, 0, "три тона вверх"),
    ("unlock", "reward", "kenney_digital-audio", "pepSound3.ogg", 0.45, 0, "разблокировка"),
]


def ff(*args):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr)


def peak_db(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "volumedetect", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"max_volume: ([-0-9.]+) dB", r.stderr)
    return float(m.group(1)) if m else 0.0


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return round(float(r.stdout.strip() or 0), 3)


def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_tmp.wav")
    manifest = {"version": 1, "format": ["ogg", "mp3"], "sounds": {}}
    credits = {}
    for sid, cat, pack, fname, vol, pvar, desc in SOUNDS:
        src = os.path.join(SRC, pack, "Audio" if pack != "synth" else "", fname)
        if not os.path.exists(src):
            sys.exit("missing source " + src)
        ff("-i", src, "-ac", "1", "-af", "silenceremove=start_periods=1:start_threshold=-50dB", tmp)
        gain = -1.0 - peak_db(tmp)
        ff("-i", tmp, "-af", f"volume={gain:.2f}dB", "-c:a", "libopus", "-b:a", "96k", os.path.join(OUT, sid + ".ogg"))
        ff("-i", tmp, "-af", f"volume={gain:.2f}dB", "-c:a", "libmp3lame", "-q:a", "4", os.path.join(OUT, sid + ".mp3"))
        title, url = LIC[pack]
        manifest["sounds"][sid] = {
            "category": cat, "volume": vol, "pitchVariation": pvar, "duration": duration(tmp),
            "description": desc, "source": title, "sourceFile": fname, "sourceUrl": url, "license": "CC0-1.0",
        }
        credits.setdefault(title, []).append(f"{sid} ← {fname}")
        print(f"{sid:16} {cat:9} {duration(tmp):5.2f}s  gain {gain:+5.1f} dB  ← {pack}/{fname}")
    os.remove(tmp)
    with open(os.path.join(OUT, "sounds.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    lines = ["# UIFX — источники и лицензии звуков", "",
             "Все звуки библиотеки — **CC0 1.0** (общественное достояние): можно использовать в коммерческих играх,",
             "изменять, атрибуция не обязательна. Указывать Kenney в титрах — желательно (вежливость, не требование).", "",
             "Лицензии исходных паков лежат в `sources/<pack>/License.txt` (проверено 2026-11-04).",
             "Звуки `synth` созданы процедурно скриптом `tools/synth_sounds.py` для GameFactory и также отданы в CC0.", ""]
    for title, items in credits.items():
        url = next(u for t, u in LIC.values() if t == title)
        lines += [f"## {title}", f"Источник: {url}", "", *[f"- {i}" for i in items], ""]
    lines += ["## Не использовано (почему)",
              "- freesound.org — лицензия у каждого звука своя (CC0 / CC-BY / CC-BY-NC), скачивание требует аккаунта. Брать только CC0/CC-BY с записью автора и ссылки сюда.",
              "- pixabay.com — собственная Pixabay Content License (коммерция можно, но нельзя распространять звуки как самостоятельные файлы/паки) — для библиотеки-набора не подходит, в конкретную игру можно точечно.",
              "- elevenlabs.io — генерация платная/по тарифу; права на коммерческое использование зависят от плана. Только по согласованию.", ""]
    with open(os.path.join(ROOT, "SOUND_CREDITS.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n{len(SOUNDS)} sounds -> {OUT}")


if __name__ == "__main__":
    main()
