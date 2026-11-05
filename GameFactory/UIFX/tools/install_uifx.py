#!/usr/bin/env python3
"""Copy UIFX into a game project (vendored copy — the game owns and may tweak it).

usage: install_uifx.py PROJECT_DIR [--sounds all|id1,id2,...] [--code-dest src/uifx]
                       [--audio-dest public/assets/audio/ui] [--force] [--dry-run]

- code: UIFX/src/* -> PROJECT/<code-dest>/   (TypeScript, zero deps, includes uifx.css)
- audio: chosen sounds (.ogg + .mp3) + a filtered sounds.json -> PROJECT/<audio-dest>/
- writes PROJECT/<audio-dest>/SOUND_CREDITS.md (CC0 sources) and UIFX_VERSION.txt
Refuses to overwrite an existing destination without --force.
"""
import argparse
import datetime
import json
import os
import shutil
import sys

UIFX = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--sounds", default="all")
    ap.add_argument("--code-dest", default="src/uifx")
    ap.add_argument("--audio-dest", default="public/assets/audio/ui")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    proj = os.path.abspath(a.project)
    if not os.path.isfile(os.path.join(proj, "package.json")) and not os.path.isdir(os.path.join(proj, "src")):
        sys.exit(f"{proj} doesn't look like a game project (no package.json / src)")
    code_dst = os.path.join(proj, a.code_dest)
    audio_dst = os.path.join(proj, a.audio_dest)
    for d in (code_dst, audio_dst):
        if os.path.exists(d) and os.listdir(d) and not a.force:
            sys.exit(f"refusing: {d} exists and is not empty (use --force to overwrite)")

    manifest = json.load(open(os.path.join(UIFX, "sounds", "sounds.json"), encoding="utf-8"))
    all_ids = list(manifest["sounds"])
    ids = all_ids if a.sounds == "all" else [s.strip() for s in a.sounds.split(",") if s.strip()]
    unknown = [i for i in ids if i not in manifest["sounds"]]
    if unknown:
        sys.exit(f"unknown sound ids: {unknown}\navailable: {', '.join(all_ids)}")

    print(f"code  -> {code_dst}")
    print(f"audio -> {audio_dst} ({len(ids)} sounds)")
    if a.dry_run:
        return
    if os.path.exists(code_dst):
        shutil.rmtree(code_dst)
    shutil.copytree(os.path.join(UIFX, "src"), code_dst)
    os.makedirs(audio_dst, exist_ok=True)
    for i in ids:
        for ext in ("ogg", "mp3"):
            shutil.copy2(os.path.join(UIFX, "sounds", f"{i}.{ext}"), audio_dst)
    sub = {**manifest, "sounds": {i: manifest["sounds"][i] for i in ids}}
    json.dump(sub, open(os.path.join(audio_dst, "sounds.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    shutil.copy2(os.path.join(UIFX, "SOUND_CREDITS.md"), audio_dst)
    stamp = f"GameFactory UIFX copied {datetime.date.today()} from {UIFX}\nsounds: {', '.join(ids)}\n"
    open(os.path.join(code_dst, "UIFX_VERSION.txt"), "w").write(stamp)
    print("done. Usage:\n  import './uifx/uifx.css';\n  import { createUIFX } from './uifx';\n"
          f"  const fx = await createUIFX({{ style: 'roblox-cartoon', soundsUrl: '{a.audio_dest.replace('public/', '/', 1)}/' }});")


if __name__ == "__main__":
    main()
