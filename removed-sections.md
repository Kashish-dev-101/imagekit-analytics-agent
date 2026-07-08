# Removed Sections Archive

Sections removed from `.claude/CLAUDE.md` — kept here for reference in case needed later.

---

## How to Use (removed 2026-06-23)

**Why removed:** Already fully covered in README.md (lines 37–83) with more detail and examples. Duplicating human onboarding docs in CLAUDE.md adds tokens with no behavioral benefit — Claude doesn't need to know how a CSM opens the terminal.

### Original content

1. Drop the customer's analytics JSON(s) into `data/input/` (gitignored — safe for customer data)
2. Open Claude Code in this project root
3. Invoke a skill with a hint, e.g. `/analytics-run kalki`
4. The skill lists matching files in `data/input/`, you confirm which to use; it confirms the period read from the data, then runs
5. The output is presented inline + copyable; you tell it the folder to save to

---

## How Claude Should Handle a Run Request (removed 2026-06-23)

**Why removed:** Multi-step procedure — Claude Code docs say these belong in skills, not CLAUDE.md. The `analytics-preflight` skill already owns input resolution and routing. Keeping this in CLAUDE.md created a second source of truth that could diverge from the skill.

### Original content

1. **Resolve input** — list `data/input/`, filter by the hint, and confirm the file(s) with the user. Confirm the period read from the JSON date range. Do not guess silently.
2. **Check for an existing extract** — `data/extracted/[account]-extracted.txt`. If present, use it. If not, run:
   ```bash
   python3 agent/extract.py data/input/[filename].json > data/extracted/[account]-extracted.txt
   ```
3. **Read `agent/prompt.md`** — the full analysis prompt. Follow it exactly, phase by phase.
4. **Read `.claude/rules/guardrails.md`** — as instructed at the top of the prompt.
5. **Incorporate any account context** the user provided.
6. **Build the three outputs in `data/output/`** as the working location, then deliver per Output Delivery.

---

## Operating Mode (removed 2026-06-23)

**Why removed:** Soft enforcement only — Claude follows explicit user instructions over background rules. CSMs don't know `prompt.md` exists so accidental edits aren't a real risk. The global workspace rule ("never edit any agent's prompt.md without the user initiating the change") already covers the real concern. Section added noise for CSM users without providing reliable protection.

### Original content

Default to **CSM Mode**.

In CSM Mode:
- Do not edit `agent/prompt.md`, `.claude/rules/guardrails.md`, `.claude/CLAUDE.md`, `AGENTS.md`, or prompt-development files in `archive/`
- Run analyses from `data/input/`
- Present outputs inline + copyable and save to the folder the user names (see Output Delivery)
- Only edit existing `[account]-customer-report.md` files for post-analysis changes

Only switch to **Prompt Maintainer Mode** when the user explicitly asks for prompt-development work or explicitly authorizes editing prompt/rules/notes files.

In Prompt Maintainer Mode:
- Read `archive/test/customer-report-prompt-notes.md` before starting prompt work
- Use the `Next Up` section as the task list
- Update that same notes file in place after work
