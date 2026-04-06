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

- **WebP** — automatic, no account configuration needed. ImageKit converts to WebP by default for all supporting browsers.
- **AVIF** — must be explicitly enabled in ImageKit account settings. Not on by default. When enabled + `f-auto` is in the URL, ImageKit serves AVIF to AVIF-capable browsers and WebP to others.
- Always distinguish between the two in analysis. Never say "WebP/AVIF" as if they're the same setting.

---

## 4. `f-auto` on Native Mobile Apps

`f-auto` and automatic WebP delivery via content negotiation works for browsers (which send `Accept: image/webp`). Native mobile app HTTP clients (OkHttp, URLSession) often do **not** send the correct Accept headers — they will receive the original format regardless of `f-auto`. For native apps, explicitly set `f-webp` in the URL.

> Reference: [Mobile App Optimizations](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations)

---

## 5. VPU Consumption

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
