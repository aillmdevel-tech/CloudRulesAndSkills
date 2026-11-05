---
name: grill-me
description: A relentless interview to sharpen a plan or design.
disable-model-invocation: true
---

<!-- GameFactory local patch (2026-11-04): upstream body was `Call the Skill tool with "grilling".`,
     which fails because disable-model-invocation blocks that Skill-tool call
     (https://github.com/mattpocock/skills/issues/1052). The flag is kept: this skill stays
     user-only (/grill-me); the auto-invocable path is the `grilling` skill. -->

Read `~/.claude/skills/grilling/SKILL.md` with the Read tool and follow its instructions exactly, as if that skill had been invoked.
