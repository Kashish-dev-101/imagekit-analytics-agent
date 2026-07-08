# ImageKit Analytics Agent

A Claude Code agent for analysing ImageKit monthly analytics JSON exports. Drop in a customer's data, ask Claude to run the analysis, and get a full technical analysis plus a customer-facing report ready for the account review call.

---

## How It Works

![Analytics Agent overview](https://ik.imagekit.io/Kashish12345/Agents/Analytics/analytics_agent_overview_v2_6_IJymqGz.png)

![Analytics Agent run path](https://ik.imagekit.io/Kashish12345/Agents/Analytics/analytics_run_path_v3_pVMWccxvc.png)

---

## What It Produces

For each customer, the agent creates three files:

| File | Audience | Purpose |
|------|----------|---------|
| `[account]-[period]-analysis.md` | Internal | Full technical findings — every phase, every flag, all numbers |
| `[account]-[period]-trace.md` | Internal | Reasoning log — what was read, how calculations were done, why things were flagged |
| `[account]-[period]-customer-report.md` | Customer-facing | Non-technical summary for the account review call — what's working, what to fix, questions for the call |

---

## Skills

Each of these can be invoked directly, independent of a full run:

| Skill | Use |
|-------|-----|
| `/analytics-run <hint>` | Full report — all 9 phases, 3 output files |
| `/analytics-quickcheck <hint>` | Pre-call health check — traffic, formats, device mix, cache. State only, no recommendations |
| `/analytics-compare <hint>` | Month-over-month diff between two exports |
| `/analytics-report-edit <hint>` | Safe edits to a finished customer report — no re-run |

`analytics-preflight` runs automatically before any of the above — it resolves which file in `data/input/` to use and routes to the right skill.

---

## Getting Started

First time? Follow **[setup/installation.md](./setup/installation.md)** to install Node.js, VS Code, Claude Code, and Python. Takes about 10 minutes and only needs to be done once.

---

## How to Use

### 1. Add the customer's JSON

Drop the analytics JSON export from the ImageKit dashboard into `data/input/`:

```
data/input/girnar.json
```

### 2. Open Claude Code in this project folder

```bash
cd "ImageKit Analytics Agent"
claude
```

### 3. Run the analysis

Use the skill directly:

```
/analytics-run girnar
```

Or in plain language, optionally adding account context that should shape the findings or report tone:

> "Run the analysis for Girnar — JSON is `data/input/girnar.json`, March 2026. This is a renewal call and they've been asking about bandwidth costs."

Claude resolves the file, runs the extractor, works through all 9 phases, and saves the three output files — nothing to confirm mid-run.

### 4. Review the outputs

All three files land in `data/output/[account]/`:

```
data/output/girnar/girnar-march-2026-analysis.md
data/output/girnar/girnar-march-2026-trace.md
data/output/girnar/girnar-march-2026-customer-report.md
```

The **customer report** is what you bring to the call — it's also shown inline in the chat, copyable. The **analysis** and **trace** are reference — use them if you need to go deeper on a finding or verify a number.

For a faster pulse check instead of the full run, use `/analytics-quickcheck <hint>`.

---

## Learn More

- **Full phase-by-phase breakdown** (all 9 phases in detail) → [`docs/phases.md`](./docs/phases.md)
- **Folder structure & what's gitignored** → [`docs/architecture.md`](./docs/architecture.md)
- **Technical rules, thresholds, UA classification** → [`.claude/rules/guardrails.md`](./.claude/rules/guardrails.md). The one rule worth knowing up front: **check for data truncation before drawing any format or device conclusion** — high-traffic accounts often have dimensional breakdowns capping at 10–15% of total, and every other rule assumes that check happened first.
- **Codex / other coding assistant instructions** (work in progress) → [`AGENTS.md`](./AGENTS.md)
