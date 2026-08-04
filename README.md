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

### Analytics (JSON-based)

Each of these requires a customer JSON export in `data/input/`. `analytics-preflight` runs automatically before any of them — it resolves which file to use and routes to the right skill.

| Skill | Use |
|-------|-----|
| `/analytics-run <hint>` | Full report — all 8 phases, 3 output files |
| `/analytics-quickcheck <hint>` | Pre-call health check — traffic, formats, top bandwidth assets, cache. State only, no recommendations |
| `/analytics-compare <hint>` | Period-over-period diff — equal-duration exports, any date range. Factual, no external inference |
| `/analytics-report-edit <hint>` | Safe edits to a finished customer report — no re-run |
| `/clear-analytics-data` | Clears `data/input/` and `data/extracted/` for a fresh testing round. Never touches `data/output/` |

### URL, domain, and IP tools

These work on a URL, domain, or IP directly — no JSON needed, no preflight.

| Skill | Use |
|-------|-----|
| `/url-check <url>` | Delivery vendor, format served, cache HIT/MISS, vary headers, and origin hosting — all from one curl |
| `/ik-debug <url> [runs]` | Debug an ImageKit URL with `ik-debug=true` — latency, transformation time, ik-error. Default 3 runs |
| `/transform-test <url>` | Interactively test transforms on an IK image URL — format, resize, server timing |
| `/ip-lookup <ip> [ip2...]` | Look up IPs via ipinfo.io and classify — CDN, cloud, residential ISP, VPN/proxy, bot |
| `/origin-vendor <domain>` | Resolve a domain to its hosting vendor via dig + ipinfo.io |
| `/imagekit-cname-check <domain> [domain2...]` | Check if a domain is CNAME'd to ImageKit and which endpoint it points to |
| `/custom-domain-request <domain> <clientNumber> [imagekitID]` | Check custom domain DNS state and produce the right message — internal activation request or customer DNS fix |

---

## Getting Started

First time? Follow **[setup/installation.md](./setup/installation.md)** to install Node.js, VS Code, Claude Code, and Python. Takes about 10 minutes and only needs to be done once.

---

## How to Use

> **Note:** `acme` is used throughout these examples as a placeholder for a customer account name. Replace it with the actual account name when running — e.g. if the account is Acme, your file would be `data/input/acme.json` and you'd run `/analytics-run acme`.

### 1. Add the customer's JSON

Drop the analytics JSON export from the ImageKit dashboard into `data/input/`:

```
data/input/acme.json
```

### 2. Open Claude Code in this project folder

```bash
cd "ImageKit Analytics Agent"
claude
```

### 3. Run the analysis

Use the skill directly:

```
/analytics-run acme
```

Or in plain language, optionally adding account context that should shape the findings or report tone:

> "Run the analysis for Acme — JSON is `data/input/acme.json`, March 2026."

Claude resolves the file, runs the extractor, works through all 8 phases, and saves the three output files — nothing to confirm mid-run.

### 4. Review the outputs

All three files land in `data/output/[account]/`:

```
data/output/acme/acme-march-2026-analysis.md
data/output/acme/acme-march-2026-trace.md
data/output/acme/acme-march-2026-customer-report.md
```

The **customer report** is what you bring to the call — it's also shown inline in the chat, copyable. The **analysis** and **trace** are reference — use them if you need to go deeper on a finding or verify a number.

For a faster pulse check instead of the full run, use `/analytics-quickcheck <hint>`.

---

## Learn More

- **Full phase-by-phase breakdown** (all 8 phases in detail) → [`project-docs/phases.md`](./project-docs/phases.md)
- **Folder structure & what's gitignored** → [`project-docs/architecture.md`](./project-docs/architecture.md)
- **Technical rules, thresholds, UA classification** → [`.claude/rules/guardrails.md`](./.claude/rules/guardrails.md). The one rule worth knowing up front: **check for data truncation before drawing any format or device conclusion** — high-traffic accounts often have dimensional breakdowns capping at 10–15% of total, and every other rule assumes that check happened first.
- **Codex / other coding assistant instructions** (work in progress) → [`AGENTS.md`](./AGENTS.md)
