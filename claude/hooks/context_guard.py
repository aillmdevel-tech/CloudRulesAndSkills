#!/usr/bin/env python3
"""Context guard hook (GameFactory). stdlib only, never blocks, never fails the prompt.

  context_guard.py prompt   # UserPromptSubmit: measures context from the transcript; above the
                            # thresholds tells the model to run chat-handoff and offer a new chat
  context_guard.py start    # SessionStart (startup/resume/compact): if the project has
                            # docs/PROJECT_STATE.md, reminds the model to read it first

Auto-compact at 70% (settings env CLAUDE_AUTOCOMPACT_PCT_OVERRIDE). Handoff to a new chat after 2 compactions.
"""
import json
import os
import sys
import tempfile



def out(event, text):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}, ensure_ascii=False))


def context_tokens(path):
    """Prompt size of the last main-thread assistant turn = current context."""
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - 3_000_000))
            lines = f.read().decode("utf-8", "ignore").splitlines()
    except OSError:
        return 0, 0
    tokens, compactions = 0, 0
    for line in lines:
        if '"compact_boundary"' in line or '"isCompactSummary":true' in line:
            compactions += 1
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant" or d.get("isSidechain"):
            continue
        u = (d.get("message") or {}).get("usage") or {}
        t = u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
        if t:
            tokens = t
    return tokens, compactions


def once(session, key):
    """True the first time (session, key) is seen."""
    p = os.path.join(tempfile.gettempdir(), f"ctxguard-{session}-{key}")
    if os.path.exists(p):
        return False
    try:
        open(p, "w").close()
    except OSError:
        pass
    return True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "prompt"
    try:
        data = json.load(sys.stdin)
    except ValueError:
        data = {}
    session = str(data.get("session_id", "x"))[:40]
    cwd = data.get("cwd") or os.getcwd()

    if mode == "start":
        state = os.path.join(cwd, "docs", "PROJECT_STATE.md")
        if os.path.isfile(state):
            src = data.get("source", "")
            extra = " Контекст был сжат — детали из чата могли потеряться, опирайся на этот файл." if src == "compact" else ""
            out("SessionStart", f"[context-guard] {state}: начни с актуального блока и читай детали по задаче. "
                                f"«Продолжи работу» → chat-handoff.{extra}")
        return

    tokens, compactions = context_tokens(data.get("transcript_path", ""))
    k = tokens // 1000
    # Сжатие делает сам Claude Code на 70% окна (env CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=70).
    # Новый чат — только после 2 сжатий; до этого работаем в том же чате.
    if compactions >= 2 and once(session, "handoff"):
        out("UserPromptSubmit",
            f"[context-guard] Контекст ~{k}k токенов, сжатий: {compactions}. Сначала ответь на запрос, затем: "
            f"скилл chat-handoff (режим сохранения) → обнови docs/PROJECT_STATE.md (включая визуальные решения "
            f"и что сверено с референсом) → сам запусти новую сессию в той же папке с брифом «продолжи работу» "
            f"и сообщи Alex одной строкой. Эту сессию после передачи не продолжай.")
    elif compactions == 1 and once(session, "c1"):
        out("UserPromptSubmit",
            "[context-guard] Было 1 сжатие. Держи docs/PROJECT_STATE.md актуальным (решения, визуальный стиль, "
            "что сверено) — после второго сжатия будет передача в новый чат.")

if __name__ == "__main__":
    try:
        main()
    except Exception:  # a hook must never break the session
        pass
