# Analytics Agent — JSON Schema Guide

> Field reference for ImageKit analytics JSON exports.
> Three sections: (1) field-by-field reference, (2) UA classification rules, (3) thresholds and flag values.

---

## Section 1 — Field Reference

| JSON Key | Phase | What It Contains | What to Look For |
|---|---|---|---|
| `request.total` | 0, 1 | Total requests for the period | Baseline for all % calculations |
| `bandwidth.total` | 1 | Total bandwidth in bytes | Convert to GB/TB for reporting |
| `storage_bytes.total` | 1 | Storage used in the media library | Context for account size |
| `request.dateWise.labels` | 1 | Array of date strings | Date axis for trend |
| `request.dateWise.datasets[0].data` | 1 | Array of daily request counts | Spikes, dips, growth pattern |
| `bandwidth.dateWise` | 1 | Same structure, daily bandwidth | Bandwidth trend (may differ from request trend if large asset days) |
| `request.pattern` | 1 | Array of `{name, count}` — URL endpoint groups | Traffic distribution by product area / folder |
| `bandwidth.pattern` | 1 | Same structure, bandwidth per group | Which areas consume most bandwidth |
| `formatWise` | 0, 2 | Array of `{name, count, bandwidth}` — format breakdown | WebP %, AVIF presence, GIF presence |
| `topImages.bandwidthWise` | 5 | Top 50 images by bandwidth | `{url, count, bandwidth}` — per-view size = bandwidth ÷ count |
| `topImages.requestWise` | 5 | Top 50 images by request count | High-frequency assets |
| `topVideos.bandwidthWise` | 5 | Top videos by bandwidth | Same fields — check transform for `f-auto`, `w-` |
| `topVideos.requestWise` | 5 | Top videos by request count | |
| `topOthers.bandwidthWise` | 5 | Non-image/video assets (JS, CSS, audio, PDF) | Look for unexpectedly large non-media assets |
| `top404` | 5 | Top missing file paths | Group by pattern to identify root cause |
| `browserDistribution` | 3 | Aggregated browser/client breakdown | Chrome, Safari, OkHttp, bots — aggregated categories |
| `topUserAgent` | 3 | Raw UA strings with count and bandwidth | Most detailed source for classification — use this as primary |
| `deviceDistribution` | 3 | Granular device model breakdown | Model-level detail |
| `deviceTypeDistribution` | 0, 3 | Smartphone / Desktop / Tablet / Unknown | Use for mobile % and truncation check |
| `topIps` | 4 | Array of `{name, count, bandwidth}` — top IPs | IP = client IP; high count = scraper or single server |
| `referral.items` | 1 | Top referral domains with count and bandwidth | Where traffic originates; compare avg asset size per referrer |
| `country.items` | — | Top 50 countries by requests and bandwidth | Single-market concentration, bandwidth-heavy countries |
| `country.count` | — | Total requests attributed to countries | May be < total if data is truncated |
| `transform.items` | 6 | Top image transformation strings | Count, bandwidth per transform string |
| `videoTransform.items` | 6 | Top video transformation strings | Same structure |
| `resultType` | 7 | Array of `{name, count}` — Hit / Miss / Error / RefreshHit | Cache hit rate = Hit / (Hit + Miss) |
| `statusCodeWise` | 7 | Array of `{name, count}` — 200, 206, 304, 404, 400 | Status code mix |
| `errorCodeWise` | 7 | Array of `{name, count}` — ENOENT, UNIDENTIFIED, etc. | Error pattern classification |
| `networkDistribution` | — | CDN vs origin split | May be empty on some exports |
| `savings` | — | Reported bandwidth savings | May be empty — not always configured |
| `videoProcessingUnits` | 8 | Total VPU consumed + `dateWise` daily trend | Track first-time processing costs |
| `extensionUnits` | 8 | Usage of paid extensions | Background removal, auto-tagging, AI description |

---

## Section 2 — User Agent Classification Rules

Use these patterns to classify every entry in `topUserAgent` into one of 5 categories.
Match against the raw UA string. One entry can only belong to one category — use the first match.

### Web Browser
Standard browser clients that send correct `Accept` headers for content negotiation.
- `Mozilla/5.0` + `Chrome/` → Chrome (desktop or mobile)
- `Mozilla/5.0` + `Safari/` (no Chrome) → Safari
- `Mozilla/5.0` + `Firefox/` → Firefox
- `Mozilla/5.0` + `Edg/` → Edge
- `Mozilla/5.0` + `SamsungBrowser/` → Samsung Browser

### Native Mobile App
Clients that do NOT send `Accept: image/webp` — `f-auto` will not trigger WebP/AVIF delivery for these.
- `Dart/` → Flutter (Dart HTTP client)
- `okhttp/` → Android native (OkHttp)
- `CFNetwork/` or `Darwin/` → iOS native (URLSession)
- `com.apple.WebKit` with no browser UA → iOS WKWebView

### In-App Browser
Embedded browsers inside social apps — may have inconsistent Accept header behaviour.
- `FBAN/` or `FBAV/` or `FB_IAB` → Facebook in-app
- `Instagram` → Instagram in-app
- `Twitter` or `X/` → Twitter/X in-app
- `MicroMessenger` → WeChat in-app

### Bot / AI Agent
Non-human clients — important for usage cost analysis and format recommendation scoping.
- `Claude-User` or `anthropic-ai` → Anthropic AI agent fetching assets
- `GPTBot` or `ChatGPT-User` or `OAI-SearchBot` → OpenAI crawler
- `OpenAI-File-Downloader` → OpenAI file processing
- `ai-sdk/` → Vercel AI SDK (orchestration layer)
- `Googlebot` or `Bingbot` or `Slurp` → Search crawlers
- `python-httpx` or `python-requests` → Python HTTP clients (usually backend/automation)
- `Go-http-client` → Go HTTP client (usually backend)
- `axios/` → JavaScript HTTP client (usually backend)
- `node-fetch` or `node/` (no browser UA) → Node.js server-side
- `curl/` → Direct curl calls

### Server-side / Programmatic
Backend application servers — include in request count but separate from user-facing traffic for recommendations.
- `node` (bare) → Node.js server
- Any of the above Bot patterns used by the customer's own backend (check referrer for confirmation)

---

## Section 3 — Thresholds and Flag Values

These are the specific numbers that trigger a flag. Apply consistently across all accounts.

| Signal | Threshold | Flag level | Action |
|---|---|---|---|
| Single IP % of total requests | > 5% | ⚠️ | Flag as concentration risk — potential scraper or single app server |
| Single IP avg bandwidth per request | > 1 MB | ⚠️ | Full-resolution downloads — check what transforms (if any) are applied |
| Cache hit rate (Hit / Hit+Miss) | < 80% | ⚠️ | Check for unique transforms (Phase 6) or signed URL usage. ImageKit docs define ≥ 80% as optimal. |
| Unique transformation strings | > 30 | ⚠️ | Transformation sprawl — poor CDN cache efficiency |
| Near-duplicate transforms | width diff < 10px | ⚠️ | Consolidation opportunity |
| Bot / AI Agent traffic | > 15% of requests | ⚠️ | Non-human traffic is significant — note for usage cost discussion |
| In-App Browser traffic | > 10% of requests | ⚠️ | Check format delivery behaviour for these clients |
| Native Mobile App detected | any | flag | `f-auto` won't work — explicit `f-webp` needed |
| AVIF requests | = 0 | ⚠️ | AVIF not enabled in account settings |
| GIF requests | > 0 | ⚠️ | Can be replaced with WebP or MP4 automatically |
| Image bandwidth per view | > 2 MB | 🔴 | Oversized asset — check for missing resize |
| Video bandwidth per view | > 10 MB | 🔴 | Unoptimised video — check for missing width cap and f-auto |
| Daily request spike | > 2× daily average | ⚠️ | Note date — ask customer if expected (campaign, launch, bot event) |
| 304 browser cache rate | < 1% | ⚠️ | Cache-Control headers may not be set correctly |
| 404 rate | > 1% of total | ⚠️ | Broken references — group top404 by pattern |
| Mobile % (browser + in-app + native) | > 30% | note in talking points | Provide mobile breakdown in Output 2 |
| Web Browser % | > 60% | trigger | Recommend post-sales perf agent as next step |

---

## Bandwidth Saving Estimates (for flagged opportunities)

Use these conservative ranges when estimating potential savings. Always flag as ⚠️ estimate.

| Optimization | Saving vs current | Notes |
|---|---|---|
| Enable AVIF (from WebP) | 20–30% of WebP bandwidth | Requires account settings change |
| Enable WebM for video (from MP4) | 20–30% of MP4 bandwidth | Add `f-auto` to video URL |
| Add resize to full-resolution image | 40–60% of current bandwidth | Depends on original vs display size ratio |
| Add `f-webp` to native app requests | 20–35% of those requests | Depends on current format being served |
| GIF → WebP | 30–50% of GIF bandwidth | Automatic with `f-auto` |
