# Popopo — Traffic Analysis & Optimization Recommendations
## March 2026

> **Date:** 2026-03-19
> **Source data:** ImageKit usage analytics (`Analytics.json`) covering March 1–19, 2026
> **Gist:** https://gist.github.com/Kashish-dev-101/39150173e456f4f62730122b7beb13bc
> **References:**
> - [ImageKit Production Checklist — Mobile App Optimizations](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations)
> - [ImageKit — Optimize Image and Video for Web Delivery](https://imagekit.io/docs/optimize-image-and-video-for-web-delivery)
> - [Flutter — Assets and Images (supported formats)](https://docs.flutter.dev/development/ui/assets-and-images)

---

## TL;DR

Traffic is overwhelmingly from a **Flutter (Dart) mobile app** concentrated in **Japan**. A massive spike hit on **March 18** (41.9M requests in a single day vs a baseline of ~10K/day). The single largest optimization opportunity is switching user icons from PNG to WebP — the `w-512,h-512,q-15,f-png` transform alone accounts for **~192 GB of bandwidth** for 3M requests, and Flutter natively supports WebP. Two additional high-volume transforms are missing a format parameter entirely, leaving bandwidth savings on the table.

---

## 1. Volume: Traffic Spike

| Date | Requests | Bandwidth |
|---|---|---|
| Mar 1–13 (baseline avg) | ~3,800 / day | ~18 MB / day |
| Mar 14 | 1,749 | 45 MB |
| Mar 15 (from 19:00) | 5,285 | 115 MB |
| Mar 16 | 15,017 | 381 MB |
| Mar 17 | 2,530 | 49 MB |
| **Mar 18** | **41,946,522** | **~4.1 TB** |
| Mar 19 (partial) | 13,962,232 | ~1.4 TB |
| **Period total** | **55,959,015** | **~5.5 TB** |

The spike is concentrated on March 18–19, which together account for **~99.9% of all traffic in the period**. The growth from Mar 15–17 is relatively modest; the step-change happened overnight into Mar 18.

---

## 2. Client / Browser Distribution

| Client | Requests | Bandwidth | % of Requests |
|---|---|---|---|
| **Dart (Flutter)** | 41,309,762 | 4.05 TB | **73.8%** |
| popopo (custom UA) | 296,768 | 18.4 GB | 0.53% |
| Node.js | 230,739 | 14.4 GB | 0.41% |
| UnityPlayer | 98,330 | 6.4 GB | 0.18% |
| Chrome | 26,922 | 582 MB | 0.05% |
| Notification | 24,782 | 641 MB | 0.04% |
| Android | 5,471 | 352 MB | 0.01% |
| OkHttp | 2,951 | 129 MB | — |

**Dart is the Flutter HTTP client.** Flutter's networking layer identifies itself as `Dart/x.x` in User-Agent strings. At 73.8% of all requests and 73.7% of bandwidth, the app is overwhelmingly driven by Flutter mobile clients.

**Node.js** (230,739 requests from multiple GCP IPs in the `34.146.x.x` range — Tokyo region) is backend/server-side traffic, likely a media processing or notification service running on Google Cloud.

> Per the [ImageKit Production Checklist](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations): *"Mobile apps don't always send proper Accept headers or User-Agent values... You can force the output format using URL transformation parameters."*
> This is directly relevant: Dart/Flutter does not reliably send `Accept: image/webp`, so ImageKit cannot automatically negotiate WebP delivery. **Format must be explicitly set in the URL.**

---

## 3. Geographic Distribution

| Country | Requests | Bandwidth | % of Requests |
|---|---|---|---|
| **Japan** | 41,621,039 | 4.06 TB | **99.1%** |
| USA (LA) | 75,341 | 7.3 GB | 0.18% |
| Hong Kong | 47,025 | 4.5 GB | 0.11% |
| Taiwan | 41,407 | 3.99 GB | 0.10% |
| South Korea | 21,739 | 2.1 GB | 0.05% |

Japan accounts for 99.1% of CDN-resolved traffic. The top server-side IPs (`34.146.x.x`) are Google Cloud's `asia-northeast1` (Tokyo) region, consistent with a Japan-based backend.

---

## 4. Format Distribution

| Format | Requests | Bandwidth | % of Bandwidth |
|---|---|---|---|
| **PNG** | 29,884,542 | **3.86 TB** | **70.6%** |
| WebP | 11,862,061 | 223 GB | 4.1% |
| JPEG | 94,090 | 8.0 GB | 0.15% |
| text/plain | 136,878 | 99 MB | — |
| video/mp4 | 2 | 10.5 MB | — |

PNG dominates both by request count (53.4%) and bandwidth (70.6%). PNG is a lossless format — when serving photographic content (user profile icons), PNG files are significantly larger than WebP or JPEG equivalents at equivalent visual quality. WebP, despite handling 21.2% of requests, accounts for only 4.1% of bandwidth — demonstrating the compression benefit already being realized where WebP is used.

---

## 5. Top Transformations

| Transform | Requests | Bandwidth | Asset type |
|---|---|---|---|
| `w-512,q-80,f-webp` | 7,787,067 | 144.5 GB | Item thumbnails |
| `w-1080,q-15,f-webp` | 3,341,391 | 55.7 GB | Managed/look images |
| **`w-512,h-512,q-15,f-png`** | **3,000,780** | **191.9 GB** | **User icons ← see note** |
| `w-1080,q-80,f-webp` | 643,038 | 15.6 GB | Initial looks |
| `w-4089,q-80,f-webp` | 89,282 | 7.2 GB | Wide images |
| **`w-1280,h-2560,c-at_max,q-80`** | **35,383** | **3.9 GB** | **No format specified** |
| **`w-1080,h-2160,c-at_max,q-80`** | **31,096** | **4.3 GB** | **No format specified** |
| `w-512,h-1024,c-at_max,q-15` | 20,505 | 329 MB | — |
| `w-256,h-256` | 10,190 | 154 MB | No format specified |

### Critical: `w-512,h-512,q-15,f-png` — User Icons

This is the highest-bandwidth transform at **191.9 GB for 3M requests**. It is used exclusively for user profile icons (`/users/*/icon`).

- **PNG is lossless** — the `q-15` quality parameter has no effect on PNG file size (quality only applies to lossy formats like JPEG/WebP). The intent was likely to produce small files at low quality, but PNG ignores the quality setting and outputs full-size lossless files.
- The top single icon asset consumed **8.99 GB for only 4,589 views** — approximately **1.96 MB per icon load**.
- WebP at q-15 (or even q-80) would reduce icon file size by **60–80%** compared to PNG.

### Also: Missing Format on Large-Dimension Transforms

`w-1280,h-2560,c-at_max,q-80` (3.9 GB) and `w-1080,h-2160,c-at_max,q-80` (4.3 GB) have no `f-` parameter. Since the Dart client does not reliably send `Accept: image/webp`, these requests will be served in the original format (likely PNG or JPEG) rather than WebP. Combined bandwidth: **~8.2 GB** that is missing WebP conversion.

---

## 6. Status Codes

| Status | Count | Notes |
|---|---|---|
| 200 OK | 41,838,696 | 74.8% |
| 404 Not Found | 136,874 | 0.24% |
| 304 Not Modified | 15,865 | — |
| 0 (timeout) | 1,924 | — |
| ENOENT errors | 2,047 | Resource not found at upstream origin |

The 136,874 404 errors warrant a separate investigation but are a small fraction of total traffic (0.24%) and not spike-related.

---

## 7. Referrals

| Referrer | Requests | Bandwidth |
|---|---|---|
| popopo-prod.web.app | 26,956 | 584 MB |
| localhost | 201 | 8.5 MB |

The overwhelming majority of traffic (~55.9M requests) carries no Referer header, consistent with native mobile app traffic — apps do not send HTTP Referer headers.

---

## 8. Recommendations

> All recommendations are grounded in the [ImageKit Production Checklist](https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations) and [ImageKit Optimization Docs](https://imagekit.io/docs/optimize-image-and-video-for-web-delivery). Flutter's native WebP support is confirmed in [Flutter's official asset documentation](https://docs.flutter.dev/development/ui/assets-and-images).

| Priority | Issue | Recommendation |
|---|---|---|
| **High** | User icons served as PNG (`w-512,h-512,q-15,f-png`) — 191.9 GB bandwidth | Change transform to `w-512,h-512,q-80,f-webp`. PNG is lossless and ignores the `q-15` quality param; WebP at q-80 will produce far smaller files with no perceptible quality loss. Flutter natively supports WebP (JPEG, WebP, GIF, animated WebP/GIF, PNG, BMP). |
| **High** | Dart (Flutter) UA does not reliably send `Accept: image/webp` | Per ImageKit production checklist for mobile apps: force output format explicitly in the URL using `f-webp`. Do not rely on content negotiation. Review all transforms and add `f-webp` where missing. |
| **Medium** | `w-1280,h-2560,c-at_max,q-80` and `w-1080,h-2160,c-at_max,q-80` missing `f-webp` | Add `f-webp` to both: `w-1280,h-2560,c-at_max,q-80,f-webp` and `w-1080,h-2160,c-at_max,q-80,f-webp`. Combined: ~8.2 GB currently not getting WebP conversion. |
| **Medium** | `w-1080,q-15,f-webp` — quality 15 is very aggressive | Q-15 at 1080px width may result in visible compression artifacts. Per the optimization docs, the `q` parameter controls compression level. Consider testing q-60 to q-80 for this asset type to balance quality and file size. |
| **Low** | `w-4089` width — very large images | The `w-4089,q-80,f-webp` transform serves images at over 4000px width. Confirm whether clients actually need images this wide — serving a smaller width would reduce file size proportionally. |

---

## 9. Validation: PNG Ignores Quality Parameter

To confirm that `q-15` has no effect when `f-png` is specified, a test PNG (800×600, 224,566 bytes) was uploaded to ImageKit and fetched with five different transform combinations:

| Transform | File Size | Content-Type | Notes |
|---|---|---|---|
| Original (no transform) | 224,566 bytes | image/png | Source file |
| `f-png,q-15` | **224,566 bytes** | image/png | Identical to original |
| `f-png,q-80` | **224,566 bytes** | image/png | Identical to original |
| `f-webp,q-15` | **58,190 bytes** | image/webp | 74% smaller |
| `f-webp,q-80` | **68,982 bytes** | image/webp | 69% smaller |

`f-png,q-15` and `f-png,q-80` produce **byte-for-byte identical files** — PNG is a lossless format and silently ignores the `q` parameter entirely regardless of the value set. The `w-512,h-512,q-15,f-png` transform used for popopo user icons is therefore outputting full-size lossless PNG files, not compressed small files as likely intended.

Switching icons to `f-webp,q-80` would reduce per-file size by ~69%, turning ~192 GB of icon bandwidth into approximately **60 GB** — saving ~132 GB for a traffic period of this volume.

---

## 10. Summary

The spike on March 18–19 represents a ~4,000× increase over baseline in a single day, driven entirely by **Dart (Flutter) mobile clients in Japan**. The traffic appears to be real usage.

The most impactful optimization is converting **user icon delivery from PNG to WebP**. PNG is lossless — the `q-15` quality parameter currently applied to icon transforms has no effect, and PNG icon files are approximately 1.96 MB per load. Switching to `f-webp` for all icon transforms is a direct, low-risk URL change that could reduce icon-related bandwidth by 60–80%, saving ~115–155 GB for a traffic period of this size.

The second-most impactful change is ensuring all transforms explicitly specify `f-webp`, since Flutter/Dart does not send `Accept: image/webp` headers and cannot benefit from ImageKit's automatic format negotiation.
