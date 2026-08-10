# ImageKit Analytics Agent

Drop in a customer's analytics JSON, run one command, and get a full technical analysis plus a customer-facing report — ready for the account review call.

---

## How It Works

![Analytics Agent overview](https://ik.imagekit.io/Kashish12345/Agents/Analytics/analytics_agent_overview_v2_6_IJymqGz.png)

![Analytics Agent run path](https://ik.imagekit.io/Kashish12345/Agents/Analytics/analytics_run_path_v3_pVMWccxvc.png)

---

## What You Get

For each customer, the agent creates three files:

| File | Who it's for | What it is |
|------|-------------|------------|
| `[account]-[period]-analysis.md` | You | Full technical findings — every metric, every flag |
| `[account]-[period]-trace.md` | You | Reasoning log — how Claude worked through the data |
| `[account]-[period]-customer-report.md` | Customer call | Plain-language summary — what's working, what to fix, questions for the call |

---

## First Time?

Follow **[setup/installation.md](./setup/installation.md)** to install Node.js, VS Code, Claude Code, and Python. Takes about 10 minutes and only needs to be done once.

> **What is Claude Code?** It's a chat panel that lives inside VS Code. You type commands or plain English, and it does the work. Think of it like a chat window that can read files and run analysis.

---

## How to Use

> **Note:** `acme` is used throughout as a placeholder — replace it with the actual account name (e.g. if the account is Acme, your file is `data/input/acme.json` and you run `/analytics-run acme`).

### Step 1 — Drop in the JSON

Put the customer's analytics export in `data/input/`:

```
data/input/acme.json
```

### Step 2 — Open the project in VS Code and start Claude Code

Open VS Code and open the `imagekit-analytics-agent` folder (**File → Open Folder**).

Then open Claude Code — it's the chat panel in the left sidebar (look for the Anthropic icon). Click it and you'll see a chat input at the bottom.

Alternatively, open a terminal in VS Code (**Terminal → New Terminal**) and run:

```bash
claude
```

### Step 3 — Run the analysis

In the Claude Code chat, type:

```
/analytics-run acme
```

Or just describe it in plain language:

> "Run the analysis for Acme — JSON is `data/input/acme.json`, March 2026."

Claude will work through the data — you'll see it progressing in the chat. No need to confirm anything mid-run.

### Step 4 — Find your report

When it's done, the **customer report** appears directly in the chat — you can copy it from there.

All three files are also saved to:

```
data/output/acme/
  acme-march-2026-customer-report.md   ← bring this to the call
  acme-march-2026-analysis.md
  acme-march-2026-trace.md
```

Open them in VS Code by clicking the file in the Explorer panel on the left. The `.md` files render as readable text.

---

## Other Things You Can Do

### Quick check before a call

Don't need the full analysis? Run a fast pulse check instead:

```
/analytics-quickcheck acme
```

Returns key numbers only — traffic, formats, cache, top assets. No recommendations, just the state of the account.

### Investigate suspected bot/scraper abuse

A customer thinks bots or scrapers are driving their usage and wants to know if it's real, and what to do about it:

```
/bot-traffic-check acme
```

Checks suspect IP ranges, looks for traffic disguising itself as normal browser traffic, and recommends next steps based on their plan (robots.txt, blocking at their own edge, or ImageKit's Advanced WAF if they're on Enterprise). New skill — still being refined as it's used on more accounts.

### Compare two months

```
/analytics-compare acme
```

Needs two JSON exports for the same account. Shows what changed between periods and what drove the change.

### Edit a finished report

```
/analytics-report-edit acme
```

Adjust tone, wording, or reprioritise findings — without re-running the analysis.

### Check a URL or domain on the fly

These work without any JSON — just paste a URL or domain directly into the chat:

| Command | What it does |
|---------|-------------|
| `/url-check <url>` | Who's serving this URL, what format, is it cached? |
| `/ik-debug <url>` | Is this ImageKit URL working? Checks latency, errors, 3 test runs |
| `/transform-test <url>` | Test format conversion, resize, and compression on an IK image URL |
| `/ip-lookup <ip>` | Look up an IP address — CDN, cloud, ISP, or bot? |
| `/origin-vendor <domain>` | What infrastructure is behind this domain? |
| `/imagekit-cname-check <domain>` | Is this domain pointed to ImageKit? |
| `/custom-domain-request <domain> <clientNumber>` | Check DNS and generate the right setup message |

---

## Learn More

- **Full phase-by-phase breakdown** (all 8 phases in detail) → [`project-docs/phases.md`](./project-docs/phases.md)
- **Folder structure & what's gitignored** → [`project-docs/architecture.md`](./project-docs/architecture.md)
- **Technical rules, thresholds, UA classification** → [`.claude/rules/guardrails.md`](./.claude/rules/guardrails.md)
- **Codex / other coding assistant instructions** (work in progress) → [`AGENTS.md`](./AGENTS.md)
