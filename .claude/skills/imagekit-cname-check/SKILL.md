---
name: imagekit-cname-check
description: Check whether one or more custom domains are pointed to ImageKit by resolving their DNS CNAME. ImageKit's CNAME target is *.imgkit.net. Use when verifying if a customer has CNAME'd their media/vanity domain to ImageKit, or to spot when multiple domains share one ImageKit endpoint.
when_to_use: User gives a domain (or several) and wants to know if it points to ImageKit / what ImageKit endpoint it uses.
---

# ImageKit CNAME Check

Resolve the DNS of one or more domains and determine whether they point to ImageKit.

## How it works

ImageKit serves custom (vanity) domains via a CNAME to **`<endpoint-id>.imgkit.net`**. So if a domain's CNAME chain ends in `.imgkit.net`, it's delivering through ImageKit, and the label before `.imgkit.net` is the **endpoint id** (which identifies the ImageKit account/URL-endpoint).

## Steps

1. Take one or more domains from the user's message (e.g. `media.brand-a.com`, `media.brand-b.com`).
2. For each domain, resolve the DNS answer/CNAME chain:
   ```bash
   dig +noall +answer <domain>
   ```
   (If `dig` is unavailable, fall back to `host <domain>` or `nslookup <domain>`.)
3. Inspect the answer:
   - If a `CNAME` target ends in **`.imgkit.net`** → the domain **is pointed to ImageKit**. Extract the endpoint id = the subdomain label before `.imgkit.net`.
   - If it resolves to something else (another CDN, an A record, etc.) → **not** ImageKit; note what it points to instead.
   - If it doesn't resolve → say so.

## Output

A table:

| Domain | CNAME target | ImageKit? | Endpoint id |
|--------|--------------|-----------|-------------|

Then call out anything notable:
- **Shared endpoint:** if two or more domains resolve to the *same* `<endpoint-id>.imgkit.net`, flag it — they're served from the same ImageKit account/URL-endpoint (common for multi-brand customers).
- **Not on ImageKit:** if a domain points elsewhere, name the target (e.g. Cloudflare, CloudFront, another CDN).

## Example

`media.brand-a.com` and `media.brand-b.com` both → `abc123xyz.imgkit.net` → both on ImageKit, same endpoint `abc123xyz` (one account fronting two brand domains).
