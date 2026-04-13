# Analytics Agent — Video Extension Prompt

> Run this AFTER prompt.md (images analysis) has completed.
> Merge with prompt.md once video-specific technical details are finalised.
> Replace `[CUSTOMER NAME]`, `[PERIOD]`, and `[JSON FILE]` before running.

---

```
Continue the analysis for [CUSTOMER NAME] — [PERIOD]. The image analysis from prompt.md is already complete and output files exist. This prompt adds video-specific phases to those files.

Before starting: confirm guardrails.md and schema.md are already loaded from the image run. If not, re-read them now.

Append all video findings to the existing analysis file `outputs/[account]-[period]-analysis.md`.
Append all trace entries to the existing trace file `outputs/[account]-[period]-trace.md`.
Update the customer report `outputs/[account]-[period]-customer-report.md` with a Video section.

---

## VIDEO PHASE 1 — VIDEO FORMAT DELIVERY

Read: `formatWise` (video entries only), `topVideos.bandwidthWise`, `topVideos.requestWise`

This phase answers: **what video formats did ImageKit serve this month?**

From `formatWise`, isolate video format entries (MP4, WebM, MOV, etc.):
- List all video formats served with request count and bandwidth
- If WebM requests > 0 → ✅ video format optimisation is active
- If WebM = 0 → ⚠️ MP4-only delivery — `f-auto` is not applied to video URLs
  - **Recommendation:** Add `f-auto` to video transformation strings. ImageKit will serve WebM to supporting browsers, MP4 as fallback. WebM is 20–30% more efficient than MP4. ⚠️ Estimate saving = MP4 video bandwidth × 20–30%.
  - Reference: https://imagekit.io/docs/video-transformation#first-time-request-and-cache
- Check `tr=orig` entries — these are intermediate responses for first-time video transformation requests that are not yet cached. They are NOT errors. Do not flag as a failure.
  - Reference: https://imagekit.io/docs/video-transformation#first-time-request-and-cache

Append findings to analysis file. Append trace entry.

---

## VIDEO PHASE 2 — TOP VIDEO ASSETS

Read: `topVideos.bandwidthWise`, `topVideos.requestWise`

Asset-level efficiency check for videos.

For each top video:
- Is a width cap transformation applied? (`w-` in the transform string)
- Is format optimisation applied? (`f-auto` in the transform string)
- Bandwidth per view = total bandwidth ÷ view count → flag if > 10MB per view

**Fetch video dimensions using ffprobe for videos with no width cap:**

```bash
ffprobe -v quiet -print_format json -show_streams '[VIDEO_URL]' 2>&1 | python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data.get('streams', []):
    if s.get('codec_type') == 'video':
        print(s.get('width'), 'x', s.get('height'))
"
```

If ffprobe is not available, note the URL and flag that dimensions could not be determined — do not skip the asset.

**Flag rules:**
- Bandwidth per view > 10MB → 🔴 unoptimised video
  - **Recommendation:** Add `w-[appropriate width]` to cap resolution and `f-auto` for WebM delivery. Start with `w-1280` as a standard HD cap. Reference: https://imagekit.io/docs/video-transformation
- Video width > 1920px with no width cap → ⚠️ source-resolution delivery to all devices
  - **Recommendation:** Add `c-at_max,w-1280` or lower depending on display context. Confirm max display width with customer.
- No `f-auto` on video URL → flag (connects to Video Phase 1 finding)
  - **Recommendation:** Add `f-auto` to the transform string — covered in Video Phase 1.
- `tr=orig` in analytics data for this video → this is the first-time intermediate response, not an error. Note it and confirm with customer that it occurred during initial cache warm-up.

Append findings to analysis file. Append trace entry.

---

## VIDEO PHASE 3 — VIDEO TRANSFORMATION ANALYSIS

Read: `videoTransform.items`

- Count unique video transformation strings
- List top 10 by request count
- Identify near-duplicate breakpoints (width difference < 10px)
- Check whether `f-auto` is present across the majority of transform strings
- Check for hardcoded format params (`f-mp4`, `f-mov`) that block WebM delivery

**Flag rules:**
- Unique video transforms > 15 → transformation sprawl for video
  - **Recommendation:** Consolidate to a small set of standard video widths (e.g. 480, 720, 1080, 1280). Too many unique transforms fragment CDN caching.
- Hardcoded `f-mp4` or `f-mov` → blocks WebM delivery regardless of `f-auto` being present elsewhere
  - **Recommendation:** Remove hardcoded format params and use `f-auto` to allow format negotiation.
- Videos with resize but no `f-auto` → partial optimisation
  - **Recommendation:** Add `f-auto` to existing video transform strings.

Append findings to analysis file. Append trace entry.

---

## VIDEO PHASE 4 — VPU CONSUMPTION

Read: `videoProcessingUnits`

VPU (Video Processing Units) are consumed once per unique video transformation on the first request. Subsequent requests serve from cache.

- Total VPU consumed this period
- Daily VPU trend from `videoProcessingUnits.dateWise` — identify spikes
- Cross-reference VPU spike days with `videoTransform.items` — were new transform strings introduced?
- Thumbnail generation: each unique thumbnail size = 30 VPU. If multiple thumbnail sizes per video are used, calculate the per-video VPU cost.

**VPU pricing reference:**
- SD (< 1280×720 px total pixels) = 1 VPU per second of video processed
- HD (≥ 1280×720 and < 3840×2160) = 2 VPU per second
- Thumbnail = 30 VPU per unique size
- Reference: https://imagekit.io/docs/how-pricing-works#video-processing-units-pricing

**Flag rules:**
- VPU spike that correlates with new transform strings being introduced → explain the first-request cost
  - **Recommendation:** Pre-process popular videos with standard transforms rather than relying on on-demand first-request processing.
- Multiple thumbnail sizes per video → each additional size = 30 VPU
  - **Recommendation:** Standardise on 2–3 thumbnail sizes maximum. Audit `videoTransform.items` for thumbnail transform strings.
- ⚠️ VPU applies to video processing ONLY — never reference VPU for image findings.

Append findings to analysis file. Append trace entry.

---

## VIDEO PHASE 5 — VIDEO-SPECIFIC RECOMMENDATIONS SUMMARY

After all video phases complete, produce a consolidated video recommendations table in the analysis file:

| Area | Finding | Priority | Recommendation |
|---|---|---|---|
| Video Format | WebM delivery status | HIGH / MEDIUM | |
| Video Resize | Width cap on top videos | HIGH / MEDIUM | |
| Video Transforms | Unique transform count | MEDIUM / LOW | |
| VPU | Consumption pattern | MEDIUM / LOW | |

---

## UPDATE CUSTOMER REPORT

Add a **Video Performance** section to `outputs/[account]-[period]-customer-report.md`:

- 2–3 sentences on what video formats are being served and whether format optimisation is active
- Flag the highest-impact opportunity (usually: add `f-auto` for WebM delivery or add width cap for oversized videos)
- One action item with expected improvement estimate (flagged ⚠️)
- Do not include raw video URLs, VPU numbers, or transform strings in the customer report

---

## VIDEO-SPECIFIC RULES

- `tr=orig` is video-only — it is the intermediate response ImageKit delivers for video transformations on first request before the cache is warm. Never flag it as an error for video. Never apply this to images.
- VPU is consumed once per unique transformation on first request. Subsequent requests serve from cache. Always explain this to avoid alarm at VPU spike data.
- MP4→WebM saving estimate: 20–30% of MP4 video bandwidth. Always flag as ⚠️ estimate.
- For video dimensions use ffprobe — not ImageKit headers, not Pillow/ImageMagick.
- Never reference VPU in any image-related finding.
- Reference: https://imagekit.io/docs/video-transformation#first-time-request-and-cache | https://imagekit.io/docs/how-pricing-works#video-processing-units-pricing
```
