---
name: ik-debug
description: Debug an ImageKit URL by fetching it with ik-debug=true — captures HTTP status, TTFB, transformation time, download time, ik-error, and CloudFront PoP across multiple runs. Use when a specific URL from an analytics report is slow, returning errors, or behaving unexpectedly.
when_to_use: A specific ImageKit URL needs investigation — 404, slow response, intermittent errors, or unexpected content-type.
---

You are troubleshooting an ImageKit URL by fetching it with debug query parameters to get extra logs in ImageKit Grafana.

The user will pass a URL (and optionally a number of runs) as: `$ARGUMENTS`

Parse the input:
- First token is the URL
- Second token (optional) is the number of runs (default: 3)

Steps:
1. Append these query params to the URL (preserve any existing params):
   - `ik-debug=true`
   - `refetch=true`
   - `ik-version=<n>` — increment n for each run to bypass cache

2. For each run, curl the URL and capture:
   - HTTP status code
   - `x-request-id`
   - `ik-error` (if present)
   - `content-type`
   - `cache-control`
   - `server-timing` — extract `download` and `transformation` ms
   - `x-ik-skey` (IK node identifier)
   - `x-amz-cf-pop` (CloudFront PoP / region)
   - TTFB and total time

3. Present results in a clear table: run number, status, request ID, ik-error or "OK", TTFB, download ms, transformation ms. Flag download time with ⚠️ if > 600ms.

4. After all runs, summarise:
   - Is the issue consistent or intermittent?
   - If 404: `ik-error` value — file missing at origin vs other error
   - If 200: confirm cache-control and size
   - Call out anything unusual (redirects, slow TTFB >1s, varying status codes)
   - If any download > 600ms: flag as slow origin fetch — note the `x-ik-skey` and `x-amz-cf-pop` for infra escalation

Use this bash pattern for each run:
```bash
curl -s -o /dev/null -w "%{http_code} TTFB:%{time_starttransfer}s Total:%{time_total}s Size:%{size_download}b" \
  -D - "<URL>?ik-debug=true&refetch=true&ik-version=<n>" 2>/dev/null | \
  grep -E "^HTTP|x-request-id|ik-error|content-type|cache-control"
```
