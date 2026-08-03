---
description: Interactively test ImageKit features on any image URL — compression, format, resize, transformations
---

Ask the user for a base image URL if not provided in $ARGUMENTS.

**Important — ImageKit defaults:**
In ImageKit, automatic compression and automatic format conversion happen with zero parameters. You do NOT need `f-auto` or `q-auto` — they are on by default. Tests should verify this behaviour is working, not configure it.

Reference docs (fetch these when relevant to the check being run):
- Automatic compression: https://imagekit.io/docs/image-optimization#automatic-image-compression
- Automatic format conversion: https://imagekit.io/docs/image-optimization#automatic-format-conversion
- Full optimisation overview: https://imagekit.io/docs/image-optimization

---

Run the following checks in order. After each one, print the result and ask: "Continue to the next check? (or type a custom transformation to test)"

**Check 1 — Baseline**
Fetch the original image with no transformations:
```bash
curl -o /dev/null -s -w "Status: %{http_code}\nContent-Type: %{content_type}\nSize: %{size_download} bytes\nTime: %{time_total}s\n" "<url>"
```
Report: format, size in KB, response time. This is the baseline to compare everything against.

**Check 2 — Automatic format conversion**
Fetch the same URL with an `Accept: image/webp` header to confirm ImageKit serves WebP automatically:
```bash
curl -o /dev/null -s -H "Accept: image/webp,image/avif" -w "Status: %{http_code}\nContent-Type: %{content_type}\nSize: %{size_download} bytes\nVary: %{header[vary]}\n" "<url>"
```
Also fetch the response headers to check for `Vary: Accept` — this confirms content negotiation is active.
Read https://imagekit.io/docs/image-optimization#automatic-format-conversion if the content-type is unexpected.

**Check 3 — Automatic compression**
Compare original size vs IK-served size from Check 1. IK applies compression automatically — the served file should be smaller than the original.
Read https://imagekit.io/docs/image-optimization#automatic-image-compression to explain the result.

**Check 4 — Explicit resize**
Test `w-300` and confirm the image is actually resized. Append transformation parameters using `?tr=` if the URL has no query string, or `&tr=` if it already has one:
```bash
curl -o /dev/null -s -w "Status: %{http_code}\nContent-Type: %{content_type}\nSize: %{size_download} bytes\n" "<url_with_tr>"
```
Report size difference vs baseline. A smaller file confirms resize is working.

**Check 5 — Format override**
Test explicit format — force `f-webp` and `f-avif` separately, compare sizes:
```bash
curl -o /dev/null -s -w "Content-Type: %{content_type}\nSize: %{size_download} bytes\n" "<url_with_tr_f-webp>"
curl -o /dev/null -s -w "Content-Type: %{content_type}\nSize: %{size_download} bytes\n" "<url_with_tr_f-avif>"
```

**Check 6 — Custom transformation**
Ask the user: "Any specific transformation to test? (e.g. `w-600,h-400,c-maintain_ratio` or `e-sharpen`)"
Run their input and report the result.

**Check 7 — Server timing (cache-busted)**
Bust the cache by appending a unique `&cb=<timestamp>` parameter to force a fresh request from origin. This bypasses CDN cache and shows real processing times.

```bash
curl -sI "<url>&cb=$(date +%s)" | grep -i "server-timing\|x-cache\|age"
```

Extract from the `Server-Timing` header:
- `download` — ms IK took to fetch the original from your origin
- `transformation` — ms IK took to apply transformations

Report:
- **Origin fetch time** (download) — high value = slow origin or large original
- **Transformation time** — high value = heavy transformation (large resize, format conversion)
- **x-cache** — should be MISS on first request (cache was busted), HIT on repeat

This tells you where time is being spent — origin latency vs processing vs CDN. Reference: https://imagekit.io/docs/integration/connect-external-storage#debugging-slow-origin-response

---

**Final summary table:**

| Check | Params | Format | Size (KB) | Notes |
|-------|--------|--------|-----------|-------|
| Baseline | none | | | |
| Auto format | Accept: webp | | | Vary: Accept? |
| Resize | w-300 | | | |
| Force webp | f-webp | | | |
| Force avif | f-avif | | | |
| Custom | (user input) | | | |
| Server timing | cb=bust | — | — | download ms / transform ms |
