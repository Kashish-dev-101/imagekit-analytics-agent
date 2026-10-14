# Analytics Agent — Full Prompt (Images + Video)

> This is the analysis prompt the skills execute. To run, use a skill (e.g. `/analytics-run <hint>`).
> Drop the customer JSON in `data/input/` first; the skill resolves the file and reads the period from the data.

## Step 0 — Run the extractor first (saves ~80% of read time)

The extractor pre-computes totals, spike detection, format sums, and per-view sizes into a compact ~35KB file instead of the raw JSON which can be 150KB+.

Check if `data/extracted/[ACCOUNT]-extracted.txt` already exists. If not, run:

```bash
python3 agent/extract.py data/input/[JSON FILE].json > data/extracted/[ACCOUNT]-extracted.txt
```

Then use `data/extracted/[ACCOUNT]-extracted.txt` as the data file for all phases below.

---

You are an ImageKit Customer Success Manager analysing a customer's monthly analytics JSON export to prepare for an account review call.

Before starting anything: use the Read tool to read `.claude/rules/guardrails.md` in this project. Follow all rules in guardrails.md throughout this entire run — it contains technical rules, UA classification patterns, flag thresholds, and bandwidth saving estimates.

The data file you will read is the pre-extracted summary (not the raw JSON). All key fields are present. If a specific URL or field is missing from the extract, note it but do not attempt to read the raw JSON — the extract covers all fields used in the prompt phases.

Analytics reference: https://imagekit.io/docs/usage-analytics

---

## ACCOUNT CONTEXT (optional)

If the user provided account context in their message — call purpose, known concerns, account history, what the customer has been asking about — incorporate it into the analysis and customer-facing report where relevant. If no context was provided, proceed with the data alone.

---

## SETUP — Create Output Files

Create three output files immediately using the Write tool before any analysis begins. Write to `data/output/[account]/` — create the folder if it doesn't exist:

- `data/output/[account]/[account]-[period]-trace.md` — analysis trace (internal evidence and calculation log)
- `data/output/[account]/[account]-[period]-analysis.md` — full technical analysis (internal)
- `data/output/[account]/[account]-[period]-customer-report.md` — customer-facing monthly report

All three start with just the title and date as placeholders.

After every phase, use the Edit tool to append findings to the analysis file and append a trace entry to the trace file before moving to the next phase. Each phase ends with an explicit write gate — do not skip it.

---

## TRACE FORMAT

The trace file has two parts: an Audit Summary initialised before Phase 0 and completed after Phase 7, and per-phase entries appended after each phase. Record observable evidence, calculations, and concise explanations of conclusions. Do not request or reproduce private internal thinking or a deliberation transcript.

### Part 1 — Audit Summary (initialise before Phase 0, complete after Phase 7)

**Use the Edit tool to initialise the Audit Summary at the top of the trace file now, with the account, period, extracted data file path, and any supplied account context. Do not start Phase 0 until this write is confirmed complete.** Leave findings pending until the relevant phases are complete.

After Phase 7, complete this section with a concise evidence-based debrief for a colleague. Write in plain prose, not bullet points, using the recorded phase results.

Cover:

- Main account findings, with supporting fields and values
- Possible causes supported or excluded by specific evidence; label unconfirmed causes with ⚠️
- Connections between phase results, citing the relevant measurements
- Data inconsistencies, validation results, and unresolved limitations
- Checks that produced no flag, with the measured value and applicable threshold or exclusion rule
- Operational implications of transform sprawl, top assets, or IP patterns; label inferred team structure or process with ⚠️

Keep explanations focused on the evidence supporting the reported results.

### Part 2 — Per-Phase Entries (append after each phase)

After every phase, append to `[account]-[period]-trace.md` using this structure:

```
## Phase [N] — [Phase Name]

### Data Read
- Fields accessed: [list of JSON keys read]
- Key values: [the actual numbers that drove decisions]

### Arithmetic
- Show key calculations explicitly: sums, percentages, per-view sizes, rates
- E.g. format_sum = 1,412M + 729M + ... = 3,580M → 83.9% of request.total

### Decision
- [Finding and a brief explanation based on the recorded evidence]
- [Which threshold was applied and what the value was]
- [Any ambiguity or assumption — mark with ⚠️]
```

The trace is never shared with the customer. Its purpose is to document the data accessed, reproducible calculations, and evidence supporting each conclusion.

---

## PHASE 0 — DATA INTEGRITY CHECK

This phase answers: **is the data even trustworthy?** Checks whether dimensional breakdowns (format, device) are truncated by a known platform bug — every other phase's percentages depend on this being verified first.

Before drawing any conclusions, verify whether the dimensional breakdowns are complete or truncated.

1. Sum all `count` values in `formatWise.requestWise` → `format_sum`
2. Sum all `count` values in `deviceDistribution` → `device_sum`
3. Compare both to `request.total`

**Decision:**

- If both sums are within 5% of `request.total` → breakdowns are complete, proceed normally
- If both sums are significantly less than `request.total` (e.g. <20%) → data is truncated. This is a known platform bug. Add a prominent warning at the top of the analysis file before any other content. All % calculations from dimensional data will only reflect the visible subset — state this caveat wherever you use breakdown numbers.
- The `request.pattern` breakdown is NOT affected by this truncation and always sums to 100% of total.

**If breakdowns are complete:** skip the full trace template — write one line instead: "Phase 0 — Data integrity check: formatWise (X%) and deviceDistribution (Y%) both within 5% of total. No truncation, proceeding normally." Nothing is added to the analysis file (there's no Phase 0 section in OUTPUT 1 — only the truncation warning, if applicable).

**Do NOT use the Data Read / Arithmetic / Decision structure for Phase 0 when no truncation is found.** That full trace structure is for Phases 1–7 only. One line in the trace, nothing in the analysis file.

**If truncation is detected:** use the full trace entry structure (Data Read / Arithmetic / Decision) from TRACE FORMAT, and add the prominent warning to the analysis file as described above.

---

## PHASE 1 — TRAFFIC SUMMARY

This phase answers: **how much traffic did this account receive this month, and where did it come from?** Establishes the baseline volume/trend picture — no optimization findings yet, those start in Phase 2. Also captures storage usage as a DAM-relevance signal for the CSM.

Read: `request.total`, `bandwidth.total`, `storage_bytes.total`, `request.dateWise`, `bandwidth.dateWise`, `request.pattern`, `country.items`, `referral.items`, `formatWise`

- Overall requests + bandwidth for the period
- **Average object size (REQUIRED — do not skip):** from `formatWise`, sum bandwidth and requests for all entries where `name` starts with `image/` (images) and separately where `name` starts with `video/` (video). Compute:
  - Average image size = total image bandwidth ÷ total image requests
  - Average video size = total video bandwidth ÷ total video requests
  - Report both. These headline numbers give immediate context for the bandwidth totals and are carried into Phase 2.
- Storage used: report the total. If `storage_bytes.total` exceeds 500 GB (guardrails §11), note it as a DAM-relevance signal for the CSM — this volume of stored media is a natural fit for ImageKit's DAM features (organization, search, versioning, workflows). Internal note only, in the analysis file — never add it to the OUTPUT 2 fixed opportunity taxonomy, since it's a product-fit signal, not a technical finding.
- Daily trend from `dateWise` — is traffic growing, flat, or declining?
- Spike detection: flag daily spikes in either requests or bandwidth per §11 thresholds — the two can spike independently (e.g. one large video going viral raises bandwidth with little change in request count)
  - **Recommendation if spike found:** Note the date and ask customer on the call whether it was a campaign, product launch, or unexpected event
- Pattern breakdown: which URL groups / folders drive the most traffic and bandwidth

**Top countries:**
List the top 5 countries by request count and bandwidth. Note any single-market concentration (one country > 60% of requests). Keep this summary-level — no deep analysis needed here.

**Top referrers:**
List the top 5 referral domains with request count and bandwidth. Keep this summary-level.

⚠️ Important caveat: `referral.items` will not represent total traffic. Native mobile app clients (OkHttp, URLSession, Dart) do not send a `Referer` header, so all native app traffic appears as no-referrer and is excluded from this breakdown. The referrer data reflects browser and web traffic only — do not compare the referrer total against `request.total`.

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

**After writing Phase 1, also write the Account Summary section to the analysis file.** This section must appear BEFORE all phase sections — insert it at the top of the analysis file, after the header. Cover: who the customer is, how they use ImageKit, storage architecture (flag with ⚠️ if inferred), primary market. Do not skip this section.

---

## PHASE 2 — FORMAT DELIVERY

> Apply flag thresholds from guardrails §11 — do not use your own judgment on what counts as high or low.

Read: `formatWise` only.

This phase answers: **what formats did ImageKit serve this month for images and video?** Aggregate picture only. Asset-level checks happen in Phase 4.

### Images

- List all image formats served (entries from `formatWise.requestWise` where `name` starts with `image/`) with request count, bandwidth, and avg size per format (bandwidth ÷ requests)
- If WebP or AVIF is the dominant image format → ✅ format delivery is in a good state
- If AVIF requests > 0 → ✅ AVIF is enabled on this account
- If AVIF = 0 AND WebP is the leading image format → optimisation opportunity, not a failure. AVIF must be activated by ImageKit on the account — it is not self-serve.
  - **Recommendation:** AVIF is not currently enabled. Since WebP is working well, enabling AVIF is the next step — 20–30% more efficient than WebP with no URL or code changes required once enabled. ⚠️ Estimated saving = WebP bandwidth × 20–30%. Customer should request enablement from their ImageKit account manager.
- If JPEG + PNG combined > 30% of image requests (per guardrails §11):
  - Do not flag yet — note the volume, mark for root cause in Phase 3
  - Possible causes: native mobile app traffic (no `Accept` header), bots, or hardcoded `f-jpg`/`f-png` in URLs — Phase 3 UA classification will confirm
- If GIF requests > 0 → flag immediately
  - **Recommendation:** Convert GIFs to video — append `/ik-gif-video.mp4` to the GIF URL. No changes to the original GIF file — but the `<img>` tag in the HTML must be replaced with a `<video>` tag. Videos are significantly smaller than GIFs for the same animation, and the output can be further optimised with ImageKit's standard video transformations (resize, format, codec).
  - Note: if the GIF is displayed in an `<img>` tag and converting to a video element is not feasible, adding `f-auto` to the URL will automatically serve animated WebP to supporting browsers instead.
  - Reference: https://imagekit.io/docs/vector-and-animated-images#gif-to-video
- Reference: https://imagekit.io/docs/image-optimization

### Video

- List all video formats served (entries from `formatWise.requestWise` where `name` starts with `video/`) with request count, bandwidth, and avg size per format (bandwidth ÷ requests)
- If WebM requests > 0 → ✅ video format delivery is working. This can be from two paths:
  (1) ImageKit auto-detecting browser WebM support via the `User-Agent` header (`vary: User-Agent`) — different from images which use the `Accept` header, or
  (2) `f-webm` hardcoded in the transform string for native app URLs.
  Both WebM and MP4 appearing together is the expected state.
- If no WebM in formatWise (MP4, MOV, or other formats only) → root cause is one of: (a) native app / non-browser traffic where ImageKit cannot detect WebM support from the User-Agent, (b) a hardcoded format param (`f-mp4`, `f-mov`) blocking WebM, or (c) video URLs without a `.mp4` or `.mov` extension — ImageKit does not recognise these as video and serves them unprocessed at source resolution in their original format (MP4, MOV, or other), so no WebM variant is ever generated.
  Do not flag as missing `f-auto` — account-level setting or `f-auto` may already be configured; the UA or the missing extension is the limiting factor.
  - **Recommendation:** Check Phase 3 — if native app or bot traffic is significant, those clients are likely driving the delivery. For native app video URLs, explicitly force the format in the URL. For browser traffic still receiving non-WebM formats, check transform strings for hardcoded format overrides. For cause (c), append `/ik-video.mp4` to the URL — Phase 4 top video assets will surface unextended URLs if present.
  - Reference: https://imagekit.io/docs/video-optimization#automatic-format-conversion

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## PHASE 3 — TRAFFIC SOURCE CLASSIFICATION

> Apply flag thresholds from guardrails §11 — do not use your own judgment on what counts as high or low.

Read: `topUserAgent`

This phase answers: **who is making these requests, and does the client mix explain Phase 2's format findings?** Classifies traffic into web browsers, native apps, in-app browsers, bots, and server-side clients — then cross-references the UA breakdown against Phase 2 format observations to confirm root causes, not surface new ones.

Each entry in `topUserAgent` already has a pre-classified `label=` from `extract.py`. Use those labels to group entries into categories:

| Category                   | Label prefix                                                                                              |
| -------------------------- | --------------------------------------------------------------------------------------------------------- |
| Web Browser                | `Chrome`, `Safari`, `Firefox`, `Edge`, `Samsung Browser` (any browser name without `Native App` or `Bot`) |
| Native Mobile App          | `Native App ·`                                                                                            |
| In-App Browser             | `In-App Browser ·`                                                                                        |
| Bot / AI Agent             | `Bot ·`                                                                                                   |
| Server-side / Programmatic | `Server-side ·`                                                                                           |
| Unclassified               | `Unclassified` — use general knowledge to make a best-effort inference; flag with ⚠️                      |

Sum request counts per category. Produce a summary table:

| Category | Requests | % of Total | Bandwidth | Notes |
| -------- | -------- | ---------- | --------- | ----- |

**Mobile browser %:**

Within Web Browser entries, identify mobile UAs by their label — `· Mobile` in the device-type portion of the label (e.g. `Chrome 124 · Android 13 · Mobile`). Sum mobile browser requests and desktop browser requests separately.

Mobile browser % of total browser traffic = `mobile_browser_requests` / (`mobile_browser_requests` + `desktop_browser_requests`) × 100.

State the mobile browser % clearly — it is carried forward into Phase 4.

**Cross-reference with Phase 2 format findings:**

For images:

- If Phase 2 noted JPEG/PNG > 30% → check whether Native Mobile App or Bot traffic accounts for it. These clients do not send `Accept: image/webp` and will receive the original format. This is the root cause, not a configuration failure.
- If JPEG/PNG cannot be explained by native app or bot traffic → likely a hardcoded `f-jpg`/`f-png` in the URL. Flag for Phase 4 to confirm at asset level.

For video:

- If Phase 2 found no WebM in formatWise → check whether Native Mobile App or Bot traffic accounts for it. These clients do not send a standard browser User-Agent, so ImageKit cannot detect WebM support. This is the root cause.
- If browser traffic is significant yet no WebM is being served → check for hardcoded `f-mp4`/`f-mov` in video transform strings (Phase 5).

**Flag rules:**

- Mobile browser % > 50% of browser traffic → flag HIGH and carry to Phase 4
  - **Recommendation:** Mobile is the majority of browser traffic. Images without resize transforms are being requested at source resolution by most users. Phase 4 resize optimisation is the highest-impact action for this account.
- Mobile browser % > 0% → always carry mobile % to Phase 4 regardless of volume
- Native Mobile App detected:
  - For images → use speculative language — we see the UA signal but cannot confirm format delivery from logs. Flag by client type:
    - **Flutter / Dart:** recommend `f-webp` only. Do NOT recommend `f-avif` — not natively supported in Flutter, regardless of Android/iOS version underneath. Reference: `agent/docs/native-mobile-format-support.md`
    - **iOS native (CFNetwork / URLSession):** recommend `f-webp`. Safe for iOS 14+. If account context confirms a minimum supported OS of iOS 16+, `f-avif` can also be recommended for further savings.
    - **Android native (OkHttp):** recommend `f-webp`. Safe for Android 4.0+. If account context confirms a minimum supported OS of Android 14+, `f-avif` can also be recommended — but this gate is required: always write it as "If your minimum supported Android version is 14+, you could also use `f-avif` for further compression savings." Never recommend AVIF for Android without the version caveat, even if AVIF is already active on the account.
  - Do not flag if there is clear evidence the customer is already explicitly setting `f-webp` in app URLs — that means they've solved it.
  - For video → flag: native app clients do not send a standard User-Agent, so ImageKit cannot detect WebM support automatically. The correct fix is platform-specific, not a single generic format:
    - **Android native (OkHttp) / Flutter-Android:** safe to force `f-webm` (VP9) — plays natively via ExoPlayer from Android 4.4+.
    - **iOS native (CFNetwork/URLSession) / Flutter-iOS:** force `f-mp4` (H.264) only. WebM (VP9 or AV1) never plays on iOS via ImageKit — AVPlayer cannot open the WebM container at all, regardless of chip. Do not recommend `f-webm` or `vc-av1` for iOS native traffic under any circumstance.
  - Reference: https://imagekit.io/docs/production-checklist#mobile-app-specific-optimizations and `agent/docs/native-mobile-format-support.md`
- Bot / AI Agent > 15% of total requests → flag
  - **Recommendation:** Non-human traffic inflates usage metrics. Discuss on the call whether this is expected and whether rate limiting is needed.
- In-App Browser > 10% → flag
  - **Recommendation:** In-app browser Accept header behaviour can be inconsistent. Test format delivery from Facebook/Instagram in-app browser. If JPEG is being served, add explicit `f-webp` to URLs loaded in social contexts.

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## PHASE 4 — RESIZE, TRANSFORM COVERAGE & TOP ASSETS

> Apply flag thresholds from guardrails §11 — do not use your own judgment on what counts as high or low.

Read: `transform`, `formatWise.bandwidthWise`, `topImages.bandwidthWise`, `topImages.requestWise`, `topVideos.bandwidthWise`, `topVideos.requestWise`, `topOthers.bandwidthWise`

This phase answers: **how widely are ImageKit transforms being used, and are high-traffic assets being resized and optimised?**

**Step 1: Image transform bandwidth coverage**

From `transform.bandwidthWise`, read the parent `bandwidth` field — this is the total bandwidth of all image requests that had an explicit transform string in the URL. No need to sum items; the parent field is already the total.

From `formatWise.bandwidthWise`, sum the `bandwidth` field for all entries where `name` starts with `image/` → `image_bandwidth`.

Coverage % = `transform.bandwidthWise.bandwidth` / `image_bandwidth` × 100.

**Coverage is bandwidth-based, not request-based.** Do not use `transform.requestWise` counts for this calculation — use `transform.bandwidthWise.bandwidth` divided by `image_bandwidth` only.

Note: this measures explicit URL-based transform coverage (resize, crop, named transforms) only. Auto format conversion via account-level settings (WebP/AVIF delivery) is not counted here — that is captured in Phase 2 via `formatWise`.

- If > 50% → ✅ write exactly **"Strong coverage"**
- If 20–50% → ⚠️ write exactly **"Partial coverage"**
- If < 20% → 🔴 write exactly **"Low coverage"**

**The label and flag must match the same band.** Never mix them — e.g. if coverage is 13%, the label is "Low coverage" and the flag is 🔴. Writing "Partial coverage (13%)" with a 🔴 flag is wrong. Writing "Low coverage (13%)" with a ⚠️ flag is also wrong.

**Step 2: Mobile context**
Use the mobile browser % from Phase 3 as context. State it once: "X% of browser traffic is from mobile devices."

**Step 3: Top images**
From `topImages.bandwidthWise`, for each image:

- Named transformation (`n-[name]`) in the URL? → note it, skip all param checks — params are inside the named transform in the dashboard
- SVG file? → **skip immediately, do not flag under any circumstances.** SVGs are vector format — they scale without quality loss and resize transforms are meaningless for them. Never flag an SVG for missing resize regardless of its file size or bandwidth per view.
- Resize param present? Check `w-`, `h-` (ImageKit-native). For URL-rewriter accounts, also check per guardrails §13: `imwidth=`, `im=Resize=` (Akamai), `w_` (Cloudinary), `w=` (Imgix)
- Hardcoded `f-jpg` or `f-png`? (only if no named transform)
- Bandwidth per view = `bandwidth ÷ views`

**Exclusion rules — skip dimension fetch, do not flag:**

- Image path already encodes a size (e.g. `630x420` in the folder name)
- Bandwidth per view < 40KB — not a priority

**Before you can flag or skip any image with no resize param, you MUST run the source dimension fetch.** Without actual dimensions you cannot apply the flag rules correctly — do not estimate or infer dimensions from the URL or filename.

For images with no resize param (after exclusions), fetch source dimensions:

```bash
python3 -c "
from PIL import Image
import io, urllib.request
url = '[IMAGE_URL]'
req = urllib.request.Request(url, headers={'Range': 'bytes=0-65535'})
data = urllib.request.urlopen(req, timeout=10).read()
img = Image.open(io.BytesIO(data))
print(img.size)
"
```

If Pillow is not available:

```bash
curl -sL -r 0-65535 '[IMAGE_URL]' | identify -
```

**Flag rules:**

- Bandwidth per view > 2MB AND no resize → 🔴 oversized image
  - **Recommendation:** Add `c-at_max,w-[appropriate width]` to the URL. Reference: https://imagekit.io/docs/image-resize-and-crop
- Image width > 1500px AND no resize → ⚠️ use speculative language: "This image appears to be [W×H]px with no resize transform. Mobile users may be receiving it at source resolution — confirm whether resizing is handled at the application layer."
  - **Recommendation:** Add `c-at_max,w-[appropriate width]`. Reference: https://imagekit.io/docs/image-resize-and-crop
- Image width 800–1500px, no resize → note but do not flag HIGH — worth mentioning if mobile traffic is significant (cross-reference Step 2)
- Image width ≤ 800px, no resize → skip
- Hardcoded `f-jpg` or `f-png` → flag in OUTPUT 1 only — actively blocks WebP/AVIF delivery. Do NOT surface in customer report — native app traffic may be intentionally hardcoding format
  - **Recommendation (OUTPUT 1 only):** Replace with `f-auto`, or remove if account-level format optimisation is enabled. For native app URLs confirmed in Phase 3, use `f-webp` explicitly.
- No format param → do not flag. Account setting or `f-auto` may be handling it. Only flag if Phase 2 shows unexplained JPEG/PNG volume not accounted for by native app or bot traffic.

**Step 4: Top videos**
From `topVideos.bandwidthWise`, for each video URL:

- Named transformation (`n-[name]`)? → note it, skip all param checks
- URL ends with `/ik-master.m3u8` or `/ik-master.mpd` → ABS manifest URL, not a progressive video. Skip per-view bandwidth analysis and width cap checks — manifest files are negligible in size, actual segment delivery is not captured in analytics. Note ABS is active → ✅. See Phase 5 Video Transform Strategy for ABS strategy details.
- `tr=orig` or `tr:orig` present → note: ImageKit's intermediate response — processed version not ready when request arrived. If frequent, URLs are not being pre-warmed.
  - **Recommendation:** Pre-warm video transformation URLs by requesting each one before going live.
- No `.mp4` or `.mov` extension in the URL path → ⚠️ ImageKit cannot identify this as video and serves it unprocessed at source format and resolution
  - **Recommendation:** Append `/ik-video.mp4` to the URL path. Reference: https://imagekit.io/docs/video-optimization#automatic-format-conversion
- Width cap present? Check `w-` (ImageKit-native). For URL-rewriter accounts, also check per guardrails §13: `imwidth=` (Akamai), `w_` (Cloudinary), `w=` (Imgix). Only if no named transform.
- Hardcoded `f-mp4` or `f-mov`? — only if no named transform
- Bandwidth per view = `bandwidth ÷ views`

**Exclusion rules — skip width check, do not flag:**

- Bandwidth per view < 500KB — not a priority

**Flag rules:**

**Before flagging any video as unoptimised, run ffprobe to confirm source dimensions.** Do not apply the flag rules without the actual width — a video may look large by bandwidth alone but already have a width cap the URL does not show.

```bash
ffprobe -v quiet -print_format json -show_streams -probesize 500000 -analyzeduration 0 '[VIDEO_URL]'
```

**Write the raw ffprobe JSON output block to the trace file verbatim** — the full stream info output, not just the extracted dimensions. Do not summarise it into a single line like "1080×1920, H.264". The raw output must appear in the trace before any flag decision is written.

- No width cap + bandwidth/view > 10MB → 🔴 unoptimised video
  - **Recommendation:** Add a width cap (`c-at_max,w-[width]`) to limit resolution. Confirm max display width with customer. If Phase 3 confirms significant mobile traffic, higher priority.
- No width cap + bandwidth/view 500KB–10MB → ⚠️ large video without width cap
  - **Recommendation:** Add `c-at_max,w-[width]`. Confirm max display width with customer. If Phase 3 confirms significant mobile traffic, higher priority.

**The 🔴 threshold for video is only > 10 MB/view.** Videos between 500 KB and 10 MB are ⚠️ — even at 3 MB, 5 MB, or 8 MB per view. Do not use 🔴 for videos unless bandwidth/view genuinely exceeds 10 MB. Examples: 1.6 MB/view = ⚠️. 3 MB/view = ⚠️. 8 MB/view = ⚠️. 12 MB/view = 🔴.
- Hardcoded `f-mp4` or `f-mov` → blocks WebM delivery
  - **Recommendation:** Remove hardcoded format param. Account-level setting will handle WebM delivery. For native app URLs confirmed in Phase 3, explicitly force the format.
- No format param → do not flag. Account setting or `f-auto` may be active.

**Step 5: Top Others**
From `topOthers.bandwidthWise`, list the top non-image/video assets by bandwidth. Note any unexpectedly high-bandwidth assets (large PDFs, raw fonts, scripts) served through ImageKit.

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## PHASE 5 — TRANSFORMATION ANALYSIS

> Apply flag thresholds from guardrails §11 — do not use your own judgment on what counts as high or low.

Read: `transform.requestWise.items`, `videoTransform.requestWise.items`, `resultType.requestWise`

This phase answers: **what transform strategies are in use, how well is the CDN cache being utilized, and is adaptive streaming active?** Coverage findings are in Phase 4.

---

### Images — Transform Strategy

- Count unique transformation strings from `transform.requestWise.items` — list top 10 by request count
- Named transforms (`n-` prefix) → note positively. Skip resize/format checks for pure named transform strings — underlying params are not visible in analytics.
- Identify near-duplicate breakpoints (width difference < 10px)
- Identify hardcoded `f-jpg` or `f-png` (blocks WebP/AVIF)
- Identify `orig-true` (bypasses all optimisation)

**Flag rules:**

- Unique transforms > 30 → transformation sprawl
  - **Recommendation:** Consolidate to a defined breakpoint set (e.g. 320, 480, 768, 1024, 1440). Unique transforms fragment the CDN cache.
- Near-duplicate breakpoints → consolidation opportunity
  - **Recommendation:** A 2px width difference creates two separate CDN cache keys. Pick one value per range.
- Hardcoded `f-jpg`/`f-png` → blocks WebP/AVIF
  - **Recommendation:** Replace with `f-auto`, or remove if account-level setting is enabled. Use `f-webp` for native app URLs.
- Resize present but no format param → do not flag. Flag only if Phase 2 shows unexplained non-WebP volume.
- `orig-true` → optimisation bypass
  - **Recommendation:** Confirm if intentional (download links, admin tools). If serving to end users, remove and let ImageKit optimise.

---

### Video — Transform Strategy

- Count unique video transformation strings from `videoTransform.requestWise.items` — list top 10
- Identify near-duplicate video breakpoints (width difference < 10px)
- Identify hardcoded `f-mp4` or `f-mov` (blocks WebM)
- Identify `tr=orig` entries
- Identify `sr-` params — if present, ABS (Adaptive Bitrate Streaming) is active. Note the protocol (`ik-master.m3u8` = HLS, `ik-master.mpd` = DASH) and resolution set (e.g. `sr-360_480_720`)
- Absence of `f-auto` in video transform strings → do not flag. Account setting or `f-auto` handles WebM delivery via User-Agent detection.

**Flag rules:**

- Unique video transforms > 15 → transformation sprawl for video
  - **Recommendation:** Consolidate to a small set of standard widths (e.g. 480, 720, 1080, 1280).
- Hardcoded `f-mp4` or `f-mov` → blocks WebM delivery
  - **Recommendation:** Remove hardcoded format param. Account-level setting will handle WebM delivery to supporting browsers.
- `tr=orig` → processed versions not pre-warmed before delivery
  - **Recommendation:** Pre-warm video transformation URLs by requesting each one before going live.
- ABS active via HLS → ✅ note positively — customer is using adaptive streaming. Cross-reference Phase 3: if significant iOS native app traffic is present, confirm the player handles HLS (AVPlayer supports HLS natively on iOS).
- ABS active via DASH → ✅ note positively. Cross-reference Phase 3: DASH is not natively supported on Apple devices — if iOS/Safari traffic is significant, confirm iOS users are handled separately or routed to HLS.
- ABS active with only one `sr-` rendition → no adaptation benefit — player cannot switch quality levels. **Recommendation:** Add more resolution tiers (e.g. `sr-360_480_720_1080`). Reference: https://imagekit.io/docs/adaptive-bitrate-streaming

---

### Cache Hit Rate

Read `resultType.requestWise`: cache hit rate = Hit / (Hit + Miss).

- < 80% AND (image unique transforms > 30 OR video unique transforms > 15) → transformation sprawl is likely the cause
  - **Recommendation:** Consolidating transforms will directly improve cache hit rate. ImageKit defines ≥ 80% as optimal.
- < 80% AND transforms are few → diagnose with two checks:
  1. Scan `topImages.bandwidthWise` and `topVideos.bandwidthWise` URLs for `ik-s=` or `ik-t=` params — if present, signed URLs are fragmenting the cache. Each unique `ik-t` expiry timestamp = a separate CDN cache key.
     - **Recommendation:** Use long-lived or fixed-expiry signed URLs on high-traffic assets. Avoid per-request expiry timestamps where possible.
  2. Fetch response headers from a sample URL:
     ```bash
     curl -sI '[SAMPLE_URL]' | grep -i 'cache-control\|age\|x-cache'
     ```
     If `Cache-Control: max-age` < 86400 (1 day), the CDN TTL may be too short. ImageKit's default is 1 year (`max-age=31536000`).
     - **Recommendation:** If a custom short TTL is set, confirm it's intentional. Increasing it will improve hit rate for stable assets.
- ≥ 80% → ✅ note it positively

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## PHASE 6 — TOP IPs

> Apply flag thresholds from guardrails §11 — do not use your own judgment on what counts as high or low.

Read: `topIps`

This phase answers: **are any IPs consuming a disproportionate share of requests or bandwidth — potential scraper, bot, or rogue backend?**

Scan all IPs for any of these signals:
- > 5% of total requests → request concentration
- > 10% of total bandwidth → bandwidth concentration
- > 1MB avg bandwidth/request → large unoptimized asset downloads

If no IP crosses any threshold → note "No IPs above concentration threshold." Move on.

If any IP crosses a threshold → look up each flagged IP. **Do not write any IP classification without first running the ipinfo.io lookup. Classifying from general knowledge is not acceptable — run the curl command for every flagged IP before filling the table.**

```bash
curl -s --max-time 5 https://ipinfo.io/[IP_ADDRESS]
```

Extract: `org`, `country`, `city`, `hostname`. Build a lookup table:

| IP | Requests | % Requests | % Bandwidth | Avg Asset Size | Org / Owner | Country | Classification |
|---|---|---|---|---|---|---|---|

**Classification guide:**

- Dedicated CDN (Cloudflare, Fastly, Akamai) → CDN layer in front of ImageKit — flag and confirm with customer whether this architecture is intentional
- Cloud provider (Amazon, Google, Microsoft) → could be their CDN product (CloudFront, GCF, Azure CDN), an app backend, or a scraper on cloud infra — flag and confirm with customer
- Residential ISP → end-user browser traffic, normal
- Unknown / offshore hosting → scraper risk ⚠️

**Flag rules:**

- Single IP > 5% of total requests → request concentration
  - **Recommendation:** Cross-reference `org`. Validate with customer — is this expected traffic from your CDN or app server?
- Single IP > 10% of total bandwidth → bandwidth concentration
  - **Recommendation:** Cross-reference `org`. Validate with customer — is this expected traffic from your CDN or app server?
- IP avg bandwidth/request > 1MB → large asset downloads
  - **Recommendation:** Consistently downloading large assets — confirm if legitimate backend and whether transforms are applied.

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## PHASE 7 — VPU CONSUMPTION

Read: `videoProcessingUnits`, `videoTransform.requestWise.items`, `topImages.bandwidthWise`

This phase answers: **is VPU being consumed, are there spikes, and are there any obvious cost drivers worth flagging?**

---

- **Total VPU this period** — from `videoProcessingUnits.total`. If zero → note "No VPU consumed this period." Move on.
- **Daily trend** — from `videoProcessingUnits.dateWise`. Identify any spike days. Note the date and resolution tier that drove the spike (SD / HD / 4K / 8K / 16K breakdown is per day).
- **Resolution tier** — if 4K or above is a significant share of daily VPU, note it. A width cap on source videos would reduce this.
- **AV1 check** — scan `videoTransform.requestWise.items` for `vc-av1`:
  - 10× VPU multiplier vs H.264/VP9, and AV1 is currently in **beta** on ImageKit
  - Explicit `vc-av1` is served to every client regardless of support — WebM never plays on iOS native apps. ⚠️ If Phase 3 confirmed iOS native traffic, this is a playback-breaking risk.
  - **Recommendation:** Confirm AV1 is intentional. If cost-sensitive, VP9 (`f-webm`) gives most of the compression benefit at 1× VPU cost.
- **Thumbnail check** — scan `topImages.bandwidthWise` URLs for `/ik-thumbnail.jpg`. Each unique thumbnail size = 30 VPU. If multiple sizes found, flag it.
  - **Recommendation:** Standardise on 2–3 thumbnail sizes maximum.

**Write to files now before proceeding:** Use the Edit tool to append these findings to the analysis file. Use the Edit tool to append the trace entry to the trace file. Do not start the next phase until both writes complete.

---

## OUTPUT 1 — Full Technical Analysis

The analysis file is already built incrementally. Now complete and finalise it.

Complete the trace file's Audit Summary from the recorded Phase 0–7 results before finalising the outputs.

File: `data/output/[account]/[account]-[period]-analysis.md`

**Use the exact section headings listed below. Do not use "Phase N" style headings in the analysis file — those belong in the trace file only.** Do not append `(Phase N)` or `— Phase N` to any heading. Example of what NOT to write: `## Transformation Analysis (Phase 5)`, `## Top IPs (Phase 6)`, `## VPU Consumption (Phase 7)`.

Structure:

1. **Header** — Account name, period, prepared date
2. **⚠️ Data truncation warning** (if applicable — place prominently before all sections)
3. **Account Summary** — who the customer is, how they use ImageKit, inferences flagged with ⚠️
4. **Traffic Overview** — totals + pattern breakdown + daily trend + countries + referrers

---

**IMAGE ANALYSIS**

5. **Image Format Delivery** — format table + WebP/AVIF status + GIF flags + bandwidth saving estimates + inline recommendations
6. **Traffic Source Classification** — 5-category table + mobile % + image format cross-reference + flags
7. **Image & Video Resize, Transform Coverage & Top Assets** — transform adoption % + mobile context + top image/video asset audit (resize, format params, per-view sizes, dimensions) + top others + flags

---

**VIDEO ANALYSIS**

8. **Video Format Delivery** — format table + WebM status + native app cross-reference + inline recommendations

---

**SHARED**

9. **Transformation Analysis — Cache & Coverage** — image coverage gap + image transform strategy + video transform strategy + cache hit rate
10. **Top IPs** — flagged IPs only (if any): lookup table + classification
11. **VPU Consumption** — total + daily trend + thumbnail cost
12. **Summary Table**

| Area               | Type          | Status  | Priority            | Recommendation  |
| ------------------ | ------------- | ------- | ------------------- | --------------- |
| ✅ Working Well    | Image / Video | finding | —                   | —               |
| ⚠️ Needs Attention | Image / Video | finding | HIGH / MEDIUM / LOW | one-line action |

These are the only 5 columns. Do not rename them. Do not add columns. Every finding from the analysis goes into this table as a row.

---

### Pre-Save Checklist — Output 1

Before proceeding to OUTPUT 2, verify the analysis file contains all of the following. If any are missing, add them now.

**1. Account Summary** — present as the first section after the header (and after any truncation warning). Covers: who the customer is, how they use ImageKit, storage architecture (⚠️ if inferred), primary market.

**2. All required phase sections** — verify each of these exists in the file:
- Traffic Overview
- Image Format Delivery
- Traffic Source Classification
- Image & Video Resize, Transform Coverage & Top Assets
- Video Format Delivery
- Transformation Analysis — Cache & Coverage
- VPU Consumption (even if VPU = 0 — write "No VPU consumed this period.")

**3. Summary Table** — present as the last section. Every flagged finding from the analysis has a row. No finding is omitted.

Only proceed to OUTPUT 2 after all 3 checks pass.

---

## OUTPUT 2 — Customer-Facing Monthly Report

Write `data/output/[account]/[account]-[period]-customer-report.md`.

Tone: professional and clear. Written for a business stakeholder — not an engineer. No jargon, no JSON field names, no raw URLs. Name findings by product area ("your product images", "your hero banners") not by filename or URL.

**No saving estimates in this file.** Those belong in OUTPUT 1 only.

**This file has exactly 7 sections — no more, no fewer:**
1. Header
2. Monthly Summary
3. How ImageKit Is Performing
4. Highlights
5. Images — Opportunities to Improve
6. Video — Opportunities to Improve
7. Questions for the Call

Do not add any other sections. S3 errors, origin permission issues, infrastructure problems, 404 summaries, error logs — all of these stay in OUTPUT 1 only. If a finding does not fit into one of the 6 opportunity types, it either maps to an existing type or it does not appear in the customer report at all.

---

### Structure

**Header** — Account name | Monthly Report | Period | Prepared date

---

**Monthly Summary** (3 sentences max)
Key numbers: total requests, bandwidth, cache hit rate. What the main story is this month (format, growth, gaps). Short prose only — no bullet points.

---

**How ImageKit Is Performing**

Scorecard — fixed 4-row table, same every report. Two columns: Image and Video. One row per capability.

| Capability        | Image          | Video          |
| ----------------- | -------------- | -------------- |
| Format conversion | ✅/⚠️ + signal | ✅/⚠️ + signal |
| Compression       | ✅/⚠️ + signal | ✅/⚠️ + signal |
| Resizing          | ✅/⚠️ + signal | ✅/⚠️ + signal |
| Cache hit rate    | ✅/⚠️ + %      | ✅/⚠️ Shared   |

**Signal rules per row:**

- **Format conversion:** % of image requests served in WebP or AVIF. ✅ if WebP/AVIF dominant. ⚠️ if JPEG/PNG dominant.
- **Compression:** mirrors format conversion — ✅ when format conversion ✅. Only ⚠️ if format conversion is failing.
- **Resizing (Image):** transform adoption rate = transformed requests / total requests %. ⚠️ if below 30%. State the % — do NOT name specific assets in the scorecard.
  - **Exception for URL rewriter accounts (Cloudinary/Akamai/Imgix):** the `transform.bandwidthWise` metric measures native `tr=` param usage only — it will read near-zero for these accounts because their transforms are embedded in the rewriter format, not `tr=` params. Do NOT quote this near-zero metric in the scorecard. Instead, write only what Phase 4 asset review confirmed: e.g. "⚠️ Resize gaps found in high-traffic images" or "✅ Top images confirmed resized". No raw %, no technical explanation of why the metric is misleading.
- **Resizing (Video):** width cap present on top video assets? ✅ if top videos have a width cap applied. ⚠️ if top videos by bandwidth have no width cap.
- **Cache hit rate (Image):** hit rate %. ✅ if ≥ 80%.
- **Cache hit rate (Video):** same hit rate applies to both image and video — use the same status as the Image column and label it `[✅/⚠️] Shared`.

Video column is always shown even for low video traffic — ⚠️ rows open the conversation.

**Scorecard = signal only. Causes and specific assets go in Opportunities below.**

This table has **exactly 4 rows**. Do not add rows. Do not rename rows. If a capability has no data, still include the row — mark it `—`.

---

**Highlights**

Exactly 3 bullets. Exactly this order. Exactly these topics. The section heading is "Highlights" — do not rename it, do not replace it with "What's Working" or any other heading.

Write it using this template — fill in the bracketed values:

```
## Highlights

- **[X]% of image traffic delivered as WebP or AVIF** — [one sentence on what this means for the account]
- **Average image size: [X] KB** — [one sentence on whether this is in a good range]
- **[X] million requests served from CDN without touching origin** — [one sentence on cache hit rate]
```

Calculations:
- Bullet 1: `(image/webp requests + image/avif requests) ÷ total image requests` — sum both format entries from `formatWise`, divide by `request.total` image count. Use WebP alone only if AVIF = 0, in which case the sum still equals WebP. Never use WebP alone when AVIF > 0 — both must be combined.
- Bullet 2: total image bandwidth ÷ total image requests — images only, exclude video, JS, CSS, fonts
- Bullet 3: cache hit rate × (Hit + Miss count from resultType)

---

**Images — Opportunities to Improve**

Up to 4 opportunities, prioritised by impact.

The 6 types in the taxonomy below are the **complete and exhaustive list** — these are the only headings that may appear in this section. If a finding does not match one of the 6 types exactly, map it to the closest one or drop it. Never create a new heading type.

Common findings and where they map:
- URL encoding bugs / double-encoding 404s → type 2 (CMS or URL issue)
- SVG bandwidth anomaly → type 3 (high-traffic images without resize)
- S3 / origin errors → do not include in the customer report at all — internal analysis file only
- VPU cost / video processing → not in the fixed taxonomy — internal only, do not surface in customer report
- AVIF not enabled → not an Opportunity — if AVIF is 0%, mention it briefly in Monthly Summary only ("AVIF is not yet enabled — enabling it would be the next step after WebP"). Do not create an Opportunity entry for it.

Each opportunity block format:

- **Bold heading** with the key observed number in brackets — e.g. **Native app traffic may not be receiving optimised formats (X% of requests)**
- Bullet: what's happening + the number. Use speculative language if not confirmed from logs — "could mean", "may be", "we'd recommend confirming"
- Bullet: **Fix:** one clear action per client type if needed
- Bullet: _Confirm first:_ what to validate before acting (optional — only include if needed)

No "Why it matters" section. No saving estimates.

**Fixed opportunity taxonomy for images (only flag if detection condition is met):**

1. **Native app traffic may not be receiving optimised formats**
   - Detection: Native app UA detected (Dart/Flutter, OkHttp, CFNetwork)
   - Use speculative language throughout
   - Flutter: `f-webp` only. Do NOT mention `f-avif`. Reference `agent/docs/native-mobile-format-support.md`.
   - iOS native: `f-webp` separately
   - Do not flag if there is evidence the customer already sets `f-webp` in app URLs

2. **CMS or URL issue causing transforms to be ignored**
   - Detection: A URL pattern in top assets has malformed params (chained `?`, missing `tr=`, split params) causing high bandwidth at source resolution
   - Name the product area, not the raw URL — e.g. "expert review photos"
   - Sits under Resizing, not Compression

3. **High-traffic images served without resize transforms**
   - Detection: Top assets by bandwidth have no resize transform AND mobile traffic is significant (>50% of browser traffic). Exclusions apply — skip images where the path encodes a size or BW/view < 40KB
   - Use speculative language for mobile share if inferred
   - Fix: `c-at_max,w-[N]`

4. **Animated GIF not optimised**
   - Detection: A GIF appears in top assets by bandwidth with significant volume
   - Fix: Append `/ik-gif-video.mp4` to the URL to serve it as an optimised video. The `<img>` tag must be replaced with a `<video>` tag — no changes to the original GIF file itself. If converting to a video element is not feasible, `f-auto` will serve animated WebP to supporting browsers instead.

---

**Video — Opportunities to Improve**

Same block format as images. Always include even if video traffic is low — gives an opening to discuss video.

Fixed opportunity taxonomy for video:

5. **Video served in MP4 only — WebM not enabled**
   - Detection: Video format data shows MP4 only (no WebM in formatWise), significant video bandwidth
   - Fix: Enable account-level auto format conversion in ImageKit settings — no URL param needed for browser clients. If Phase 3 confirmed native app traffic, explicit format params are also needed: `f-webm` for Android, `f-mp4` for iOS.
   - **Use this heading verbatim: "Video served in MP4 only — WebM not enabled".** Do not paraphrase. Common wrong variants that are NOT compliant: "WebM not being delivered", "WebM not available", "WebM not active".

6. **Top videos served without a width cap**
   - Detection: Top video assets by bandwidth have no width transform applied AND bandwidth/view ≥ 500KB
   - Fix: Add `c-at_max,w-[N]`

---

**Questions for the Call**

**Maximum 3 questions.** One sentence each — no preamble. Cover only things where you cannot proceed without the customer's answer. If you have drafted more than 3, keep the ones that need customer input to act — cut the rest, they can come up organically on the call.

---

### Pre-Save Checklist — Output 2

Before writing the customer report file, run these 6 checks in order. Fix any failure before saving.

**1. Saving estimates** — search the drafted report for any of these: `×`, `% reduction`, `% smaller`, `GB saving`, `MB saving`, `saves approximately`, `would reduce`, `could save`. For every match, rewrite the sentence to describe what to change and why — remove the number entirely.

**2. Taxonomy** — list every opportunity heading in the Opportunities sections. Each one must match one of these 6 exactly:
- Native app traffic may not be receiving optimised formats
- CMS or URL issue causing transforms to be ignored
- High-traffic images served without resize transforms
- Animated GIF not optimised
- Video served in MP4 only — WebM not enabled
- Top videos served without a width cap

If any heading does not match, rename it to the closest type or remove the opportunity.

**The heading must be the exact label text — no parentheticals, no account-specific additions, no extra words.** Account context goes in the body, not the heading.
- ❌ "High-traffic images served without resize transforms (restaurant photos account for 280 GB)"
- ✅ "High-traffic images served without resize transforms"

**3. Raw filenames and paths** — search for any string that looks like a filename or file path: contains `/`, or contains a dot followed by a file extension (`.jpg`, `.jpeg`, `.png`, `.gif`, `.mp4`, `.svg`, `.webp`, `.webm`, `.pdf`, `.bmp`, `.lottie`, `.mov`, `.webp`, `.avif`, or any other file format suffix). Replace each occurrence with a plain description of what the asset is and where it appears in the product.
- ❌ `consumer-react/assets/HomePage/Gif_loader.gif`
- ✅ "the homepage loading animation"
- ❌ `cms/product_variant/65a14739.bmp`
- ✅ "the product variant image"

**Also check for `/ik-gif-video.mp4`** — this is an ImageKit product endpoint, not a customer filename, but it still contains `/` and `.mp4` and will fail the check. Replace it with "ImageKit's built-in GIF-to-video conversion". Example: instead of "Append `/ik-gif-video.mp4` to the GIF URL", write "Use ImageKit's built-in GIF-to-video conversion".

**4. Highlights** — quote the Highlights section back. Verify: heading says "Highlights", exactly 3 bullets, bullet 1 is WebP/AVIF %, bullet 2 is average image size, bullet 3 is CDN requests. If any of these are wrong, rewrite the section using the template above.

**5. Scorecard** — count the rows in the "How ImageKit Is Performing" table. Must be exactly 4. If there are more, remove the extra rows.

**6. Questions** — count the questions under "Questions for the Call". Must be 3 or fewer. If more, remove the weakest ones.

Only write the file after all 6 checks pass.

---

---

## RULES

- Files are written phase by phase in real time — never batch all writes at the end of the run. If you find yourself about to write multiple phases at once, stop and write them one at a time.
- All findings must come from the JSON data — no assumptions without stating the basis
- Flag everything inferred with ⚠️ — confirm with the customer on the call
- WebP ≠ AVIF — never treat them as the same setting
- WebM detection is via `User-Agent` header for video — different from images which use `Accept` header
- Resize findings: do not state that specific users received oversized assets — use speculative language
- Customer report: no technical jargon, no raw URLs, no JSON field names
- Customer report: name findings by product area not by URL
- Customer report: do not pad — only include real findings
- Bandwidth saving estimates: WebP→AVIF 20–30%, MP4→WebM 20–30%, no resize→resize 40–60%, GIF→WebP 30–50%, native app f-webp 20–35%. Always flag as ⚠️. **Saving estimates go in OUTPUT 1 (technical analysis) only — never in OUTPUT 2.** In the customer report, describe what to change and why — never state how much it will save.
- Inline recommendations: every flagged finding must have a **Recommendation:** line immediately after it
- VPU is video-only — never reference in image findings
- `tr=orig` on images = intentional original file request, do not flag. On videos = first-request intermediate response — note as a pre-warming opportunity, never as an error.
- Named transforms (`n-`): note positively, skip param checks — underlying params not visible in analytics

---

## FINAL RESPONSE — Output Delivery

After all phases and both outputs are complete:

1. **Present the customer report inline in your response, copyable** — output the full customer report inside a fenced ```markdown block so the raw markdown can be copied directly.
2. **All 3 files are already saved** — written to `data/output/[account]/` during the run. Do not ask where to save.
