# Morphic — ImageKit Analytics Analysis (March 2026)

> **Date:** 2026-03-20
> **Source:** AnalyticsMarch.json (March 1–20, 2026)
> **Note:** Some findings marked ⚠️ are inferred from data patterns — confirm with customer on call.

---

## Who is Morphic?

**Industry: Generative AI / Agentic SaaS Platform**

Morphic appears to be an AI-powered content generation platform where users generate images and videos through AI-driven chat sessions. Key evidence from the data:

- Assets named `output.png` / `output.mp4` — programmatically generated, not user-uploaded filenames
- Path structure: `{workspace_id}/{project_id}/{session_id}/output.png` — workspace → project → session hierarchy
- `Claude-User` is the #2 traffic source — Claude AI is actively fetching assets from ImageKit as part of the agent loop
- `ai-sdk/6.0.116 runtime/node.js/24` (Vercel AI SDK) confirms AI orchestration layer
- `temp-production` folder = staging during generation; `assets-production` = final committed outputs

⚠️ **Architecture assumption:** Assets appear to be stored in a GCS bucket (`external-cdn.morphic.com` is inferred to be a custom domain pointing to ImageKit with GCS as origin). Confirm with customer.

---

## Traffic Summary

| Metric | Value |
|---|---|
| Total requests (Mar 1–20) | ~23M |
| Total bandwidth | **7.45 TB** |
| Daily average | ~1.1M requests, trending up to 2M by Mar 19 |
| Peak day | Mar 19 — 2.05M requests |

### By Folder/Pattern

| Pattern | Requests | Bandwidth | Purpose |
|---|---|---|---|
| `assets-production` | 13.3M | 4.72 TB | Core product — AI-generated outputs |
| `chat-production` | 3.5M | 1.18 TB | Images shared/generated in chat sessions |
| `website-production` | 1.3M | 808 GB | Marketing site |
| `temp-production` | 660K | 41.6 GB | Staging during AI generation |
| `Default` | 2.6M | 568 GB | Untagged/fallback |

---

## Client / User Agent Breakdown

| Client | Requests | Bandwidth | Notes |
|---|---|---|---|
| Chrome (Windows/Mac) | ~3.3M | ~2.6 TB | Primary web users |
| **Claude-User** | **3.9M** | **39 GB** | Claude AI fetching images for analysis |
| ai-sdk (Node.js) | 1.9M | 79 GB | Vercel AI SDK — backend AI orchestration |
| Facebook crawler | 1.46M | 248 GB | Social sharing/link previews |
| node | 971K | 180 GB | Backend server-side requests |
| python-httpx | 715K | 0.5 GB | Backend, tiny payloads |
| Mobile (Android Chrome) | ~956K | ~475 GB | Mobile web users |
| iPhone Safari | ~570K | ~183 GB | iOS users |
| OpenAI File Downloader | 193K | 9.6 GB | ⚠️ OpenAI also fetching assets — multi-LLM? |

**Mobile total: ~1.79M requests (11.8%), ~657 GB (12.7%)**

**Key insight on Claude-User:** 3.9M requests at only ~10KB average = Claude is fetching **small/resized images** from ImageKit URLs to include in its vision context, not full-resolution originals. ImageKit sits inside the agent reasoning loop.

---

## Geography

| Country | Requests | Bandwidth |
|---|---|---|
| USA | 12.8M (61%) | 2.06 TB |
| India | 3.06M (15%) | **2.21 TB** |
| UK | 940K (4.5%) | 104 GB |
| South Korea | 563K | 308 GB |
| Netherlands | 449K | 214 GB |
| Global (50+ countries) | — | — |

⚠️ **India anomaly:** India has 15% of requests but more bandwidth than USA (2.21 TB vs 2.06 TB) — Indian users are consuming heavier content (likely videos or larger images). Worth investigating with customer.

---

## Format Distribution

| Format | Requests | Bandwidth | Notes |
|---|---|---|---|
| **image/png** | 2.6M | **2.94 TB** | AI-generated outputs, no format optimization |
| **video/mp4** | 1.2M | **2.67 TB** | AI-generated and marketing videos |
| **video/webm** | 2.3M | 712 GB | Some WebM already being served |
| image/jpeg | 1.3M | 302 GB | — |
| **image/webp** | 11.2M | 204 GB | Optimized thumbnails — already good practice |
| audio/mpeg | 87K | 14.6 GB | Audio assets |
| image/avif | 1.3M | 13.5 GB | — |

---

## Top Assets

### By Bandwidth
- `output.png` files served at high resolution — AI-generated images, no format conversion applied
- `output.mp4/ik-thumbnail.jpg?tr=f-auto,h-1024,c-at_max` — **10.98 GB for 4,626 views = ~2.4MB per thumbnail**
- `output.mp4/ik-thumbnail.jpg?tr=f-auto,h-1920,c-at_max` — **8.83 GB for 1,456 views = ~6MB per thumbnail**

### By Request Count
All top assets by request count are video thumbnails:
- `output.mp4/ik-thumbnail.jpg?tr=h-100,f-webp,q-60` → 55K, 53K, 51K views each

These thumbnail URLs use `f-webp,q-60` — **this is already well optimized**.

---

## Status Codes

| Code | Count | Notes |
|---|---|---|
| 200 OK | 16.8M | |
| **206 Partial Content** | **3.3M** | Video streaming (range requests) |
| 404 Not Found | 793K | ~3.4% error rate — worth investigating |
| 304 Not Modified | 123K | Cache hits |
| 400 Bad Request | 21.8K | — |

---

## Optimization Opportunities

### 1. PNG Images — No Format Conversion Applied
**Confirmed from data.** AI-generated `output.png` files are being delivered without `f-webp`. Switching to WebP at delivery (no re-storage needed) could reduce the 2.94 TB PNG bandwidth by 25–35%.

> **ImageKit parameter:** Add `f-webp` to image delivery URLs. For lossless (if pixel-perfect is needed): `f-webp,q-100`.
> **Reference:** [ImageKit — Image Optimization](https://imagekit.io/docs/image-optimization)

---

### 2. Video Format — MP4 to WebM for Chrome
**Confirmed from data.** Chrome is ~32% of traffic and supports WebM natively. MP4 is 2.67 TB; WebM is typically 20–30% smaller. They already serve some WebM (712 GB) so the infrastructure supports it.

> **ImageKit parameter:** Add `f-auto` to video URLs — ImageKit auto-serves WebM to Chrome, MP4 to Safari.
> **Reference:** [ImageKit — Video Optimization](https://imagekit.io/docs/optimize-image-and-video-for-web-delivery)

---

### 3. Video `tr=orig` Intermediate Response — Pre-Processing
**Confirmed from data + docs.** When a video transformation is requested for the first time and not yet cached, ImageKit delivers the original video (`tr=orig`) as an intermediate fallback while processing in the background. This means users see the unoptimized original video on first load.

> **Fix:** Pre-process video transformations server-side immediately after writing to GCS, before the asset is exposed to users. Use webhook events to know when processing is complete.
>
> **Flow:**
> ```
> Video written to GCS
>        ↓
> Backend makes server-side GET to the ImageKit transformation URL
>        ↓
> ImageKit processes and caches the transformation
>        ↓
> video.transformation.ready webhook fires
>        ↓
> Mark asset as available in DB — users always hit cached version
> ```
>
> **Reference:**
> - [ImageKit — Video Transformation (First-time request)](https://imagekit.io/docs/video-transformation#first-time-request-and-cache)
> - [ImageKit — Video Webhook Events](https://imagekit.io/docs/video-webhook-events)

⚠️ **Needs confirmation:** Verify with customer whether they're seeing the `tr=orig` intermediate response in their logs and which specific video transformations are triggering it.

---

### 4. Thumbnail VPU — Multiple Sizes Per Video
**Confirmed from data + pricing docs.** The same `output.mp4` is being thumbnailed at 4 different sizes:
- `h-100,f-webp,q-60` (well optimized)
- `h-256,c-at_max`
- `h-1024,c-at_max` — 2.4MB per view
- `h-1920,c-at_max` — 6MB per view

**Live example URLs (same video, different transformations):**
```
# h-256
https://external-cdn.morphic.com/assets-production/0193449d-bd5f-7034-a819-90186076c7d4/019a54b5-6e71-731f-bb84-215919041e14/019b559a-c85b-713f-a760-e8432bffe347/output.mp4/ik-thumbnail.jpg?tr=f-auto,h-256,c-at_max

# h-1024
https://external-cdn.morphic.com/assets-production/0193449d-bd5f-7034-a819-90186076c7d4/019a54b5-6e71-731f-bb84-215919041e14/019b559a-c85b-713f-a760-e8432bffe347/output.mp4/ik-thumbnail.jpg?tr=f-auto,h-1024,c-at_max

# h-1920
https://external-cdn.morphic.com/assets-production/0193449d-bd5f-7034-a819-90186076c7d4/019a54b5-6e71-731f-bb84-215919041e14/019b559a-c85b-713f-a760-e8432bffe347/output.mp4/ik-thumbnail.jpg?tr=f-auto,h-1920,c-at_max
```

Per [ImageKit VPU pricing](https://imagekit.io/docs/how-pricing-works#video-processing-units-pricing): **each thumbnail generation = 30 VPU** (first time only; subsequent requests serve from cache).

4 sizes × 30 VPU = **120 VPU per unique video** on first requests.

> **Suggestions:**
> 1. Confirm if `h-1024` and `h-1920` are necessary — these are near full-resolution thumbnails with very low view counts
> 2. Consolidate to 2 standard sizes and resize client-side for smaller variants
> 3. Pre-generate thumbnails server-side at upload time using the same webhook flow above

⚠️ **Needs confirmation:** Ask customer what UI context uses `h-1024` and `h-1920` thumbnails — may be a lightbox or preview panel that could use the actual image/video instead.

---

### 5. Mobile — No Responsive Sizing
**Confirmed from data.** Mobile is 11.8% of requests (1.79M) and 12.7% of bandwidth (657 GB). No responsive sizing is applied — mobile users get the same resolution as desktop.

> **ImageKit parameter:** Add `w-800` (or appropriate width) for mobile user agents. Can also use `dpr-2` for retina displays.
> **Reference:** [ImageKit — Production Checklist: Mobile](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations)

---

## How ImageKit Adds Value to Morphic

1. **CDN delivery from GCS** — GCS alone has no global CDN. ImageKit sits in front and caches/routes globally across 50+ countries.
2. **On-the-fly video thumbnail extraction** — `output.mp4/ik-thumbnail.jpg` is core product functionality. Without ImageKit, they'd need a separate thumbnail generation service.
3. **Signed URL security** — AI-generated content is private per user/workspace. ImageKit enforces access control at the CDN layer.
4. **Inside the agent loop** — Claude fetches from ImageKit URLs (not GCS directly) for vision analysis. ImageKit is not just delivery — it's part of the AI pipeline.
5. **Format optimization at delivery** — no re-processing of GCS assets needed; transformations happen at the edge.

---

## Open Questions for Customer Call

1. Is storage on GCS with ImageKit as delivery layer — or is there a different origin setup?
2. What UI context uses `h-1024` and `h-1920` thumbnails?
3. Are they seeing the `tr=orig` intermediate response in their own logs?
4. What is the `OpenAI File Downloader` UA (193K requests) — are they running a multi-LLM pipeline?
5. What is causing the 793K 404 errors (~3.4%)?
6. India bandwidth exceeding USA despite fewer requests — is that expected?
