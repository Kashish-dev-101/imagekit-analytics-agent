---
name: analytics-preflight
description: "PRE-STEP for any ImageKit analytics task — read before analytics-run, analytics-quickcheck, analytics-compare, or analytics-report-edit. Resolves which JSON in data/input/ to use and routes the request to the correct analytics skill. Covers file resolution, intent routing, and the full-vs-quick tie-breaker."
when_to_use: Automatically loaded before any analytics skill run. Not invoked directly — used as a routing step before analytics-run, analytics-quickcheck, analytics-compare, or analytics-report-edit.
---

# Analytics Preflight

Read this first on any analytics task. Three jobs: check the environment, resolve the input, and route to the right skill.

## 0. Environment check (before anything else)

Run these two checks silently. Only surface output if something is missing.

```bash
python3 --version
```

```bash
python3 -c "from device_detector import DeviceDetector; print('OK')"
```

If either check fails, stop and tell the user:

> **Setup required before running the agent.**
>
> **Python 3 not found** *(if `python3 --version` failed)*:
> ```bash
> brew install python3
> ```
>
> **device-detector not installed** *(if the import failed)*:
> ```bash
> pip3 install -r requirements.txt
> ```
>
> After installing, verify with:
> ```bash
> python3 -c "from device_detector import DeviceDetector; print('OK')"
> ```
> Then re-run your command.

If both checks pass, continue to Step 1 without mentioning the check.

## 1. Resolve the input (auto-pick when clear, ask when not)

- List the JSON files in `data/input/`. If the user gave a hint, filter to `data/input/*<hint>*.json` (case-insensitive — `acme` matches `analyticsAcme.json`).
- **Single-file tasks** (run / quickcheck):
  - **Unambiguous** (one match, or only one JSON present) → select it and state the choice + period read from the data: *"Running on `analyticsAcme.json`, April 1–27 — say stop if that's wrong."* Proceed unless the user objects.
  - **Ambiguous** (several match, or several present with no narrowing hint) → list them and ask which.
- **Compare** (two files): unambiguous = exactly two match, or only two JSONs present → use them, state both files + periods. Otherwise list and ask for the two.
- **report-edit**: resolve the report by hint in `data/output/` (not a JSON); same auto-pick/ask.
- Always read and state the period from the JSON's date range.

## 2. Route to the right skill

**Analytics skills (JSON-based — this preflight applies):**

| User intent | Route to |
|---|---|
| full analysis, "run the analysis", monthly review, account-review prep | `analytics-run` |
| quick / fast / pulse / overview before a call | `analytics-quickcheck` |
| compare, "vs", month-over-month, "what changed" (two periods) | `analytics-compare` |
| "what's in this export", quick sanity check | `analytics-quickcheck` |
| edit / reword / reprioritise a finished report | `analytics-report-edit` |
| customer reports suspected bot/scraper abuse, "is this traffic real", unexplained bandwidth/request spike tied to abuse suspicion | `bot-traffic-check` |

**Tie-breaker:** an unqualified "run the analysis" means the FULL run (`analytics-run`), never the trimmed `analytics-quickcheck`. If you genuinely cannot tell whether the user wants the full report or a quick pulse, ask — *"Full report or a quick pulse?"* — don't silently run the trimmed one. An explicit slash command always wins.

---

**Non-analytics skills — skip this preflight entirely:**

These skills work on a URL, domain, or IP directly. They do not need a JSON file, do not need the Python environment check, and do not go through preflight. Invoke them directly.

| Skill | What it takes |
|---|---|
| `/url-check` | A URL |
| `/ik-debug` | An ImageKit URL |
| `/transform-test` | An ImageKit image URL |
| `/ip-lookup` | One or more IP addresses |
| `/origin-vendor` | A domain name |
| `/imagekit-cname-check` | A domain name |
| `/custom-domain-request` | A domain + client number |

## 3. Hand off

Once the file(s) and target skill are settled, follow the steps in the chosen skill's `SKILL.md`.
