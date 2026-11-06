---
name: chat-handoff
description: Use when the user is moving work to a new chat or resuming in one — "перехожу в новый чат", "собери контекст", "передай контекст", "сохрани контекст для нового чата", "подготовь передачу", "handoff", and in a fresh chat "продолжи работу", "продолжаем", "continue", "где мы остановились". Save mode writes an up-to-date docs/PROJECT_STATE.md in the project root so a new agent in the same folder understands everything; resume mode reads it and continues from the next step without asking for a re-brief. Also use at the end of a stage when the context is large (≥ ~150k tokens or after 2 compactions) to tell the user to switch chats.
---

# Chat handoff (save → new chat → «продолжи работу»)

Works in any project. The single source of truth is `docs/PROJECT_STATE.md` in the project root
(create `docs/` if missing). It describes the project *as it is now* — rewrite it, never append a log.
History belongs in the project's own chronology file (e.g. `docs/PROGRESS.md`) if it has one.

## Save mode («перехожу в новый чат», «собери контекст», …)

1. Finish or park the current edit so the code is consistent (don't leave a half-applied change; if
   you must, say exactly what is half-done in «Текущая задача»).
2. Collect facts, don't invent: `git status`, `git log --oneline -8`, `git remote -v`, current branch;
   what was done and verified in this chat (only what actually ran); user's rules and decisions said in
   this chat (they are lost otherwise — this is the most important part); reference paths used.
3. Write `docs/PROJECT_STATE.md` from [template.md](template.md). Rules:
   - Concrete and self-sufficient: absolute paths, file names, commands, URLs, numbers. A new agent with
     no access to this chat must be able to continue.
   - Separate facts from guesses ([H] / «гипотеза»). Mark what was not verified.
   - «Следующий шаг» = exact actions, not a vague goal. «Текущая задача» = what was in progress, which
     files were touched, what is left.
   - Keep it ~60–150 lines; link to other docs instead of copying them.
   - Never put passwords, tokens or keys in it.
4. Sync project docs that the handoff points to (e.g. outdated lines in the project `CLAUDE.md`,
   decisions file) — only short factual fixes.
5. Git: follow the project's rules (its `CLAUDE.md`). If they say to commit/push after stages, commit the
   state file with the work and push. If there are no rules or the user hasn't allowed commits, leave it
   uncommitted — the file is already on disk, the new chat will read it — and say so.
6. Reply briefly: what was saved, and the exact instruction:
   «Открой новый чат в папке `<абсолютный путь проекта>` и напиши: **продолжи работу**».
   Don't start new work after a save.

## Resume mode (fresh chat: «продолжи работу», «продолжаем», …)

1. Read `docs/PROJECT_STATE.md` fully and the project `CLAUDE.md` (auto-loaded). Then `git status` and
   `git log --oneline -5`; if they disagree with the file (newer commits, unexpected changes), trust git
   and mention the mismatch in one line.
2. Read other docs only as the next step needs them — not the whole project.
3. One short line to the user: where we are and what you're doing now. Then do «Следующий шаг».
   Ask only if the file lists open questions that block that step, or the step needs the user's
   material (files, approval).
4. No `PROJECT_STATE.md`: say so, look for the nearest equivalent (`docs/PROGRESS.md`, `README`,
   `CLAUDE.md`, git log), summarise in 3–5 lines and ask what to continue.

## When to propose switching chats yourself

At the end of each stage / fix batch (before the commit), check context usage (the session usage tool,
e.g. `get_usage`, if available). Propose switching — after running Save mode — when any holds:
≥ ~150k tokens used, the chat was compacted 2+ times, or the next step is a big new stage. Otherwise
keep the state file current anyway, so a switch at any moment loses nothing. Don't rely on `/compact`
for continuity: its summary is lossy.
