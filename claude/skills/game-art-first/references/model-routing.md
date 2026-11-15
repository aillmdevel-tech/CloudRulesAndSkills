# Who does what (quality first, savings second)

**Lead, Opus high (do it yourself):** audit + master plan, reference analysis conclusions, style decisions, map/location layout, modelling of key objects and hero assets, camera, collisions/physics design, core mechanics code, visual comparison verdicts, anything ambiguous.

**Opus medium (execute a ready plan):** implementing a planned mechanic with clear criteria, UI integration, importers following `ASSET_MANIFEST.md`, fixing listed diffs after comparison.

**Sonnet / low (mechanical, independent, easy to check):** build/tsc/smoke/moderator runs (`game-autotest`), renames and file moves, batch material/pivot fixes by a script, GLB exports by recipe, docs/state updates, repetitive modules from a template, screenshot capture.

Delegate only when: the task is independent, has a written spec + done-criteria + verification command, touches files nobody else edits. Subagent brief = goal, files, criteria, command to verify, "report in ≤10 lines". Result is checked by the lead (diff or output), not taken on faith.
Never delegate: design choices, anything where the reference interpretation matters, final approval.
Sessions for large stages: new chat per stage with `chat-handoff`; one lead at a time on the same files.
