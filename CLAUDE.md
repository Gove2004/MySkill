# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This is a monorepo of personal Claude Code skills. Each subdirectory is an independently installable skill. There is no build step, no test suite, and no shared code between skills.

## How skills work

A skill is a directory containing `SKILL.md` with YAML frontmatter:

```yaml
---
name: skill-name          # must match directory name
description: ...          # the ONLY trigger mechanism — include keywords in both English and Chinese
---
```

Claude decides whether to invoke a skill based solely on `description`. Write it to be slightly over-triggered rather than under-triggered. Mention concrete trigger phrases ("send an email", "发邮件", "parse this PDF").

## Architecture rules

- **No shared code.** Every skill is self-contained. Even `_load_env()` is copied independently into each skill that needs it — there is no common library.
- **Standard library first.** Scripts under `scripts/` use Python stdlib unless a third-party package is unavoidable.
- **`.env` never committed.** Secrets go in `.env` (gitignored). Templates go in `.env.example` (committed, with placeholder values). Scripts read config via `_load_env()` — see `ENV.md` for the copy-paste template.
- **`bundled_addons/` is third-party code.** Never modify files under any skill's `bundled_addons/` directory.
- **`references/` is supplementary.** Long reference material (templates, examples, language codes) lives here so `SKILL.md` stays under ~500 lines.
- **Not every skill needs scripts.** Some skills are pure instructions + reference templates (e.g., `html-presentation/` only has `SKILL.md` + `references/template.html`). This is fine — Claude generates output directly from the instructions.
- **`distribute.bat` auto-discovers skills.** It scans for subdirectories containing `SKILL.md` — no hardcoded list. When creating a new skill, no script changes are needed; it will be picked up automatically.

## Creating or editing a skill

- **New skill:** Follow `NEW.md` — it has the directory template, SKILL.md template, naming conventions, and a checklist. Read it before starting.
- **Adding config:** Follow `ENV.md` — create `.env.example`, copy `_load_env()` into the script, confirm `.gitignore` excludes `.env`.
- **Editing existing skills:** Make surgical changes. Do not refactor adjacent code. Match existing style. Update `SKILL.md` if command paths, config keys, or behavior changes.
- **After changes:** Run through the `NEW.md` checklist to verify nothing broke.

## Naming conventions

| Thing | Rule | Example |
|-------|------|---------|
| Directory | lowercase + hyphens | `pdf-to-markdown` |
| `name` in SKILL.md | same as directory | `pdf-to-markdown` |
| Python scripts | lowercase + underscores | `send_mail.py` |
| Config keys | UPPER_SNAKE_CASE | `MINERU_TOKEN` |

## When NOT to do something

- Do not create shared/utility modules — each skill stands alone.
- Do not hardcode specific vendors, models, or paths in docs when they're configurable via `.env`.
- Do not add features, abstractions, or error handling beyond what was requested.
- Do not "improve" code in skills you weren't asked to touch.