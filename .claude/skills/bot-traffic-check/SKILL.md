---
name: bot-traffic-check
description: "Investigate suspected bot/scraper abuse from an ImageKit analytics export — quantifies named/suspect IP ranges, detects disguised-bot UA patterns, cross-checks geography and referrer, classifies sources via /ip-lookup, and applies the plan-tier-aware recommendation policy (robots.txt / customer-edge WAF / ImageKit Enterprise WAF / cloud-provider abuse report). v1 — built from a real tech-support case (asiasur, 2026-08), not yet battle-tested on others."
when_to_use: A customer reports suspected bot/scraper traffic or unexplained bandwidth/request spikes and asks whether it's abuse and what they can do about it. Use instead of /analytics-quickcheck or /analytics-run when the ask is specifically "is this bot traffic and what do I do" — a targeted tech-support investigation, not a routine account review.
---

# /bot-traffic-check — Suspected bot/scraper abuse investigation

This is a targeted, tech-support-shaped investigation — not a full account review. It answers one question: **is the traffic the customer is worried about actually abnormal, and if so, what can they realistically do about it given their plan?** It does NOT produce the 3-file `/analytics-run` output, and does not draft the customer-facing reply itself — hand off to `/customer-reply` for that.

Complements, does not replace: `agent/prompt.md` Phase 6 (Top IPs) and `.claude/rules/guardrails.md` §11 already cover single-IP concentration thresholds during a full review. This skill reuses those thresholds but adds range-level aggregation, the disguised-UA heuristic, geography/referrer cross-checks, and the recommendation policy — none of which Phase 6 does on its own.

## 1. Resolve the input

Same auto-pick/ask pattern as `analytics-preflight` — resolve the JSON from `data/input/` (including subfolders like `techsupport/`) by hint. State the file + period read from the data before proceeding.

No need to run `agent/extract.py` — this skill reads specific breakdowns directly from the raw JSON (`topIps`, `topUserAgent`, `referral`, `country`, `resultType`), not the full flattened text.

## 2. Capture what the customer already claims

If the customer named specific IPs, ranges, or user-agent strings, note them — they're the starting point for Step 3, not the whole investigation. Don't just verify their claim and stop; the asiasur case turned up an unnamed Azure VM fleet of comparable size that the customer hadn't flagged.

## 3. Quantify named/suspect ranges

Pull `topIps.requestWise` and `topIps.bandwidthWise` (top 50 each). For every customer-named IP/CIDR range, sum matching entries across both lists (dedupe by IP) and report:
- Total requests and bandwidth attributable, as % of `request.total` / `bandwidth.total`
- **State this is a floor, not a ceiling** — only the top 50 by each metric are visible; there may be more IPs in a named range below that cutoff.
- Apply guardrails §11 single-IP thresholds (>5% requests, >10% bandwidth, >1MB avg/request) to any individual IP, named or not.

## 4. Disguised-bot UA heuristic

Pull `topUserAgent.requestWise` (top 50). Two passes:

1. **Explicit bot match** — apply the guardrails §10 bot-marker list (Googlebot, Bingbot, Baiduspider, Amazonbot, AhrefsBot, HeadlessChrome, `compatible; crawler`, etc.) and sum their share of requests/bandwidth. This is the "traffic that honestly identifies itself" baseline.
2. **Disguise pattern** — look for the *same* browser+OS combination repeated across several distinct version numbers, each individually carrying high volume (thousands of requests), especially on a platform combination that's an unusual fit for the account's real audience (e.g. `X11; Linux x86_64` desktop Chrome for a consumer site with no expected Linux-desktop userbase). Sum this group's share separately.

**The gap between the two passes is the finding** — if disguise-pattern volume is much larger than explicit-bot volume, most of the abuse is riding on spoofed browser UAs and a UA-based block (robots.txt, UA-keyed WAF rules) will only catch the small honest fraction. State this explicitly; it directly shapes the recommendation in Step 6.

## 5. Geography and referrer cross-checks

- **Country**: pull `country.requestWise.items`, sort by count. Compare top countries against the account's real/expected market (ask the customer if not obvious from the domain/account name). A mismatch — real home-market traffic sitting far below unexpected countries — is often the single sharpest signal, sharper than any per-IP threshold.
- **Referrer**: pull `referral.requestWise.items`. If the account's own domain dominates (i.e. this traffic is rendering real pages, not hotlinking), the fix belongs at the customer's own edge — ImageKit can't distinguish this traffic from real visitors since it arrives with a legitimate-looking referrer. If a foreign/absent referrer dominates instead, that's a different conversation (hotlinking protection), not covered by this skill's recommendation policy below.

## 6. Classify flagged IPs

Run `/ip-lookup` (this project's skill) on: the customer's named IPs, plus any generic/unlabeled IPs repeating across the top-15 by count or bandwidth that aren't otherwise explained. Do not classify from general knowledge — the ip-lookup skill's ipinfo.io check is mandatory, same rule as prompt.md Phase 6.

## 7. Apply the recommendation policy

This is the part that took real back-and-forth to settle — apply it as-is, don't improvise a different structure:

| Source type | Recommendation | Notes |
|---|---|---|
| Identifiable legitimate business (e.g. a named media-monitoring/SEO crawler, confirmed via reverse DNS/org in Step 6) | `robots.txt` restriction | Not an "abuse" case — they're not violating anything. State plainly if Step 4 showed most of their traffic is disguised: robots.txt only catches the honest fraction. |
| Disguised/scraper traffic riding the account's **own referrer** (Step 5 confirms this) | Customer-side WAF/bot-manager at their own edge, filtering by **IP/ASN, not User-Agent** | ImageKit can't block this at the ImageKit layer unless the account is Enterprise (next row) — the traffic looks identical to a real visitor from ImageKit's vantage point. |
| Same, but account is **confirmed Enterprise** | Also mention ImageKit Advanced WAF (IP/UA/geo blocking at the ImageKit layer) as an option | **Do not assume plan tier — ask if not already stated in the ticket.** Do not mention Advanced WAF at all for non-Enterprise accounts; it just invites a "how do I enable that" follow-up with a dead end. |
| Traffic from AWS/GCP/Azure specifically | Cloud-provider abuse report | **Gate on two conditions together: account is Enterprise, AND that specific provider's share is genuinely dominant** (not just present at a few thousand requests). A handful of moderate-volume VMs on a non-Enterprise account isn't worth the customer's time filing an abuse report that likely won't get fast action. |
| Traffic from a smaller/generic hosting provider (not AWS/GCP/Azure) | Folds into the customer-edge WAF/bot-manager recommendation | Do not recommend an abuse report here — that path is reserved for the three major clouds per standing practice. |

Do not propose ImageKit WAF or a cloud abuse report as a first move regardless of plan tier — check plan tier and dominance first, every time.

## 8. Output

Factual finding + recommendation, addressed to the internal reader (you), not customer-facing. Structure:

```
## Bot Traffic Check — [Account] — [Period]

### Scale
[Named ranges' share of requests/bandwidth, with floor caveat]
[Any additional unnamed source of comparable size found]

### Disguise gap
[Explicit bot-UA % vs disguise-pattern %, and what that implies for UA-based blocking]

### Geography / referrer
[Home-market % vs actual top countries]
[Referrer dominance — customer's own domain or hotlinking]

### IP classification
[Table from /ip-lookup]

### Recommendation
[Applying the Step 7 policy to what was actually found — plan tier stated explicitly, not assumed]
```

Hand off to `/customer-reply` for the actual customer-facing message — this skill's job ends at the internal finding + recommendation.
