# Сторонние скиллы

Установлены 2026-11-04 через официальный CLI `npx skills` (v1.7.6), глобально для Claude Code,
режим `--copy` (реальные файлы в `~/.claude/skills/`), телеметрия отключена (`DO_NOT_TRACK=1`).
Перед установкой прочитаны SKILL.md и все скрипты; установленные файлы сверены с ревью (`diff -r`).

| Набор | Скиллы | Источник (commit) | Заметки |
|---|---|---|---|
| PlayCanvas (официальные) | add-effects, apply-conventions, assemble-scene, bake-lighting, build-app, calibrate-model, configure-animation, find-examples, inspect-glb, inspect-runtime, light-scene, load-assets, override-shader-chunks, reduce-draw-calls, reuse-scripts, verify-pixels | playcanvas/skills (de7dac4) | скрипты: `inspect-glb/scripts/inspect.mjs` (офлайн, только чтение), `inspect-runtime/scripts/devtools-hook.js` |
| Anthropic | frontend-design, webapp-testing | anthropics/skills (ca45fc4) | webapp-testing требует Python Playwright (установлен user-wide) |
| Matt Pocock | grilling, grill-me | mattpocock/skills (4ae2317) | **grill-me пропатчен локально**, см. ниже |
| daymade | frontend-visual-qa | daymade/claude-code-skills (2fee8de) | сетевые запросы скриптов — только к указанному URL/allowlist |

Команды (то же делает `scripts/restore.sh`):

```bash
export DO_NOT_TRACK=1 DISABLE_TELEMETRY=1
npx -y skills@latest add playcanvas/skills -g -a claude-code --copy -y
npx -y skills@latest add anthropics/skills --skill frontend-design --skill webapp-testing -g -a claude-code --copy -y
npx -y skills@latest add mattpocock/skills --skill grill-me --skill grilling -g -a claude-code --copy -y
npx -y skills@latest add daymade/claude-code-skills --skill frontend-visual-qa -g -a claude-code --copy -y
```

Обновление: `npx -y skills@latest update -g` — **после него заново примени патч grill-me**
(или `scripts/restore.sh` перезапишет его из `backup/`).

## Патч grill-me (issue mattpocock/skills#1052, открыт на 2026-11-04)

Апстрим: `disable-model-invocation: true` + тело «Call the Skill tool with "grilling"». Флаг блокирует
именно этот вызов, поэтому `/grill-me` падает в обоих путях. Локальный патч сохраняет флаг
(grill-me остаётся только ручной командой `/grill-me`), а тело заменено на «прочитай
`~/.claude/skills/grilling/SKILL.md` и следуй ему». Автоматически используется `grilling`
(model-invocable). Ограничения Claude Code не обходятся.

## Не установлено (осознанно)

- **majidmanzarpour/threejs-game-skills** — ставить только при старте Three.js-проекта, выборочно и
  в проект. Ревью и команда: `~/.claude/skills/game-project-workflow/references/threejs-skills.md`.
  Генераторы (Tripo, Gemini, ElevenLabs) — платные внешние API, только с явного разрешения.
- Отдельные скиллы для IK/процедурной анимации, видеоанализа, диагностики — качественных
  проверенных не искал массово; покрыто собственными скиллами
  (`game-reference-analysis`, `game-project-workflow/references/procedural-motion.md`).
