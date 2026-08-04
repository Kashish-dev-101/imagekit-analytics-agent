---
name: origin-vendor
description: Resolve a domain to its IP, look up ASN/org info, and identify the hosting/infrastructure vendor — usage: /origin-vendor <domain>
when_to_use: You have a domain and want to know what hosting or CDN infrastructure is behind it — useful for understanding a customer's origin setup.
---

No plan step — this is a quick lookup.

**Step 1 — Resolve the domain**

Run `dig <domain> +short` to get the IP address.

If the result contains a CNAME chain, note the final A record IP.

**Step 2 — Look up IP info**

Run `curl -s https://ipinfo.io/<ip>/json` to get org, ASN, hostname, city, and country.

**Step 3 — Identify the vendor**

Match the `org` field (ASN + name) against known vendors:

| Signal | Vendor |
|--------|--------|
| `AS13335 Cloudflare` | Cloudflare (CDN / proxy — origin may be hidden) |
| `AS16509 Amazon` / `AS14618 Amazon` | AWS (EC2, CloudFront, etc.) |
| `AS15169 Google` | Google Cloud / GCP |
| `AS8075 Microsoft` | Azure |
| `AS20940 Akamai` | Akamai CDN |
| `AS54113 Fastly` | Fastly CDN |
| `AS60068 CDN77` | CDN77 |
| `AS60626 DigitalOcean` | DigitalOcean |
| `AS14061 DigitalOcean` | DigitalOcean |
| `AS16276 OVH` | OVH Hosting |
| `AS24940 Hetzner` | Hetzner |
| `AS55293 A2 Hosting` | A2 Hosting (shared/managed hosting) |
| `AS46606 Unified Layer` / `AS46816 Bluehost` | Bluehost / Unified Layer |
| `AS26496 GoDaddy` | GoDaddy Hosting |
| `AS29854 DreamHost` | DreamHost |
| `AS7922` / `AS33650` Comcast | Comcast (likely self-hosted / small biz) |
| `AS701` / `AS702` Verizon | Verizon (likely self-hosted) |

If the org doesn't match a known vendor, report the raw ASN and org name — that's still useful.

**Note on Cloudflare:** If Cloudflare is detected, the real origin IP is hidden. Mention this and note that the real origin infrastructure cannot be determined from DNS alone.

**Step 4 — Report**

| Field | Value |
|-------|-------|
| Domain | |
| Resolved IP | |
| Hostname (reverse DNS) | |
| ASN + Org | |
| Vendor | |
| Location | |

Then one sentence on what this means — e.g. shared hosting, managed WAF, bare cloud VM, Cloudflare proxy hiding origin, etc.
