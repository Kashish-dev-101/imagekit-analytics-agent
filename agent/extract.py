#!/usr/bin/env python3
"""
ImageKit Analytics JSON Extractor
Purpose: flatten JSON structure only — no calculations, no conversions, no truncations.
All values preserved exactly as in the source JSON.

Usage:
    python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt

See agent/docs/extractor-reference.md for full details on what is kept and why.
"""

import json
import sys

try:
    from device_detector import DeviceDetector as DD
    _DD_AVAILABLE = True
except ImportError:
    _DD_AVAILABLE = False

# IK-specific patterns DeviceDetector doesn't cover — ordered, first match wins
_IK_PATTERNS = [
    ("okhttp/",                "Native App · Android (OkHttp)"),
    ("Dart/",                  "Native App · Flutter (Dart)"),
    ("CFNetwork/",             "Native App · iOS (URLSession)"),
    ("Darwin/",                "Native App · iOS (URLSession)"),
    ("com.apple.WebKit",       "In-App Browser · iOS WKWebView"),
    ("FBAN/",                  "In-App Browser · Facebook"),
    ("FBAV/",                  "In-App Browser · Facebook"),
    ("FB_IAB",                 "In-App Browser · Facebook"),
    ("Instagram",              "In-App Browser · Instagram"),
    ("MicroMessenger",         "In-App Browser · WeChat"),
    ("Twitter",                "In-App Browser · Twitter/X"),
    ("Claude-User",            "Bot · Anthropic AI Agent"),
    ("anthropic-ai",           "Bot · Anthropic AI Agent"),
    ("GPTBot",                 "Bot · OpenAI Crawler"),
    ("ChatGPT-User",           "Bot · OpenAI Crawler"),
    ("OAI-SearchBot",          "Bot · OpenAI Crawler"),
    ("OpenAI-File-Downloader", "Bot · OpenAI File Processor"),
    ("ai-sdk/",                "Bot · Vercel AI SDK"),
    ("python-httpx",           "Server-side · Python (httpx)"),
    ("python-requests",        "Server-side · Python (requests)"),
    ("Go-http-client",         "Server-side · Go HTTP Client"),
    ("axios/",                 "Server-side · JavaScript (axios)"),
    ("undici",                 "Server-side · Node.js (undici)"),
    ("node-fetch",             "Server-side · Node.js (node-fetch)"),
    ("curl/",                  "Server-side · curl"),
]

_TYPE_MAP = {
    "desktop":     "Desktop",
    "smartphone":  "Mobile",
    "tablet":      "Tablet",
    "tv":          "TV",
    "console":     "Console",
    "car browser": "Car Browser",
}


def _val(v):
    return str(v).strip() not in ("", "Unknown", "UNK", "0", "None", "none")


def classify_ua(ua):
    """Return a human-readable label for a User-Agent string using a 3-layer fallback."""
    if not ua or ua.strip() in ("", "-"):
        return "Unknown"

    # Layer 1 — DeviceDetector
    if _DD_AVAILABLE:
        try:
            data = DD(ua).parse()
            if data.is_bot():
                name = data.bot.name() if data.bot else "Bot"
                return f"Bot · {name}"
            client = (data.client_name() or "").strip()
            c_ver  = str(data.client_version() or "").split(".")[0].strip()
            os_n   = (data.os_name() or "").strip()
            os_v   = str(data.os_version() or "").split(".")[0].strip()
            d_type = (data.device_type() or "").lower()
            d_lbl  = _TYPE_MAP.get(d_type, d_type.capitalize() if d_type else "")
            if _val(client):
                c_str  = f"{client} {c_ver}".strip() if _val(c_ver) else client
                os_str = f"{os_n} {os_v}".strip() if (_val(os_n) and _val(os_v)) else (os_n if _val(os_n) else "")
                parts  = [p for p in [c_str, os_str, d_lbl] if p]
                if parts:
                    return " · ".join(parts)
        except Exception:
            pass

    # Layer 2 — IK-specific fallback patterns
    for pattern, label in _IK_PATTERNS:
        if pattern in ua:
            return label

    # Layer 3 — Unclassified (Claude uses general knowledge + flags with ⚠️)
    return "Unclassified"


def main(path):
    with open(path) as f:
        d = json.load(f)

    out = []

    def section(title):
        out.append(f"\n{'='*60}")
        out.append(f"  {title}")
        out.append(f"{'='*60}")

    def sub(title):
        out.append(f"\n  -- {title} --")

    def line(s=""):
        out.append(s)

    # ── Header ───────────────────────────────────────────────────
    labels = d["request"]["dateWise"]["labels"]
    period_days = len(labels)
    period_start = labels[0][:10] if labels else "?"
    period_end = labels[-1][:10] if labels else "?"

    section("HEADER")
    line(f"_id                 : {d.get('_id', 'N/A')}")
    line(f"period              : {period_start} to {period_end} ({period_days} days)")
    line(f"backend             : {d.get('_meta', {}).get('backend', 'N/A')}")

    # ── Totals ──────────────────────────────────────────────────
    section("TOTALS")
    line(f"request.total       : {d['request']['total']}")
    line(f"bandwidth.total     : {d['bandwidth']['total']} bytes")
    line(f"storage_bytes.total : {d.get('storage_bytes', {}).get('total', 'N/A')} bytes")
    vpu = d.get("videoProcessingUnits", {})
    line(f"vpu.total           : {vpu.get('total', 0)}")
    eu = d.get("extensionUnits", {})
    line(f"extensionUnits.total: {eu.get('total', 0)}")
    sav = d.get("savings", {})
    line(f"savings.sav         : {sav.get('sav', 'N/A')}")
    line(f"savings.size        : {sav.get('size', 'N/A')}")

    # ── Daily Trend ──────────────────────────────────────────────
    section("DAILY TREND (date, requests, bandwidth_bytes)")
    reqs = d["request"]["dateWise"]["datasets"][0]["data"]
    bws  = d["bandwidth"]["dateWise"]["datasets"][0]["data"]
    for lbl, req, bw in zip(labels, reqs, bws):
        line(f"  {lbl[:10]}  requests={req}  bandwidth={bw}")

    # ── Request Pattern ──────────────────────────────────────────
    section("REQUEST PATTERN (all, sorted by count desc)")
    for item in sorted(d["request"].get("pattern", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  name={item['name']}")

    section("BANDWIDTH PATTERN (all, sorted by bandwidth desc)")
    for item in sorted(d["bandwidth"].get("pattern", []), key=lambda x: x["count"], reverse=True):
        line(f"  bandwidth={item['count']}  name={item['name']}")

    # ── Format Wise ──────────────────────────────────────────────
    section("FORMAT WISE")
    fw = d.get("formatWise", {})
    sub("requestWise (sorted by count desc)")
    for item in sorted(fw.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item['bandwidth']}  name={item['name']}")
    sub("bandwidthWise (sorted by bandwidth desc)")
    for item in sorted(fw.get("bandwidthWise", []), key=lambda x: x["bandwidth"], reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  name={item['name']}")

    # ── Status Codes ─────────────────────────────────────────────
    section("STATUS CODES")
    sc = d.get("statusCodeWise", {})
    sub("requestWise")
    for item in sorted(sc.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        bw_val = item.get('bandwidth', 'N/A')
        line(f"  status={item['name']}  count={item['count']}  bandwidth={bw_val}")
    sub("bandwidthWise")
    for item in sorted(sc.get("bandwidthWise", []), key=lambda x: x.get("bandwidth", 0), reverse=True):
        line(f"  status={item['name']}  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}")

    # ── Error Codes ──────────────────────────────────────────────
    section("ERROR CODES (all)")
    for item in sorted(d.get("errorCodeWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  error={item['name']}")

    # ── Result Type (Cache) ──────────────────────────────────────
    section("RESULT TYPE (Cache)")
    rt = d.get("resultType", {})
    sub("requestWise")
    for item in sorted(rt.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  name={item['name']}  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}")
    sub("bandwidthWise")
    for item in sorted(rt.get("bandwidthWise", []), key=lambda x: x.get("bandwidth", 0), reverse=True):
        line(f"  name={item['name']}  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}")

    # ── Country ──────────────────────────────────────────────────
    section("COUNTRY")
    country = d.get("country", {})
    sub("requestWise (sorted by count desc)")
    rw = country.get("requestWise", {})
    line(f"  total_count={rw.get('count', 'N/A')}  total_bandwidth={rw.get('bandwidth', 'N/A')}")
    for item in sorted(rw.get("items", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item['bandwidth']}  code={item.get('code','?')}  name={item.get('name','?')}")
    sub("bandwidthWise (sorted by bandwidth desc)")
    bw_c = country.get("bandwidthWise", {})
    line(f"  total_count={bw_c.get('count', 'N/A')}  total_bandwidth={bw_c.get('bandwidth', 'N/A')}")
    for item in sorted(bw_c.get("items", []), key=lambda x: x["bandwidth"], reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  code={item.get('code','?')}  name={item.get('name','?')}")

    # ── Referral ─────────────────────────────────────────────────
    section("REFERRAL")
    ref = d.get("referral", {})
    sub("requestWise (sorted by count desc)")
    for item in sorted(ref.get("requestWise", {}).get("items", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item['bandwidth']}  name={item['name']}")
    sub("bandwidthWise (sorted by bandwidth desc)")
    for item in sorted(ref.get("bandwidthWise", {}).get("items", []), key=lambda x: x["bandwidth"], reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  name={item['name']}")

    # ── Top User Agents ──────────────────────────────────────────
    section("TOP USER AGENTS (all)")
    if not _DD_AVAILABLE:
        line("  [NOTE: device_detector not installed — labels use IK patterns only]")
    tua = d.get("topUserAgent", {})
    sub("requestWise (sorted by count desc)")
    for item in sorted(tua.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        label = classify_ua(item["name"])
        line(f"  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}  label={label}  ua={item['name']}")
    sub("bandwidthWise (sorted by bandwidth desc)")
    for item in sorted(tua.get("bandwidthWise", []), key=lambda x: x.get("bandwidth", 0), reverse=True):
        label = classify_ua(item["name"])
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  label={label}  ua={item['name']}")

    # ── Browser Distribution ─────────────────────────────────────
    section("BROWSER DISTRIBUTION (all)")
    bd = d.get("browserDistribution", {})
    sub("requestWise")
    for item in sorted(bd.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}  name={item['name']}")

    # ── Device Distribution ──────────────────────────────────────
    section("DEVICE DISTRIBUTION (all)")
    dd = d.get("deviceDistribution", {})
    sub("requestWise")
    for item in sorted(dd.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}  name={item['name']}")

    # ── Image Transforms ─────────────────────────────────────────
    section("IMAGE TRANSFORMS")
    tf = d.get("transform", {})
    rw_tf = tf.get("requestWise", {})
    bw_tf = tf.get("bandwidthWise", {})
    line(f"requestWise.count     : {rw_tf.get('count', 0)}")
    line(f"requestWise.bandwidth : {rw_tf.get('bandwidth', 0)} bytes")
    line(f"bandwidthWise.count   : {bw_tf.get('count', 0)}")
    line(f"bandwidthWise.bandwidth : {bw_tf.get('bandwidth', 0)} bytes")
    sub("requestWise items (sorted by count desc)")
    for item in sorted(rw_tf.get("items", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item['bandwidth']}  tr={item['name']}")
    sub("bandwidthWise items (sorted by bandwidth desc)")
    for item in sorted(bw_tf.get("items", []), key=lambda x: x["bandwidth"], reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  tr={item['name']}")

    # ── Video Transforms ─────────────────────────────────────────
    section("VIDEO TRANSFORMS")
    vtf = d.get("videoTransform", {})
    rw_vtf = vtf.get("requestWise", {})
    bw_vtf = vtf.get("bandwidthWise", {})
    line(f"requestWise.count     : {rw_vtf.get('count', 0)}")
    line(f"requestWise.bandwidth : {rw_vtf.get('bandwidth', 0)} bytes")
    sub("requestWise items (sorted by count desc)")
    for item in sorted(rw_vtf.get("items", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item['bandwidth']}  tr={item['name']}")
    sub("bandwidthWise items (sorted by bandwidth desc)")
    for item in sorted(bw_vtf.get("items", []), key=lambda x: x["bandwidth"], reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  tr={item['name']}")

    # ── Top Images ───────────────────────────────────────────────
    section("TOP IMAGES — BANDWIDTH WISE (all)")
    for item in d.get("topImages", {}).get("bandwidthWise", []):
        line(f"  bandwidth={item['bandwidth']}  views={item.get('views','?')}  url={item['url']}")

    section("TOP IMAGES — REQUEST WISE (all)")
    for item in d.get("topImages", {}).get("requestWise", []):
        line(f"  views={item.get('views','?')}  bandwidth={item.get('bandwidth','?')}  url={item['url']}")

    # ── Top Videos ───────────────────────────────────────────────
    section("TOP VIDEOS — BANDWIDTH WISE (all)")
    for item in d.get("topVideos", {}).get("bandwidthWise", []):
        line(f"  bandwidth={item['bandwidth']}  views={item.get('views','?')}  url={item['url']}")

    section("TOP VIDEOS — REQUEST WISE (all)")
    for item in d.get("topVideos", {}).get("requestWise", []):
        line(f"  views={item.get('views','?')}  bandwidth={item.get('bandwidth','?')}  url={item['url']}")

    # ── Top Others ───────────────────────────────────────────────
    section("TOP OTHERS — BANDWIDTH WISE (all)")
    for item in d.get("topOthers", {}).get("bandwidthWise", []):
        line(f"  bandwidth={item['bandwidth']}  views={item.get('views','?')}  url={item['url']}")

    # ── Top 404s ─────────────────────────────────────────────────
    section("TOP 404s (all)")
    for item in d.get("top404", {}).get("t404", []):
        line(f"  views={item['views']}  url={item['url']}")

    # ── Top IPs ──────────────────────────────────────────────────
    section("TOP IPs (all)")
    tip = d.get("topIps", {})
    sub("requestWise (sorted by count desc)")
    for item in sorted(tip.get("requestWise", []), key=lambda x: x["count"], reverse=True):
        line(f"  count={item['count']}  bandwidth={item.get('bandwidth', 'N/A')}  ip={item['name']}")
    sub("bandwidthWise (sorted by bandwidth desc)")
    for item in sorted(tip.get("bandwidthWise", []), key=lambda x: x.get("bandwidth", 0), reverse=True):
        line(f"  bandwidth={item['bandwidth']}  count={item['count']}  ip={item['name']}")

    # ── VPU ──────────────────────────────────────────────────────
    section("VIDEO PROCESSING UNITS")
    line(f"vpu.total : {vpu.get('total', 0)}")
    for day in vpu.get("dateWise", []):
        usage = day.get("vpuUsage", {})
        total_day = sum(v for v in usage.values() if isinstance(v, (int, float)))
        if total_day > 0:
            line(f"  date={day['date'][:10]}  usage={usage}")

    # ── Extension Units ──────────────────────────────────────────
    section("EXTENSION UNITS")
    line(f"total : {eu.get('total', 0)}")
    for op, count in eu.get("extensionWiseOperations", {}).items():
        if count and count > 0:
            line(f"  {op} = {count}")

    # ── Storage (daily avg) ──────────────────────────────────────
    section("STORAGE (daily avg upload + original cache)")
    for day in d.get("storage", {}).get("dateWise", []):
        upload = day.get("avgUploadStorage")
        orig   = day.get("avgOriginalCacheStorage")
        if upload is not None or orig is not None:
            line(f"  date={day['date'][:10]}  avgUpload={upload}  avgOriginalCache={orig}")

    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 agent/extract.py data/input/<file>.json > data/extracted/<account>-extracted.txt", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
