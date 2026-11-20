#!/usr/bin/env python3
"""Memory Bank hook (глобальный, для всех проектов).

  start — SessionStart: если в проекте есть .claude/memory-bank/, подмешивает его файлы в контекст;
          если нет, а папка похожа на проект (.git / package.json / docs/PROJECT_STATE.md) — создаёт
          заготовки и просит заполнить их по `/save-context`.
  stop  — Stop: 1) дописывает автолог в .claude/memory-bank/session-log.md (время, сессия, изменённые
          файлы, начало последнего ответа); 2) если код менялся позже activeContext.md — один раз
          просит обновить activeContext.md и progress.md перед завершением.
Никогда не падает: любая ошибка = молча выйти с кодом 0.
"""
import json, os, subprocess, sys, time
from pathlib import Path

HOME = Path.home()
MB_FILES = ["projectbrief.md", "activeContext.md", "progress.md", "techContext.md"]
MAX_CTX = 14000  # символов в additionalContext


def read_input():
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def project_root(cwd):
    p = Path(cwd).resolve()
    if p == HOME or "scratch-workspaces" in str(p):
        return None
    for q in [p, *p.parents]:
        if q == HOME:
            break
        if (q / ".claude" / "memory-bank").is_dir():
            return q
    for q in [p, *p.parents]:
        if q == HOME:
            break
        if (q / ".git").exists() or (q / "package.json").exists() or (q / "docs" / "PROJECT_STATE.md").exists():
            return q
    return None


def detect_stack(root):
    pj = root / "package.json"
    if not pj.exists():
        return "не определён (нет package.json)"
    try:
        d = json.loads(pj.read_text())
        deps = {**d.get("dependencies", {}), **d.get("devDependencies", {})}
        keys = ["three", "playcanvas", "pixi.js", "phaser", "@dimforge/rapier3d-compat", "gsap", "vite", "typescript"]
        return ", ".join(f"{k} {deps[k]}" for k in keys if k in deps) or "package.json без известных игровых библиотек"
    except Exception:
        return "package.json не прочитан"


def bootstrap(root):
    mb = root / ".claude" / "memory-bank"
    mb.mkdir(parents=True, exist_ok=True)
    name = root.name
    tpl = {
        "projectbrief.md": f"# Project Brief — {name}\n\n_ЗАГОТОВКА: заполни через /save-context._\n\n- Что за игра/проект:\n- Главная цель:\n- Платформы:\n",
        "activeContext.md": f"# Active Context — {name}\n\n_ЗАГОТОВКА: заполни через /save-context._\n\n## Текущая задача\n\n## Последние изменения\n\n## Следующие шаги\n",
        "progress.md": f"# Progress — {name}\n\n## Сделано\n\n## Осталось\n",
        "techContext.md": f"# Tech Context — {name}\n\n- Стек (из package.json): {detect_stack(root)}\n\n## Архитектура\n\n## Ограничения\n",
    }
    for f, txt in tpl.items():
        p = mb / f
        if not p.exists():
            p.write_text(txt)


def cmd_start(inp):
    root = project_root(inp.get("cwd") or os.getcwd())
    if not root:
        return
    mb = root / ".claude" / "memory-bank"
    created = False
    if not mb.is_dir():
        bootstrap(root)
        created = True
    parts = []
    for f in MB_FILES:
        p = mb / f
        if p.exists():
            parts.append(f"===== {f} =====\n{p.read_text()[:4500]}")
    head = (
        "MEMORY BANK (автозагрузка хуком). Правило проекта: это восстановленный контекст, "
        "после крупного шага сам обновляй activeContext.md и progress.md.\n"
    )
    if created:
        head += ("Memory Bank в этом проекте только что создан как ЗАГОТОВКА: в начале работы "
                 "выполни /save-context, чтобы заполнить его фактами проекта.\n")
    ctx = (head + "\n".join(parts))[:MAX_CTX]
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}}, ensure_ascii=False))


def git(root, *args):
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=8).stdout
    except Exception:
        return ""


def last_assistant_text(path):
    try:
        last = ""
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if o.get("type") != "assistant":
                    continue
                c = (o.get("message") or {}).get("content")
                if isinstance(c, list):
                    t = " ".join(b.get("text", "") for b in c if isinstance(b, dict) and b.get("type") == "text").strip()
                    if t:
                        last = t
                elif isinstance(c, str) and c.strip():
                    last = c.strip()
        return " ".join(last.split())[:300]
    except Exception:
        return ""


def cmd_stop(inp):
    root = project_root(inp.get("cwd") or os.getcwd())
    if not root:
        return
    mb = root / ".claude" / "memory-bank"
    if not mb.is_dir():
        bootstrap(root)
    ac = mb / "activeContext.md"
    changed = []
    for line in git(root, "status", "--porcelain").splitlines():
        rel = line[3:].strip().strip('"')
        if " -> " in rel:
            rel = rel.split(" -> ")[-1]
        if not rel or rel.startswith(".claude/memory-bank") or rel.startswith(("dist/", "node_modules/")):
            continue
        changed.append(rel)
    # автолог
    log = mb / "session-log.md"
    stamp = time.strftime("%Y-%m-%d %H:%M")
    sid = (inp.get("session_id") or "")[:8]
    files = ", ".join(changed[:8]) + (f" (+{len(changed) - 8})" if len(changed) > 8 else "")
    entry = f"- {stamp} · сессия {sid} · изменено: {files or '—'} · итог: {last_assistant_text(inp.get('transcript_path') or '') or '—'}\n"
    prev = log.read_text().splitlines(keepends=True) if log.exists() else ["# Session log (автолог Stop-хука)\n\n"]
    if not prev or not prev[0].startswith("#"):
        prev.insert(0, "# Session log (автолог Stop-хука)\n\n")
    prev.append(entry)
    log.write_text("".join(prev[:2] + prev[2:][-60:]))  # шапка + последние 60 записей
    # напоминание: один раз, если код новее activeContext.md
    if inp.get("stop_hook_active"):
        return
    if not ac.exists() or not changed:
        return
    ac_m = ac.stat().st_mtime
    newer = []
    for rel in changed:
        fp = root / rel
        try:
            if fp.is_file() and fp.stat().st_mtime > ac_m:
                newer.append(rel)
        except Exception:
            pass
    if newer:
        reason = ("Memory Bank устарел: файлы менялись позже activeContext.md (" + ", ".join(newer[:5]) +
                  "). Коротко обнови .claude/memory-bank/activeContext.md (текущая задача, что изменено, следующий шаг) "
                  "и progress.md, затем заверши ответ.")
        print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    inp = read_input()
    try:
        if mode == "start":
            cmd_start(inp)
        elif mode == "stop":
            cmd_stop(inp)
    except Exception:
        pass


if __name__ == "__main__":
    main()
