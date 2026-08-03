---
name: url-check
description: Check what a URL is serving and what's behind it — delivery vendor, format, cache status, vary headers, and origin hosting. Useful for quickly verifying a specific URL from an analytics report or customer conversation.
when_to_use: You have a specific URL (from an analytics report, a customer message, or a recommendation you want to verify) and want to confirm vendor routing, format delivery, cache behaviour, and origin infrastructure.
---

# /url-check — URL delivery and origin check

## 1. Resolve input

Accept a URL from `$ARGUMENTS`. If not provided, ask: *"Which URL do you want to check?"*

---

## 2. Check delivery headers

```bash
curl -sI --max-time 10 "<url>"
```

Extract and classify:

**Delivery vendor** — match against these signatures in order (first match wins):

| Signal | Vendor |
|---|---|
| `x-server: ImageKit.io` | ImageKit — confirmed. Authoritative regardless of custom domain |
| `x-imgix-id` or `x-imgix-cache` header | Imgix |
| `cf-polished` header | Cloudflare Images / Polish — optimization active |
| `cf-ray` header (no `cf-polished`) | Cloudflare CDN only — no image optimization |
| `fastly-io-info` or `fastly-io-transform-stats` | Fastly Image Optimizer — transforms active |
| `x-served-by` with no `fastly-io-*` headers | Fastly CDN only |
| `x-akamai-*` headers | Akamai |
| `x-amz-cf-id` or `x-amz-cf-pop` | AWS CloudFront CDN only |
| `x-bunny-cache` | Bunny CDN |
| URL path contains `/image/upload/` or domain contains `cloudinary.com` | Cloudinary |
| No CDN headers | Raw origin — no CDN detected |

Also extract:
- **Format** — `content-type` header (e.g. `image/webp`, `video/mp4`)
- **Cache** — `x-cache` (HIT/MISS); or `age` header (> 0 = cached)
- **Content negotiation** — `vary: Accept` present = auto image format active; `vary: User-Agent` present = auto video format active
- **HTTP status** — 200, 404, 301/302, etc.

---

## 3. Check origin hosting

Extract the domain from the URL. Run:

```bash
dig +noall +answer <domain>
```

Take the first A record IP. Then:

```bash
curl -s --max-time 5 https://ipinfo.io/<ip>/json
```

Extract `org`, `country`, `city`, `hostname`. Match `org` to hosting vendor:

| Signal | Vendor |
|---|---|
| `AS13335 Cloudflare` | Cloudflare — origin IP hidden behind proxy |
| `AS16509 Amazon` / `AS14618 Amazon` | AWS (EC2, CloudFront, S3) |
| `AS15169 Google` | Google Cloud / GCP |
| `AS8075 Microsoft` | Azure |
| `AS20940 Akamai` | Akamai CDN |
| `AS54113 Fastly` | Fastly CDN |
| `AS60626 DigitalOcean` / `AS14061 DigitalOcean` | DigitalOcean |
| `AS16276 OVH` | OVH Hosting |
| `AS24940 Hetzner` | Hetzner |

If the org doesn't match, report the raw ASN and org name.

---

## 4. Output

```
## URL Check — <url>

### Delivery
| Field | Value |
|---|---|
| HTTP status | |
| Vendor | |
| Format served | |
| Cache | HIT / MISS / unknown |
| Vary: Accept | present / absent |
| Vary: User-Agent | present / absent |

### Origin
| Field | Value |
|---|---|
| Domain | |
| Resolved IP | |
| Hostname | |
| ASN + Org | |
| Hosting vendor | |
| Location | |
```

Add interpretation notes only when relevant:
- `x-server: ImageKit.io` absent → traffic is not going through ImageKit. Confirm with customer whether this URL is on their IK account.
- `vary: Accept` absent on an IK URL → account-level auto format may be off, or format is hardcoded in the URL transform string.
- Cloudflare detected at origin → real origin IP is hidden; infrastructure behind Cloudflare cannot be determined from DNS alone.
- Another CDN at the origin layer → double-CDN setup (e.g. Cloudflare in front of ImageKit) — can cause cache fragmentation.
- HTTP 404 → asset missing at origin, or URL endpoint function not deployed.

No file saved — this is a one-off check. For debugging latency or errors on an IK URL, use `/ik-debug`.
