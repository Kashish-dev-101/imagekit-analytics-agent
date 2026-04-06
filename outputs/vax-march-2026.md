# Vax ImageKit Analytics — March 2026 Full Technical Analysis

**Account:** Vax (ik.vax.co.uk)  
**Period:** 2026-03-01 to 2026-03-31  
**Prepared:** 2026-04-01

---

## 1. Traffic Overview

| Metric | Value |
|--------|-------|
| Total Requests | 41,050,503 |
| Total Bandwidth | **2.88 TB** |
| Storage Used | 4.68 GB |
| Requests with Transformations | 24,482,954 (59.6%) |
| Peak Day | Mar 28 — 1,661,162 requests |
| Lowest Day | Mar 31 — 989,577 requests |

### Traffic by URL Pattern
| Pattern | Requests | % of Total |
|---------|----------|------------|
| Default (production) | 41,009,975 | 99.9% |
| staging2 | 39,750 | 0.1% |
| vaxeu | 689 | <0.01% |
| vax2 | 89 | <0.01% |

---

## 2. Format Delivery Analysis ✅ / ⚠️

### Image Formats
| Format | Requests | % of Image Requests | Bandwidth |
|--------|----------|---------------------|-----------|
| image/webp | 30,844,373 | **93.5%** ✅ | 1.90 TB |
| image/jpeg | 714,811 | 2.2% | 168.5 GB |
| image/svg+xml | 967,626 | 2.9% | 2.2 GB |
| image/png | 439,693 | 1.3% | 17.6 GB |
| image/gif | 39,782 | 0.12% | 22.9 GB |
| **image/avif** | **0** | **0%** ⚠️ | 0 |

**Finding:** WebP delivery is excellent at 93.5% — ImageKit's automatic format conversion is working correctly. However, **AVIF is not enabled at all**. AVIF delivers ~20-30% better compression than WebP. Given the account's 2.88 TB monthly bandwidth, enabling AVIF could save an estimated 576 GB – 864 GB per month.

### Video Formats
| Format | Requests | % of Video | Bandwidth |
|--------|----------|------------|-----------|
| video/webm | 72,489 | **54.9%** ✅ | 96.0 GB |
| video/mp4 | 59,513 | 45.1% | 63.8 GB |

**Finding:** WebM is the majority video format — good. However, the top 5 highest-bandwidth videos are all served exclusively as MP4 with no WebM delivery. These UGC hero videos alone consumed 160GB+ in March.

---

## 3. User Agent & Device Analysis ⚠️

### Browser Distribution
| Browser / Agent | Requests | % of Total | Bandwidth |
|----------------|----------|------------|-----------|
| Chrome (desktop) | 10,058,354 | 33.4% | 663.7 GB |
| **Mobile (browser)** | **7,396,648** | **24.6%** | 515.5 GB |
| **Facebook (in-app)** | **4,086,130** | **13.6%** | 258.9 GB |
| **Instagram (in-app)** | **2,119,701** | **7.0%** | 129.3 GB |
| **Samsung Browser** | **2,016,013** | **6.7%** | 116.1 GB |
| Safari | 1,370,743 | 4.6% | 138.6 GB |
| Microsoft Edge | 1,190,688 | 4.0% | 82.5 GB |
| Google (bot/crawler) | 935,132 | 3.1% | 80.0 GB |
| Firefox | 272,892 | 0.9% | 17.8 GB |
| Headless | 170,191 | 0.6% | 18.4 GB |

### Mobile Traffic Summary
| Category | Requests | % |
|----------|----------|---|
| Mobile browser + Samsung | 9,412,661 | 31.3% |
| Social in-app (Facebook + Instagram) | 6,205,831 | 20.6% |
| **Total mobile-origin traffic** | **15,618,492** | **51.9%** ⚠️ |

**Finding:** Over **51.9% of traffic comes from mobile devices**. Facebook and Instagram in-app browsers represent **20.6%** of all requests. These in-app browsers are native mobile app environments that may not send standard `Accept` headers for AVIF, and do not benefit from browser-level format negotiation. Recommendation: ensure `f-auto` is applied on all image URLs to allow ImageKit to select the best format per UA, and consider `f-webp` as a forced fallback for social in-app contexts.

---

## 4. Resize / Transformation Analysis ✅ / ⚠️

**50 unique transformation variants** recorded in March. Full list below.

### Top Transformations by Request Volume
| Transformation | Requests | Type | Notes |
|----------------|----------|------|-------|
| `cm-pad_resize:w-392:h-392` | 7,681,420 | Product card resize ✅ | Mobile product thumbnails |
| `c-at_max:w-864` | 4,841,718 | Width cap ✅ | Navigation images — tablet/mobile |
| `c-at_max:w-342` | 1,685,456 | Width cap ✅ | Smaller mobile breakpoint |
| `c-at_max:w-1280` | 1,515,903 | Width cap ✅ | Desktop |
| `c-at_max:w-960` | 1,452,014 | Width cap ✅ | Tablet |
| `c-at_max:w-377` | 1,219,338 | Width cap ✅ | Mobile breakpoint |
| `c-at_max:w-2160` | 733,827 | Width cap — large ⚠️ | 2160px — retina/large desktop only |
| `c-at_max:w-592` | 709,961 | Width cap ✅ | |
| `c-at_max:w-160` | 570,491 | Thumbnail ✅ | |
| `w-912` | 540,013 | Width only ✅ | |

**Finding:** Resize behaviour is generally good. `c-at_max` (cap at max) is the dominant pattern — correct approach as it avoids upscaling. However:
- `c-at_max:w-2160` has 733,827 requests — serving 2160px images to that many users suggests some breakpoints are too large for actual device viewports
- **50 unique transformation strings** create 50+ distinct CDN cache keys for the same underlying assets. Consolidating to ~10–15 breakpoints would dramatically improve cache hit rates

### Transformation Fragmentation Flag ⚠️
The `c-at_max:w-*` parameter alone is used with **14 different width values**: 40, 160, 296, 297, 342, 377, 432, 472, 592, 594, 640, 720, 864, 960, 1280, 1440, 2160. Multiple near-duplicate breakpoints exist (e.g. 592 vs 594, 296 vs 297, 342 vs 377) that could be consolidated.

---

## 5. Top Images — Resolution & Resize Flags ⚠️

### High-Bandwidth Images Without Width Restriction (FLAG)

| Image | Bandwidth | Views | Issue |
|-------|-----------|-------|-------|
| `VAX_LiftOut_Multi_Pet-Design_Hero_3Qtr_SKU6.jpg` | **59.1 GB** | 13,711 | Served with `q_auto/f_jpg` only — no width cap. Full resolution delivered |
| `vaxuk4301-soc-con-kitchen-ugc-comp-03.jpg` | **22.5 GB** | 188,430 | `c_auto,g_center,h_1000,w_2000` — 2000px wide, no responsive capping |
| `SW-2000x1000-Top-Image.png` | **15.1 GB** | 182,770 | No transformation. Likely 2000px source delivered as-is |
| `Multi_Pet_Multi_Corded_Vacuum_Surface_resized.jpg` | **17.5 GB** | 118,949 | No resize transformation. "resized" in filename suggests manual resize, not IK |
| `VAX_SpotWash_Home_Pet-Design kitchen.jpg` | **39.3 GB** | 21,080 | No resize transformation on a 39GB asset |
| `VAX_Platinum_SmartWash_Pet-Design_3Qtr_Hero.jpg` | **39.0 GB** | 14,009 | `q_auto` only, no width |

**Estimated potential saving from adding `c-at_max:w-1280` to these 6 images alone: ~80–100 GB/month**

### Well-Optimised Top Images ✅
Most navigation images (`SmartWash Pet Design Nav`, `ONEPWR Battery Nav`, `Glide 2 Nav`, etc.) correctly use `tr:c-at_max:w-864` and are delivering WebP via `f-auto`.

---

## 6. Top Videos — Format & Size Flags ⚠️

### Highest Bandwidth Videos
| Video | Bandwidth | Views | Issues |
|-------|-----------|-------|--------|
| `HomePro_Pus_-UGC.mp4` | **29.3 GB** | 6,672 | MP4 only, `e_loop:100/q_auto` — no width cap, no WebM |
| `UGC_-_HomePro-Pet-Design.mp4` | **22.7 GB** | 6,573 | MP4 only, no width, no WebM |
| `UGC_-_HomePro_1.mp4` | **19.8 GB** | 6,497 | MP4 only, no width, no WebM |
| `Platinum_smartwash_petdesign.mp4` | **19.5 GB** | 5,965 | Stored in bupk9kgio (staging?), no transformation |
| `HomePro_Pet_-UGC.mp4` | **11.1 GB** | 6,470 | MP4 only, no width, no WebM |
| `vax-platinum-smartwash-bg-loop-brushbars-480p_tjgt1g.mp4` | 19.7 GB | 39,512 | ✅ Uses `w_579` — good |
| `SmartWash_PetDesign_Loop_BrushBar.mp4` | 19.0 GB | 40,235 | ✅ Uses `w_579` — good |

**Top 4 UGC videos combined: 83GB, 25,207 views** — all served as full-resolution MP4 with no width constraint. These videos are likely 1920px+ source files being streamed to mobile users.

**Best practice for these**: Add `w_896` or `w_579` + `f_auto` (for WebM delivery) + `q_auto` to all looping UGC videos.

### Video WebM Delivery Gap
Only 2 WebM video variants appear in top videos (`vax-platinum-smartwash-bg-loop.webm` and `SmartWash_PetDesign_Loop_BrushBar.webm`). The top UGC videos have no WebM equivalents being served. Given WebM averages ~30% smaller than MP4, adding `f-auto` to video URLs would enable automatic WebM delivery for supported browsers.

---

## 7. Cache Analysis ⚠️

### Status Code Breakdown
| Status | Count | Meaning |
|--------|-------|---------|
| 200 | 33,075,098 | Fresh responses |
| 206 | 176,864 | Partial content (byte-range, video seeks) |
| 304 | 16,721 | Browser cache reuse |
| 404 | 41,350 | Not found |
| 400 | 2,154 | Bad request |
| 0 | 16,857 | Unresolved |

**304 / (200+206+304) = 16,721 / 33,268,683 = 0.05% browser cache reuse** — extremely low. This suggests `Cache-Control` headers may not be optimal for browser-level caching on the Vax website.

**Note:** The `savings` section in the analytics data returned `sav: 0, size: 0` — this field tracks compression savings vs unoptimised delivery. This may indicate the savings comparison baseline is not configured, or a reporting gap for this period.

### Transformation Fragmentation Impact on Cache
50 unique transformations mean each image can have 50+ distinct CDN cache entries. This dilutes cache efficiency. Consolidating to fewer breakpoints (e.g. 320, 480, 768, 1024, 1440, 2160) would reduce unique cache keys and improve CDN hit rates for repeat visitors.

---

## 8. 404 Errors ⚠️

41,350 total 404s (0.1% of all requests).

### Top 404 URLs
| URL (truncated) | Views | Issue |
|----------------|-------|-------|
| `5f480b9dab2e49e99f060c5c35358d162dd61dce_2.jpg` | 974 | File not found at origin — likely deleted asset still referenced |
| LiftoutSKU3/4/1 thumbnail (double-encoded) | 145–73 | URL double-encoding issue (`%2520` instead of `%20`) |
| LiftOut multi-pet images | 80–108 | Malformed `tr%3Aw-912` (URL-encoded colon, should be `tr:w-912`) |
| Compact Power Max support images | 20–25 each | Support page assets missing from origin |

**Pattern:** Multiple 404s caused by URL encoding bugs (`%253A` = double-encoded `:`, should be `%3A`). These result in valid transformation strings being passed as literal paths. Fix: ensure transformation parameters are not double-encoded by the CMS/frontend.

---

## 9. Referral & Geography

### Top Referrers
| Referrer | Requests | % |
|---------|----------|---|
| www.vax.co.uk | 30,206,114 | 73.6% |
| support.vax.co.uk | 1,769,937 | 4.3% |
| fbapp (Facebook) | 304,108 | 0.7% |
| careline.vax.co.uk | 94,929 | 0.2% |

### Bot/Scraper Traffic
Significant crawler/scraper traffic observed in `topOthers` — hundreds of requests to paths like `/assets/images/logo-cn-vpnweb.png`, `/Alvin9999/https/fanfan1.net/daohang/`, various favicon.ico scrapes from ~100 unique bot IPs. These generate 404s with zero bandwidth but inflate request counts.

### Geography
| Country | Requests | % | Bandwidth |
|---------|----------|---|-----------|
| UK | 30,831,878 | **92.8%** | 2.13 TB |
| USA | 876,558 | 2.6% | 46.6 GB |
| Germany | 323,555 | 1.0% | 29.7 GB |
| Netherlands | 302,957 | 0.9% | 19.8 GB |
| France | 178,267 | 0.5% | 11.4 GB |

---

## 10. Summary: What's Working vs What Needs Attention

### ✅ Working Well
| Area | Finding |
|------|---------|
| WebP delivery | 93.5% of image requests served as WebP — excellent |
| Responsive resizing | `c-at_max` used correctly across navigation and product images |
| Product card resizing | `cm-pad_resize:w-392` delivering 7.6M correctly-sized thumbnails |
| Video WebM | 54.9% of video requests served as WebM |
| UK CDN coverage | 92.8% of traffic from UK — CDN proximity excellent |
| GIF optimisation | `.gif` animations serving correctly with `f_auto` where applied |

### ⚠️ Needs Attention
| Area | Issue | Priority |
|------|-------|----------|
| AVIF not enabled | 0 AVIF requests — potential ~20-30% bandwidth saving | HIGH |
| Top hero images without resize | 6 images consuming 192+ GB without width constraints | HIGH |
| Top UGC videos without resize/WebM | 4 UGC videos consuming 83GB as full-res MP4 | HIGH |
| Social in-app traffic (20.6%) | Facebook/Instagram in-app browsers may miss format optimisation | MEDIUM |
| 50 unique transformations | Cache fragmentation — CDN cannot consolidate hits | MEDIUM |
| Double-encoded URL 404s | Malformed transformation params generating 404s | MEDIUM |
| 304 browser cache rate 0.05% | Cache-Control may not be leveraged by Vax website | LOW |
| w-2160 at 733K requests | Very large images served to many users | LOW |
| Savings tracking = 0 | Analytics savings baseline not configured | LOW |
