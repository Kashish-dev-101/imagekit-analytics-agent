# Analytics Agent — Guardrails

> Technical rules Claude must follow when analysing ImageKit analytics data.
> These are learned from real analysis sessions and prevent common mistakes.

---

## 1. ImageKit Docs Are the Highest Authority

Always reference official ImageKit documentation for any technical claim. If a behaviour isn't documented or you're not certain, flag it with ⚠️. Do not infer ImageKit behaviour from general CDN knowledge.

Key docs:

- [Image Optimization](https://imagekit.io/docs/image-optimization)
- [Video Optimization](https://imagekit.io/docs/optimize-image-and-video-for-web-delivery)
- [Video Transformation + First-time Request](https://imagekit.io/docs/video-transformation#first-time-request-and-cache)
- [VPU Pricing](https://imagekit.io/docs/how-pricing-works#video-processing-units-pricing)
- [Production Checklist: Mobile](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations)
- [CDN Caching and ik-cacheTime](https://imagekit.io/docs/cdn-caching-and-purging#controlling-intermediate-cache-ttl-ik-cachetime)

---

## 2. `tr=orig` Is Video-Only

`tr=orig` in analytics data is the intermediate response ImageKit delivers for **video transformations only** when the transformation hasn't been cached yet on first request. It does NOT apply to images. Do not flag image URLs with `tr=orig` as an optimization issue — on images it means the customer is requesting the original file intentionally.

---

## 3. Format Delivery

- **WebP** — automatic when the auto format feature is enabled. ImageKit converts to WebP by default for all supporting browsers.
- **AVIF** — not enabled by default. Must be requested and enabled by ImageKit on the account (it is not a self-serve dashboard toggle). When enabled + `f-auto` is in the URL, ImageKit serves AVIF to AVIF-capable browsers and WebP to others. If an account is serving strong WebP but zero AVIF, treat this as a recommendation opportunity — not a misconfiguration.
- Always distinguish between the two in analysis. Never say "WebP/AVIF" as if they're the same setting.

**How WebP/AVIF gets delivered — three paths:**

WebP or AVIF in `formatWise` can come from any of these three mechanisms. From the analytics JSON alone you cannot tell which is active — all three produce the same result in the format breakdown:

1. **Account-level setting enabled** — ImageKit automatically performs content negotiation for all requests, no URL param needed. If the browser sends `Accept: image/webp`, WebP is served. If the setting is off, this path is inactive.
2. **`f-auto` in the URL** — same content negotiation behaviour as above, but controlled per-URL rather than account-wide. Works even if the account-level setting is off.
3. **Hardcoded format param** — `f-webp`, `f-avif` in the URL forces that specific format for all clients, bypassing content negotiation entirely.

**What this means for analysis:**

- If `formatWise` shows WebP dominant → format optimisation is working. Do not investigate which path is responsible.
- If `formatWise` shows significant JPEG/PNG despite WebP being expected → the issue is NOT a missing `f-auto`. Root cause is one of: (a) native app / bot traffic not sending `Accept` headers, or (b) a hardcoded `f-jpg` or `f-png` in the transform string actively blocking WebP.
- **The only format flag to raise from transform strings is a hardcoded override: `f-jpg` or `f-png`.** These actively block WebP/AVIF delivery regardless of account settings or `f-auto`.
- Do not flag absence of `f-auto` in a transform string as an issue — the account setting may be handling it.

---

## 4. Native Mobile Apps — Images vs Videos

**Images:** Content negotiation uses the `Accept` header. Native mobile app clients (OkHttp, URLSession, Dart) often do not send `Accept: image/webp` — they receive the original format regardless of account settings or `f-auto`. Fix: explicitly set `f-webp` in the URL for native app image requests.

**Videos:** Content negotiation uses the `User-Agent` header (`vary: User-Agent`), not the `Accept` header. Native mobile app clients often do not send a standard browser User-Agent — ImageKit cannot detect WebM support and falls back to the original format (typically MP4). Fix: explicitly force the output format in the video URL for native app clients.

Never apply the image fix (`f-webp`) to video URLs or vice versa. The detection mechanism is different for each.

> Reference: [Mobile App Optimizations](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations)

---

## 5. Video Format Delivery — How WebM Gets Served

WebM delivery for videos works via `User-Agent` header inspection (`vary: User-Agent`), not via the `Accept` header used for images. This is the key difference between image and video format optimisation in ImageKit.

**Three paths to WebM delivery (mirrors images):**

1. **Account-level setting enabled** — ImageKit checks the User-Agent on every video request and serves WebM to supporting browsers automatically
2. **`f-auto` in the video URL** — same User-Agent-based detection, controlled per-URL
3. **Hardcoded format param** — `f-webm` forces WebM for all clients regardless of User-Agent

**What this means for analysis:**

- If `formatWise` shows WebM dominant for video → format optimisation is working ✅
- If MP4 is the only video format → root cause is one of: (a) native app traffic with no standard User-Agent, or (b) a hardcoded format param blocking WebM
- **The only format flag to raise from video transform strings is a hardcoded override that blocks WebM.** Absence of `f-auto` in a video URL is not a flag — account-level setting may be handling it.
- `tr=orig` entries in video analytics are not a format issue — they are first-request intermediate responses (see Section 2)

---

## 5. VPU Consumption

- **VPU applies to video only — never to images.** Do not reference VPU in any image-related finding.
- VPU are consumed **once per unique transformation, on first request only**. Subsequent requests serve from cache.
- Each thumbnail generation = 30 VPU (equivalent to a 30-second SD video).
- Multiple thumbnail sizes per video = multiple VPU charges.
- SD = < 1280×720 px total pixels. HD = ≥ 1280×720 and < 3840×2160.

> Reference: [VPU Pricing](https://imagekit.io/docs/how-pricing-works#video-processing-units-pricing)

---

## 6. `ik-cacheTime` ≠ Signature Expiry

`ik-cacheTime` controls the TTL of ImageKit's internal intermediate cache for transformed assets. It has nothing to do with signed URL expiry or browser caching. Only available on enterprise plans.

---

## 7. Analytics Breakdown Truncation (Known Bug)

For high-traffic accounts, dimensional breakdowns (format, country, device, browser, status code) may only represent 10–15% of total traffic while the overall total is correct. The pattern breakdown (by URL group) will still sum to 100%. If you observe all dimensional breakdowns capping at the same request count, flag this explicitly rather than drawing conclusions from the incomplete breakdown data.

---

## 8. Flag Inferences Clearly

Use ⚠️ for anything inferred from data patterns rather than confirmed. Common inferences that need customer confirmation:

- Storage architecture (GCS, S3, external origin vs IK Media Library)
- Whether `tr=orig` intermediate responses are occurring in their logs
- What UI context specific thumbnail sizes serve
- Whether traffic spikes are organic growth vs bot/scraper activity

---

## 9. User Agent Classification Rules

Use these patterns to classify every entry in `topUserAgent` into one of 5 categories. Match against the raw UA string. One entry can only belong to one category — use the first match.

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

## 10. Flag Thresholds

Apply these consistently across all accounts.

| Signal | Threshold | Flag | Action |
|--------|-----------|------|--------|
| Single IP % of total requests | > 5% | ⚠️ | Flag as concentration risk — potential scraper or single app server |
| Single IP avg bandwidth per request | > 1 MB | ⚠️ | Full-resolution downloads — check what transforms are applied |
| Cache hit rate (Hit / Hit+Miss) | < 80% | ⚠️ | Check for unique transforms (Phase 6) or signed URL usage |
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
| 404 rate | > 1% of total | ⚠️ | Broken references — group top404 by pattern |

---

## 11. Bandwidth Saving Estimates

Use these conservative ranges when estimating potential savings. Always flag as ⚠️ estimate.

| Optimisation | Saving vs current | Notes |
|---|---|---|
| Enable AVIF (from WebP) | 20–30% of WebP bandwidth | Requires account settings change |
| Enable WebM for video (from MP4) | 20–30% of MP4 bandwidth | Add `f-auto` to video URL |
| Add resize to full-resolution image | 40–60% of current bandwidth | Depends on original vs display size ratio |
| Add `f-webp` to native app requests | 20–35% of those requests | Depends on current format being served |
| GIF → WebP | 30–50% of GIF bandwidth | Automatic with `f-auto` |
