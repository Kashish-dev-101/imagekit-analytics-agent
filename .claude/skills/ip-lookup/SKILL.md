---
name: ip-lookup
description: Look up one or more IP addresses via ipinfo.io and classify each one — CDN layer, cloud backend, residential ISP, VPN/proxy, or known bot infrastructure. Useful for investigating IPs flagged in analytics or raised by a customer.
when_to_use: When you have one or more IPs to investigate — from a customer query, from Phase 6 of an analytics run, or from any other source.
---

# /ip-lookup — IP investigation and classification

## 1. Resolve inputs

Accept IPs from:
- The user's message directly (e.g. `/ip-lookup 1.2.3.4 5.6.7.8`)
- A list pasted inline
- A reference to flagged IPs in an existing analytics output

If no IPs are provided, ask: *"Which IPs do you want to look up?"*

**If more than 10 IPs are passed:** warn before proceeding — *"You've passed [N] IPs. Running all of them will make [N] ipinfo.io requests — this may be slow. Proceeding with all [N]."* Then continue.

## 2. Look up each IP

For each IP, run:

```bash
curl -s --max-time 5 https://ipinfo.io/[IP_ADDRESS]
```

Extract these fields from the response:
- `org` — organisation / ASN (e.g. "AS13335 Cloudflare, Inc.")
- `country` — two-letter country code
- `city` — city
- `hostname` — reverse DNS hostname if present

If the curl times out or returns an error, note it as "Lookup failed" for that IP and continue with the rest.

## 3. Classify each IP

Apply this classification in order — use the first rule that matches:

| Classification | Signal |
|---|---|
| **CDN layer** | org contains: Cloudflare, Fastly, Akamai, Amazon CloudFront, Edgecast, Limelight, Verizon Digital Media |
| **Cloud provider** | org contains: Amazon, AWS, Google, GCP, Microsoft, Azure, DigitalOcean, Linode, Vultr, Hetzner, OVH |
| **Known bot / AI crawler** | org contains: Googlebot, Google LLC (ASN 15169 with bot hostname pattern), OpenAI, Anthropic, Meta, Apple |
| **Residential ISP** | org is a telecom or ISP name with no hosting/cloud markers (e.g. Jio, Airtel, Comcast, BT, Vodafone, AT&T) |
| **VPN / proxy / hosting** | org is an offshore or anonymous hosting provider with no known product (e.g. M247, Serverius, Sharktech, Frantech) |
| **Unknown** | org is missing, empty, or does not match any of the above |

**What each classification means in an ImageKit context:**

- **CDN layer** — another CDN is sitting in front of ImageKit. Traffic is proxied, not direct from end users. Confirm with customer whether this architecture is intentional — double-CDN setups can cause cache fragmentation.
- **Cloud provider** — could be the customer's own app backend, a CDN product (CloudFront, Cloud CDN), or a scraper running on cloud infrastructure. High avg asset size suggests downloading originals; low avg size suggests normal app backend behaviour.
- **Known bot / AI crawler** — automated indexing or AI training traffic. Not a risk, but inflates usage metrics. Customer may want to block or rate-limit if volume is significant.
- **Residential ISP** — end-user traffic, normal. High concentration from a single residential IP is unusual — could be a heavy power user, a tethered device, or a scraper disguising as residential.
- **VPN / proxy / hosting** — elevated scraper risk, especially if avg bandwidth/request is high (pulling large originals). Flag for customer attention.
- **Unknown** — cannot determine with available data. Report the raw org and hostname and let the customer investigate.

## 4. Output

One table per lookup run. No flags, no ✅/⚠️ — state only.

```
## IP Lookup Results

| IP | Org | Country | City | Hostname | Classification | Notes |
|---|---|---|---|---|---|---|
| 1.2.3.4 | AS13335 Cloudflare | US | San Jose | - | CDN layer | Another CDN in front of ImageKit |
| 5.6.7.8 | AS16509 Amazon | IE | Dublin | ec2-5-6-7-8.eu-west-1.compute.amazonaws.com | Cloud provider | AWS EC2 — app backend or CloudFront |
```

**Notes column:** one short phrase — what this likely means for the account. Factual only, no external inference.

If a lookup failed: fill all fields with "—" and Notes as "Lookup timed out — check manually."

## 5. Deliver

Present the table inline. No file is saved — this is a one-off lookup, not a persisted output.

If any IP was classified as **VPN / proxy / hosting** or **Unknown** with high request volume: add a note after the table — *"[IP] could not be classified from org data alone. Share the raw org ([org value]) with the customer to confirm whether it's their infrastructure."*
