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
