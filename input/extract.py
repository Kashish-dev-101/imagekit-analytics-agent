#!/usr/bin/env python3
"""
ImageKit Analytics JSON Extractor
Run this before the analysis prompt to produce a compact data file.

Usage:
    python3 extract.py test/analyticsgirnar.json > test/girnar-extracted.txt

The output is a structured text summary of all fields the prompt needs.
Feed the output file to the agent instead of the raw JSON — saves ~90% of tokens.
"""

import json
import sys
from pathlib import Path


def bytes_to_tb(b):
    return round(b / 1_099_511_627_776, 2)


def bytes_to_gb(b):
    return round(b / 1_073_741_824, 1)


def fmt_count(n):
    return f"{n:,}"


def main(path):
    with open(path) as f:
        d = json.load(f)

    out = []

    def section(title):
        out.append(f"\n{'='*60}")
        out.append(f"  {title}")
        out.append(f"{'='*60}")

    def line(s=""):
        out.append(s)

    # ── Totals ──────────────────────────────────────────────────
    section("TOTALS")
    req_total = d["request"]["total"]
    bw_total = d["bandwidth"]["total"]
    storage = d["storage_bytes"]["total"]
    line(f"request.total       : {fmt_count(req_total)}")
    line(f"bandwidth.total     : {fmt_count(bw_total)} bytes = {bytes_to_tb(bw_total)} TB")
    line(f"storage_bytes.total : {fmt_count(storage)} bytes = {bytes_to_gb(storage)} GB")
    line(f"period_days (count) : {d.get('count', '?')}")
    if d.get("count"):
        days = d["count"]
        line(f"daily_avg_requests  : {fmt_count(req_total // days)}")
        line(f"daily_avg_bandwidth : {bytes_to_gb(bw_total // days)} GB")

    # ── Daily Request Trend ──────────────────────────────────────
    section("DAILY REQUESTS (dateWise)")
    labels = d["request"]["dateWise"]["labels"]
    reqs   = d["request"]["dateWise"]["datasets"][0]["data"]
    bws    = d["bandwidth"]["dateWise"]["datasets"][0]["data"]
    avg_req = sum(reqs) / len(reqs)
    spike_days = [(labels[i][:10], reqs[i]) for i in range(len(reqs)) if reqs[i] > 2 * avg_req]
    line(f"{'Date':<12} {'Requests':>15} {'Bandwidth (GB)':>15}")
    for lbl, req, bw in zip(labels, reqs, bws):
        spike = " ← SPIKE (>2× avg)" if req > 2 * avg_req else ""
        line(f"{lbl[:10]:<12} {fmt_count(req):>15} {bytes_to_gb(bw):>15}{spike}")
    line(f"\nDaily avg requests : {fmt_count(int(avg_req))}")
    line(f"Spike days (>2×avg): {spike_days if spike_days else 'none'}")

    # ── Request Pattern ──────────────────────────────────────────
    section("REQUEST PATTERN (top 15 by request)")
    for item in sorted(d["request"]["pattern"], key=lambda x: x["count"], reverse=True)[:15]:
        pct = item["count"] / req_total * 100
        line(f"  {item['name']:<30} {fmt_count(item['count']):>15}  ({pct:.1f}%)")

    section("BANDWIDTH PATTERN (top 15 by bandwidth)")
    bw_patterns = d.get("bandwidth", {}).get("pattern", [])
    for item in sorted(bw_patterns, key=lambda x: x["count"], reverse=True)[:15]:
        pct = item["count"] / bw_total * 100
        line(f"  {item['name']:<30} {bytes_to_gb(item['count']):>10} GB  ({pct:.1f}%)")

    # ── Format Wise ──────────────────────────────────────────────
    section("FORMAT WISE (all, sorted by count)")
    fw = sorted(d.get("formatWise", []), key=lambda x: x["count"], reverse=True)
    fw_total_count = sum(x["count"] for x in fw)
    line(f"format_sum : {fmt_count(fw_total_count)}  ({fw_total_count/req_total*100:.1f}% of request.total)")
    line(f"{'Format':<45} {'Count':>15} {'BW (GB)':>10} {'%Count':>7}")
    for item in fw:
        pct = item["count"] / req_total * 100
        line(f"  {item['name']:<43} {fmt_count(item['count']):>15} {bytes_to_gb(item['bandwidth']):>10} {pct:>6.2f}%")

    # ── Country ──────────────────────────────────────────────────
    section("COUNTRY (top 10 by request)")
    country_total = d["country"]["count"]
    line(f"country.count : {fmt_count(country_total)}")
    line(f"{'Country':<25} {'Requests':>15} {'%Attributed':>12} {'BW (GB)':>10}")
    for item in sorted(d["country"]["items"], key=lambda x: x["count"], reverse=True)[:10]:
        pct = item["count"] / country_total * 100
        line(f"  {item.get('name','?'):<23} {fmt_count(item['count']):>15} {pct:>11.1f}% {bytes_to_gb(item['bandwidth']):>10}")

    # ── Referral ─────────────────────────────────────────────────
    section("REFERRAL (top 10)")
    line(f"{'Referrer':<45} {'Requests':>12} {'BW (GB)':>10}")
    for item in sorted(d["referral"]["items"], key=lambda x: x["count"], reverse=True)[:10]:
        line(f"  {item['name']:<43} {fmt_count(item['count']):>12} {bytes_to_gb(item['bandwidth']):>10}")

    # ── Top User Agent ───────────────────────────────────────────
    section("TOP USER AGENTS (top 30, sorted by count)")
    line(f"{'UA String':<80} {'Count':>12} {'BW (GB)':>10}")
    for item in sorted(d.get("topUserAgent", []), key=lambda x: x["count"], reverse=True)[:30]:
        ua = item["name"][:78]
        line(f"  {ua:<78} {fmt_count(item['count']):>12} {bytes_to_gb(item['bandwidth']):>10}")

    # ── Device Type Distribution ─────────────────────────────────
    section("DEVICE TYPE DISTRIBUTION")
    dtd = d.get("deviceTypeDistribution", [])
    dtd_total = sum(x["count"] for x in dtd)
    line(f"device_sum : {fmt_count(dtd_total)}  ({dtd_total/req_total*100:.1f}% of request.total)")
    for item in sorted(dtd, key=lambda x: x["count"], reverse=True):
        pct = item["count"] / req_total * 100
        line(f"  {item['name']:<20} {fmt_count(item['count']):>15}  ({pct:.1f}%)")

    # ── Transform ────────────────────────────────────────────────
    section("IMAGE TRANSFORMS (top 50, sorted by count)")
    tf = d.get("transform", {})
    line(f"transform.count     : {fmt_count(tf.get('count', 0))}  ({tf.get('count',0)/req_total*100:.1f}% of total)")
    line(f"transform.bandwidth : {bytes_to_gb(tf.get('bandwidth', 0))} GB")
    line(f"unique items shown  : {len(tf.get('items', []))}")
    line(f"{'Transform String':<50} {'Count':>12} {'BW (GB)':>10}")
    for item in sorted(tf.get("items", []), key=lambda x: x["count"], reverse=True)[:50]:
        line(f"  {item['name']:<48} {fmt_count(item['count']):>12} {bytes_to_gb(item['bandwidth']):>10}")

    # ── Video Transform ──────────────────────────────────────────
    section("VIDEO TRANSFORMS")
    vtf = d.get("videoTransform", {})
    line(f"videoTransform.count : {fmt_count(vtf.get('count', 0))}")
    for item in vtf.get("items", []):
        line(f"  {item['name']:<48} {fmt_count(item['count']):>12} {bytes_to_gb(item['bandwidth']):>10}")

    # ── Result Type (Cache) ──────────────────────────────────────
    section("RESULT TYPE (Cache)")
    rt = d.get("resultType", [])
    rt_dict = {x["name"]: x["count"] for x in rt}
    hit  = rt_dict.get("Hit", 0)
    miss = rt_dict.get("Miss", 0)
    hit_rate = hit / (hit + miss) * 100 if (hit + miss) else 0
    line(f"Cache hit rate : {hit_rate:.1f}%  (Hit={fmt_count(hit)}, Miss={fmt_count(miss)})")
    for item in rt:
        pct = item["count"] / req_total * 100
        line(f"  {item['name']:<15} {fmt_count(item['count']):>15}  ({pct:.2f}%)")

    # ── Status Codes ─────────────────────────────────────────────
    section("STATUS CODES")
    for item in d.get("statusCodeWise", []):
        pct = item["count"] / req_total * 100
        line(f"  {str(item['name']):<10} {fmt_count(item['count']):>15}  ({pct:.2f}%)")

    # ── Error Codes ──────────────────────────────────────────────
    section("ERROR CODES")
    for item in d.get("errorCodeWise", []):
        line(f"  [{fmt_count(item['count']):>8}]  {item['name']}")

    # ── Top Images (bandwidth) ───────────────────────────────────
    section("TOP IMAGES — BANDWIDTH WISE (top 30)")
    line(f"{'URL':<90} {'BW (GB)':>8} {'Views':>10} {'BW/view (KB)':>14} {'Transform in URL':>5}")
    for item in d.get("topImages", {}).get("bandwidthWise", [])[:30]:
        url = item["url"]
        bw  = item["bandwidth"]
        views = item["views"]
        bpv_kb = bw / views / 1024 if views else 0
        # crude transform detection in URL
        has_tr = "tr=" in url or "imwidth" in url
        tr_flag = "YES" if has_tr else "no"
        short_url = url[:88]
        line(f"  {short_url:<90} {bytes_to_gb(bw):>8} {fmt_count(views):>10} {bpv_kb:>13.1f} {tr_flag:>5}")

    # ── Top Videos (bandwidth) ───────────────────────────────────
    section("TOP VIDEOS — BANDWIDTH WISE (top 10)")
    line(f"{'URL':<90} {'BW (GB)':>8} {'Views':>8} {'BW/view (MB)':>13}")
    for item in d.get("topVideos", {}).get("bandwidthWise", [])[:10]:
        url = item["url"][:88]
        bw  = item["bandwidth"]
        views = item["views"]
        bpv_mb = bw / views / 1_048_576 if views else 0
        line(f"  {url:<90} {bytes_to_gb(bw):>8} {fmt_count(views):>8} {bpv_mb:>12.2f}")

    # ── Top 404s ─────────────────────────────────────────────────
    section("TOP 404s")
    for item in d.get("top404", {}).get("t404", [])[:20]:
        line(f"  [{fmt_count(item['views']):>8} views]  {item['url']}")

    # ── Top IPs ──────────────────────────────────────────────────
    section("TOP IPs (top 10)")
    line(f"{'IP':<18} {'Requests':>12} {'%Total':>7} {'BW (GB)':>10} {'Avg size (KB)':>14}")
    for item in d.get("topIps", [])[:10]:
        pct = item["count"] / req_total * 100
        avg_kb = item["bandwidth"] / item["count"] / 1024 if item["count"] else 0
        line(f"  {item['name']:<16} {fmt_count(item['count']):>12} {pct:>6.2f}% {bytes_to_gb(item['bandwidth']):>10} {avg_kb:>13.1f}")

    # ── VPU ──────────────────────────────────────────────────────
    section("VIDEO PROCESSING UNITS")
    vpu = d.get("videoProcessingUnits", {})
    line(f"VPU total : {vpu.get('total', 0)}")
    # summarise non-zero days only
    nonzero = []
    for day in vpu.get("dateWise", []):
        usage = day.get("vpuUsage", {})
        total_day = sum(usage.values())
        if total_day > 0:
            nonzero.append((day["date"][:10], usage))
    if nonzero:
        line("Non-zero VPU days:")
        for date, usage in nonzero:
            line(f"  {date}: {usage}")
    else:
        line("All daily VPU entries are zero except total.")

    print("\n".join(out))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 extract.py <path-to-analytics.json>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])
