# Analytics Agent — Main Prompt

> Paste this into Claude Code with the customer's analytics JSON file in context.
> Before running, read `guardrails.md` and `schema.md` for technical rules and field guidance.

---

## Prompt

```
I have an ImageKit analytics JSON export for [CUSTOMER NAME]. The file covers [DATE RANGE].

Please analyse it and produce two outputs:

---

### OUTPUT 1: Full Technical Analysis

1. **Account summary**
   Who is this customer? Infer their industry, product type, and how they use ImageKit from folder names, asset naming conventions, URL patterns, and user agent distribution. Flag anything inferred vs confirmed.

2. **Traffic summary**
   Total requests, bandwidth, storage, daily trends, peak/low days, and breakdown by URL pattern/folder.

3. **Format delivery**
   What formats are being served (image and video)? Is WebP enabled? Is AVIF enabled? Are videos serving WebM? Identify any format delivery gaps and quantify the potential bandwidth saving.

4. **UA & device breakdown**
   Who is requesting assets? Break down by browser, device type (mobile/desktop/tablet), native app clients (OkHttp, URLSession etc.), bots/crawlers, and AI agents. Calculate mobile % of requests and bandwidth separately.

5. **Geography**
   Top countries by request count and bandwidth. Flag anomalies (e.g. country with disproportionately high bandwidth vs request count).

6. **Top assets**
   Highest bandwidth images and videos. What transforms are applied? Are there assets being served at full resolution without resize? Flag anything consuming outsized bandwidth.

7. **Transformation usage**
   What transforms appear in the top URLs? Are resize, format, and quality params being used correctly? Are there signs of transformation sprawl (many unique variants of the same asset)?

8. **Cache & error patterns**
   Status code breakdown — 200/206/304/404 rates. Notable error patterns.

9. **Optimization opportunities**
   For each opportunity: state what the data shows, estimate the potential impact, reference the relevant ImageKit doc. Flag anything uncertain with ⚠️.

---

### OUTPUT 2: Customer Talking Points

A short, non-technical summary for use in a customer call or account review. Structure:

- **What's working well** (2–3 things with numbers)
- **Three opportunities** (each with a clear ask and estimated impact)
- **One question to ask the customer**

Keep it conversational. No jargon. Numbers only where they add weight.

---

Follow all rules in guardrails.md. Use schema.md to know which JSON fields to read and what they reveal.
```
