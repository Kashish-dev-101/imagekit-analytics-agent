# Analytics Agent — JSON Schema Guide

> Which keys to read from the ImageKit analytics JSON export and what they reveal.

---

## Top-Level Keys

| Key | What to Analyse |
|-----|----------------|
| `request.total` | Overall request volume for the period |
| `request.dateWise` | Daily request trend — identify spikes, dips, growth pattern |
| `request.pattern` | Requests by URL endpoint group — infer folder/product structure |
| `bandwidth.total` | Total bandwidth for the period |
| `bandwidth.dateWise` | Daily bandwidth trend |
| `bandwidth.pattern` | Bandwidth by URL endpoint group — which product areas consume most |
| `storage_bytes.total` | Total storage used in the media library |

---

## Format & Delivery

| Key | What to Analyse |
|-----|----------------|
| `formatWise` | Full format breakdown by requests and bandwidth — is WebP/AVIF in use? PNG/MP4 heavy? |
| `statusCodeWise` | 200/206/304/404 rates — 206 indicates video streaming, 304 is browser cache hits |
| `resultType` | Hit/Miss/Error/Redirect — CDN cache efficiency (note: may be truncated on high-traffic accounts) |
| `savings` | Reported bandwidth savings from ImageKit optimisation |
| `networkDistribution` | CDN vs origin split (may be empty on some exports) |

---

## User Agents & Devices

| Key | What to Analyse |
|-----|----------------|
| `browserDistribution` | Aggregated browser/client breakdown — Chrome, Safari, OkHttp, bots etc. |
| `topUserAgent` | Raw UA strings — identify native app clients, AI agents, crawlers, SDK versions |
| `deviceDistribution` | Granular device model breakdown |
| `deviceTypeDistribution` | Smartphone / Desktop / Tablet / Unknown — calculate mobile % |

**Signals to look for in UAs:**
- `OkHttp` = Android native app
- `URLSession` / `CFNetwork` = iOS native app
- `Claude-User` / `anthropic` = AI agent fetching assets
- `ai-sdk` / `Vercel` = AI orchestration layer
- `python-requests` / `axios` / `node-fetch` = programmatic/server-side client
- `Googlebot` / `bingbot` = search crawlers

---

## Geography

| Key | What to Analyse |
|-----|----------------|
| `country.items` | Top 50 countries by requests and bandwidth |
| `country.count` | Total requests attributed to countries (may be < total due to truncation) |

**Anomalies to flag:**
- Country with low requests but disproportionately high bandwidth = large asset downloads
- Single country representing > 80% of traffic = geo-concentration risk or single-market product
- Unexpected country in top 5 = CDN routing issue or bot traffic origin

---

## Top Assets

| Key | What to Analyse |
|-----|----------------|
| `topImages.bandwidthWise` | Top 50 images by bandwidth — are they resized? What format? |
| `topImages.requestWise` | Top 50 images by request count — frequently-served assets |
| `topVideos.bandwidthWise` | Top videos by bandwidth — are they using WebM? Is there a width cap? |
| `topVideos.requestWise` | Most-served videos |
| `topOthers.bandwidthWise` | Non-image/video assets (JS, CSS, fonts, PDFs etc.) |
| `top404` | Most-requested missing files — broken references, CMS issues |

**What to check on each top asset:**
- Is a resize transformation applied? (`w-`, `h-`, `c-at_max` etc.)
- Is format optimisation applied? (`f-auto`, `f-webp`, `f-avif`)
- Is quality set? (`q-auto`, `q-80` etc.)
- What is the bandwidth per view? (bandwidth ÷ views = avg file size per request)

---

## Transformations

| Key | What to Analyse |
|-----|----------------|
| `transform.items` | Top image transformation strings by count and bandwidth |
| `videoTransform.items` | Top video transformation strings |

**Signals to look for:**
- Many unique transformation strings for the same asset = transformation sprawl, poor cache efficiency
- No resize on high-bandwidth images = full-resolution delivery to all devices
- `c-at_max` with no width = crop mode set but no size constraint
- `e_loop` = looping video (often UGC hero content)

---

## Other

| Key | What to Analyse |
|-----|----------------|
| `referral.items` | Top referral sources — where is traffic coming from? |
| `errorCodeWise` | Specific error codes — ENOENT = file not found in storage, other codes |
| `videoProcessingUnits` | Total VPU consumed and daily trend |
| `extensionUnits` | Usage of paid extensions (background removal, auto-tagging etc.) |

---

## Truncation Check

Before drawing conclusions from any dimensional breakdown, verify:

```
sum(formatWise[].count) ≈ sum(deviceTypeDistribution[].count) ≈ request.total?
```

If all breakdowns sum to the same value but it's significantly less than `request.total`, the dimensional data is truncated. Flag this in the analysis — conclusions about format mix, device split, and country distribution will only reflect a subset of traffic.

The `request.pattern` breakdown is not affected by this truncation and will always sum to 100%.
