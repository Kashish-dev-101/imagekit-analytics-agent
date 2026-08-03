# CLAUDE.md — ImageKit Analytics Agent

This project is an AI agent for analysing ImageKit monthly analytics JSON exports. It takes raw account data and produces a full technical analysis + customer-facing talking points.


## What This Project Does

Given a customer's ImageKit analytics JSON export, the agent produces three outputs:

1. **Full technical analysis** — traffic overview, format delivery, UA breakdown, geography, top assets, transformation analysis, cache & errors, optimization opportunities
2. **Customer-facing report** — non-technical summary for account review calls
3. **Internal trace** — reasoning log showing what was read, calculated, and why things were flagged

Before analysis begins, the JSON is flattened into a compact text file by `agent/extract.py` — this reduces token usage and pre-sorts the data. The extracted file is cached in `data/extracted/` and reused on subsequent runs. See @agent/docs/extractor-reference.md for full details.

---

## Skills

The agent is driven by skills in `.claude/skills/`. **`analytics-preflight` runs first** on any analytics task — it resolves which file in `data/input/` to use (auto-pick when clear, ask when ambiguous) and routes to the right skill below.

| Skill | Use |
|-------|-----|
| `/analytics-run <hint>` | Full report — all 8 phases, 3 outputs |
| `/analytics-quickcheck <hint>` | Pre-call health check — traffic, formats, top bandwidth assets, cache, ABS. One MD, state only (no recommendations) |
| `/analytics-compare <hint>` | Period-over-period diff — equal-duration exports, any date range. Factual state only, no external inference |
| `/analytics-report-edit <hint>` | Safe edits to a customer report (no re-run) |
| `/ip-lookup <ip> [ip2 ip3...]` | Look up one or more IPs via ipinfo.io and classify each — CDN, cloud backend, residential ISP, VPN/proxy, bot |
| `/url-check <url>` | Check what a URL is serving — delivery vendor, format, cache HIT/MISS, vary headers, and origin hosting (dig + ipinfo) |
| `/ik-debug <url> [runs]` | Debug an ImageKit URL with `ik-debug=true` — latency, transformation time, ik-error, CloudFront PoP. Default 3 runs |
| `/transform-test <url>` | Interactively test transforms on an IK URL — baseline, auto format, resize, format override, server timing |
| `/origin-vendor <domain>` | Resolve a domain to its hosting/infrastructure vendor via dig + ipinfo.io |
| `/imagekit-cname-check <domain> [domain2...]` | Check if a domain (or several) is CNAME'd to ImageKit — resolves DNS and reports the endpoint id |
| `/custom-domain-request <domain> <clientNumber> [imagekitID]` | Check custom domain DNS state and produce the right message — internal activation request or customer-facing DNS fix |

---

## Output Delivery

**Full analysis (`/analytics-run`):**
- Create `data/output/[account]/` if it doesn't exist
- **Before writing new files:** check if `data/output/[account]/` already contains a prior review's 3 files (loose `[account]-[old-period]-*.md` directly in that folder, not already inside `archive/`). If so, move them into `data/output/[account]/archive/[old-period]/` first — create that folder if needed. This keeps only the current/latest review visible at the top level of each account's output folder, with history preserved underneath.
- Write all 3 new files into `data/output/[account]/`
- Show the customer report in the chat inside a copyable markdown block
- Do not ask where to save — it's already done

**Quickcheck and Compare:**
- Show the output in the chat inside a copyable markdown block
- Ask if the user wants to save it — only write the file if they say yes

**Report Edit (`/analytics-report-edit`):**
- Show the updated report in the chat inside a copyable markdown block
- Save back to the same file it edited — do not ask

---

## Folder Structure

```
.claude/
  CLAUDE.md            This file
  rules/guardrails.md  Technical rules Claude follows during analysis
  rules/side-notes.md  Unverified observations from real runs — review before promoting to guardrails
  skills/              Analytics skills (preflight, run, compare, quickcheck, report-edit)
  agents/              Reserved for subagents
  settings.json
agent/
  prompt.md            Main analysis prompt
  extract.py           Flattens JSON structure into compact text — no calculations, no conversions
  docs/                Reference docs for customer-facing recommendations
data/                  Customer data — gitignored, stays local
  input/               Drop customer JSONs here
  extracted/           Generated compact summaries
  output/              Analysis outputs organised by account
  reference-outputs/   Example analyses (Vax, Morphic, Popopo) — older single-file format
setup/
  installation.md      One-time setup guide — Node.js, VS Code, Claude Code, Python
archive/               Old prompt versions — gitignored
README.md              Human entry point
AGENTS.md              Cross-tool agent notes (Codex)
.mcp.json              MCP server configuration
```

**Gitignored:** `data/`, `archive/`

---

## Output Naming Convention

`[account]-[period]-[type].md`

| Type | Example |
|------|---------|
| Full analysis | `girnar-march-2026-analysis.md` |
| Customer report | `girnar-march-2026-customer-report.md` |
| Trace | `girnar-march-2026-trace.md` |
| Quickcheck | `girnar-march-2026-quickcheck.md` |
| Compare | `girnar-compare-feb-2026-vs-march-2026.md` |

---

## File Protection Rules

These rules apply at all times, regardless of what the user asks.

- **`[account]-[period]-trace.md` and `[account]-[period]-analysis.md` are read-only after initial generation.** Never modify them for any reason — not for edits, not for context updates, not for corrections — unless the user explicitly says they want to run a brand new analysis with new JSON data.
- **The only file that should be modified after initial generation is `[account]-[period]-customer-report.md`.** All post-analysis requests (edits, context additions, reprioritisation, tone changes) go there only.
- **When adding or changing anything in the customer report**, pull data from `[account]-[period]-analysis.md` and `[account]-[period]-trace.md` only. Do not re-read the JSON, do not re-run any analysis phase.
- **If a request is ambiguous** — e.g. "update the analysis", "can you change the findings", "revise the report" — do not touch any file. Ask first: *"Do you want to re-run the full analysis with new data, or make changes to the customer report only?"* Wait for the answer.
- **A new analysis is only triggered when** the user provides a new JSON file and explicitly asks to run the analysis.

---

## Key Technical Rules

@.claude/rules/guardrails.md

- **Check truncation first** — before drawing conclusions from dimensional breakdowns (formatWise, deviceDistribution, country), verify they sum close to `request.total`. If they cap at 10–15% of total, the data is truncated (known platform bug). Flag it prominently.

---

## Gists

Always create gists as **secret**. Never use `--public`. Default (`gh gist create` with no flag) = secret. Only use `--public` if the user explicitly asks.
