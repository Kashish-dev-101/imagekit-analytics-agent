---

name: custom-domain-request
description: Check a customer's custom domain DNS and prepare the right message — internal request to activate it if DNS is already correct, or a customer-facing message if DNS isn't set up yet or is hidden behind a Cloudflare proxy. Usage — /custom-domain-request <domain> <clientNumber> [imagekitID]
when_to_use: Setting up a custom (vanity) domain for a customer's ImageKit account — before asking internally to get it activated, or before asking the customer to fix their DNS.

---

# /custom-domain-request — Custom Domain Setup Check

Checks whether a customer's custom domain is correctly pointed to ImageKit, then produces exactly one of three outcomes: an internal activation request, or a customer-facing message asking them to fix DNS or their Cloudflare proxy setting.

## Parse `$ARGUMENTS`

Expected: `<domain> <clientNumber> [imagekitID]`

- **domain** — the customer's custom domain (e.g. `media.example.com`)
- **clientNumber** — the ImageKit account identifier, used to build the admin panel link
- **imagekitID** — optional. The `<id>` in `<id>.imgkit.net` that the domain should point to. Only needed as a fallback when DNS doesn't already show it. If DNS isn't correct and this wasn't provided, ask for it before drafting the customer message.

If `domain` or `clientNumber` is missing, ask before proceeding.

---

## Step 1 — Check DNS via the Dig Web Interface

Build the link by substituting the domain in:

```
https://www.digwebinterface.com/?hostnames={domain}&type=&ns=resolver&useresolver=9.9.9.10&nameservers=
```

Fetch that link and read the result to classify the state (Step 2) — don't skip actually checking the output. But when producing the message, share this link rather than pasting the raw dig output — it's easier for whoever's reading to open and verify themselves.

---

## Step 2 — Classify into exactly one state

**State A — Already correct**
The CNAME resolves to some `<id>.imgkit.net`. Note the id as supporting detail — the point of the check is confirming DNS is right, not "extracting" the id as if that were the goal.

**State B — Not pointed yet**
The domain resolves to something else entirely (another CDN, an A record unrelated to ImageKit), or doesn't resolve (NXDOMAIN).

**State C — Cloudflare-proxied, can't verify**
No CNAME is visible; instead A/AAAA records are returned. Confirm this is Cloudflare proxying (not just any A record) with:

```bash
curl -sI "https://{domain}" | grep -iE "^server|^cf-ray"
```

`server: cloudflare` or a `cf-ray` header confirms it. (Optionally cross-check the resolved IP against Cloudflare's published ranges at `https://www.cloudflare.com/ips-v4` / `ips-v6` for extra certainty.) When a record is "Proxied" (orange cloud) in Cloudflare, public DNS lookups return Cloudflare's anycast IPs instead of the real CNAME target — see https://developers.cloudflare.com/dns/proxy-status/ — so the actual ImageKit target can't be confirmed externally until it's checked in the Cloudflare dashboard or the proxy is temporarily disabled.

---

## Step 3 — Produce the message for that state only

**Only State A produces an internal message.** States B and C produce a customer-facing message — there's nothing for the internal team to act on until DNS actually resolves to ImageKit.

### State A — Internal (send to the team that activates custom domains)

```
Need this custom domain added to a customer account.

Client ID: {clientNumber}
Admin panel: https://imagekit.io/admin-panel/?clientNumber={clientNumber}

Domain: {domain}

DNS check: https://www.digwebinterface.com/?hostnames={domain}&type=&ns=resolver&useresolver=9.9.9.10&nameservers=
```

### State B — Customer-facing (DNS not set up)

```
Hi {customer},

For {domain} to work with ImageKit, it needs a CNAME record pointing to {imagekitID}.imgkit.net.

Right now it resolves to: {what dig actually found, or "nothing — it's not resolving"}.

Could you update the DNS record and let us know once it's done? We'll verify from our side and proceed with activating it.
```

### State C — Customer-facing (Cloudflare proxy blocking verification)

```
Hi {customer},

We can see {domain} is set up in Cloudflare, but the record appears to be "Proxied" (orange cloud), which hides the actual destination from us — we can only see Cloudflare's own IPs, not what it's ultimately pointing to. Details on how this works: https://developers.cloudflare.com/dns/proxy-status/

Could you either:
1. Confirm in your Cloudflare dashboard that the CNAME target is {imagekitID}.imgkit.net, or
2. Temporarily switch the record to "DNS only" (grey cloud) so we can verify it externally?

Once confirmed, we'll proceed with activating the custom domain on our side.
```

---

## Notes

- Never guess `imagekitID` — it varies per account. Only use a value the user supplied or one found directly in a correct DNS answer.
- If `imagekitID` is required (State B or C) and wasn't given as an argument, ask for it before drafting the message rather than leaving a placeholder in customer-facing text.
- Don't send the internal message unless State A is confirmed — sending an activation request before DNS is actually correct just creates back-and-forth for the internal team.
