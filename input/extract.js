#!/usr/bin/env node
/**
 * ImageKit Analytics JSON Extractor
 * Converts a raw analytics JSON export into a compact structured text file.
 * Feed the output to the analysis agent instead of the raw JSON — saves ~80% tokens.
 *
 * Usage:
 *   node extract.js test/analyticsgirnar.json > test/girnar-extracted.txt
 *
 * No npm dependencies — uses Node built-ins only.
 */

const fs = require("fs");
const path = require("path");

const filePath = process.argv[2];
if (!filePath) {
  console.error("Usage: node extract.js <path-to-analytics.json>");
  process.exit(1);
}

const d = JSON.parse(fs.readFileSync(filePath, "utf8"));
const lines = [];

// ── Helpers ────────────────────────────────────────────────────────────────

const toTB  = (b) => (b / 1_099_511_627_776).toFixed(2);
const toGB  = (b) => (b / 1_073_741_824).toFixed(1);
const fmt   = (n) => Number(n).toLocaleString("en-US");
const pct   = (n, total) => ((n / total) * 100).toFixed(1) + "%";
const pad   = (s, n, right = false) => {
  const str = String(s);
  return right ? str.padStart(n) : str.padEnd(n);
};

function section(title) {
  lines.push("");
  lines.push("=".repeat(60));
  lines.push(`  ${title}`);
  lines.push("=".repeat(60));
}

// ── Totals ─────────────────────────────────────────────────────────────────

section("TOTALS");
const reqTotal = d.request.total;
const bwTotal  = d.bandwidth.total;
const storage  = d.storage_bytes.total;
const days     = d.count || 31;

lines.push(`request.total       : ${fmt(reqTotal)}`);
lines.push(`bandwidth.total     : ${fmt(bwTotal)} bytes = ${toTB(bwTotal)} TB`);
lines.push(`storage_bytes.total : ${fmt(storage)} bytes = ${toGB(storage)} GB`);
lines.push(`period_days         : ${days}`);
lines.push(`daily_avg_requests  : ${fmt(Math.round(reqTotal / days))}`);
lines.push(`daily_avg_bandwidth : ${toGB(bwTotal / days)} GB`);

// ── Daily Request Trend ────────────────────────────────────────────────────

section("DAILY REQUESTS (dateWise)");
const labels  = d.request.dateWise.labels;
const reqData = d.request.dateWise.datasets[0].data;
const bwData  = d.bandwidth.dateWise.datasets[0].data;
const avgReq  = reqData.reduce((a, b) => a + b, 0) / reqData.length;

lines.push(`${pad("Date", 12)} ${pad("Requests", 15, true)} ${pad("Bandwidth (GB)", 15, true)}`);
reqData.forEach((req, i) => {
  const spike = req > 2 * avgReq ? "  ← SPIKE (>2× avg)" : "";
  lines.push(`${pad(labels[i].slice(0, 10), 12)} ${pad(fmt(req), 15, true)} ${pad(toGB(bwData[i]), 15, true)}${spike}`);
});

const spikeDays = reqData
  .map((r, i) => (r > 2 * avgReq ? labels[i].slice(0, 10) : null))
  .filter(Boolean);
lines.push(`\nDaily avg requests : ${fmt(Math.round(avgReq))}`);
lines.push(`Spike days (>2×avg): ${spikeDays.length ? spikeDays.join(", ") : "none"}`);

// ── Request Pattern ────────────────────────────────────────────────────────

section("REQUEST PATTERN (top 15 by request)");
[...d.request.pattern]
  .sort((a, b) => b.count - a.count)
  .slice(0, 15)
  .forEach((item) => {
    lines.push(`  ${pad(item.name, 30)} ${pad(fmt(item.count), 15, true)}  (${pct(item.count, reqTotal)})`);
  });

section("BANDWIDTH PATTERN (top 15 by bandwidth)");
[...(d.bandwidth.pattern || [])]
  .sort((a, b) => b.count - a.count)
  .slice(0, 15)
  .forEach((item) => {
    lines.push(`  ${pad(item.name, 30)} ${pad(toGB(item.count) + " GB", 12, true)}  (${pct(item.count, bwTotal)})`);
  });

// ── Format Wise ────────────────────────────────────────────────────────────

section("FORMAT WISE (all, sorted by count)");
const fw = [...(d.formatWise || [])].sort((a, b) => b.count - a.count);
const fwTotalCount = fw.reduce((s, x) => s + x.count, 0);
lines.push(`format_sum : ${fmt(fwTotalCount)}  (${pct(fwTotalCount, reqTotal)} of request.total)`);
lines.push(`${pad("Format", 45)} ${pad("Count", 15, true)} ${pad("BW (GB)", 10, true)} ${pad("%Count", 7, true)}`);
fw.forEach((item) => {
  lines.push(
    `  ${pad(item.name, 43)} ${pad(fmt(item.count), 15, true)} ${pad(toGB(item.bandwidth), 10, true)} ${pad(pct(item.count, reqTotal), 7, true)}`
  );
});

// ── Country ────────────────────────────────────────────────────────────────

section("COUNTRY (top 10 by request)");
const countryTotal = d.country.count;
lines.push(`country.count : ${fmt(countryTotal)}`);
lines.push(`${pad("Country", 25)} ${pad("Requests", 15, true)} ${pad("% Attributed", 13, true)} ${pad("BW (GB)", 10, true)}`);
[...d.country.items]
  .sort((a, b) => b.count - a.count)
  .slice(0, 10)
  .forEach((item) => {
    lines.push(
      `  ${pad(item.name || "?", 23)} ${pad(fmt(item.count), 15, true)} ${pad(pct(item.count, countryTotal), 13, true)} ${pad(toGB(item.bandwidth), 10, true)}`
    );
  });

// ── Referral ───────────────────────────────────────────────────────────────

section("REFERRAL (top 10)");
lines.push(`${pad("Referrer", 45)} ${pad("Requests", 12, true)} ${pad("BW (GB)", 10, true)}`);
[...d.referral.items]
  .sort((a, b) => b.count - a.count)
  .slice(0, 10)
  .forEach((item) => {
    lines.push(`  ${pad(item.name, 43)} ${pad(fmt(item.count), 12, true)} ${pad(toGB(item.bandwidth), 10, true)}`);
  });

// ── Top User Agent ─────────────────────────────────────────────────────────

section("TOP USER AGENTS (top 30, sorted by count)");
lines.push(`${pad("UA String", 80)} ${pad("Count", 12, true)} ${pad("BW (GB)", 10, true)}`);
[...(d.topUserAgent || [])]
  .sort((a, b) => b.count - a.count)
  .slice(0, 30)
  .forEach((item) => {
    lines.push(
      `  ${pad(item.name.slice(0, 78), 78)} ${pad(fmt(item.count), 12, true)} ${pad(toGB(item.bandwidth), 10, true)}`
    );
  });

// ── Device Type Distribution ───────────────────────────────────────────────

section("DEVICE TYPE DISTRIBUTION");
const dtd = d.deviceTypeDistribution || [];
const dtdTotal = dtd.reduce((s, x) => s + x.count, 0);
lines.push(`device_sum : ${fmt(dtdTotal)}  (${pct(dtdTotal, reqTotal)} of request.total)`);
[...dtd]
  .sort((a, b) => b.count - a.count)
  .forEach((item) => {
    lines.push(`  ${pad(item.name, 20)} ${pad(fmt(item.count), 15, true)}  (${pct(item.count, reqTotal)})`);
  });

// ── Image Transforms ───────────────────────────────────────────────────────

section("IMAGE TRANSFORMS (sorted by count)");
const tf = d.transform || {};
lines.push(`transform.count     : ${fmt(tf.count || 0)}  (${pct(tf.count || 0, reqTotal)} of total)`);
lines.push(`transform.bandwidth : ${toGB(tf.bandwidth || 0)} GB`);
lines.push(`unique items        : ${(tf.items || []).length}`);
lines.push(`${pad("Transform String", 50)} ${pad("Count", 12, true)} ${pad("BW (GB)", 10, true)}`);
[...(tf.items || [])]
  .sort((a, b) => b.count - a.count)
  .slice(0, 50)
  .forEach((item) => {
    lines.push(
      `  ${pad(item.name, 48)} ${pad(fmt(item.count), 12, true)} ${pad(toGB(item.bandwidth), 10, true)}`
    );
  });

// ── Video Transforms ───────────────────────────────────────────────────────

section("VIDEO TRANSFORMS");
const vtf = d.videoTransform || {};
lines.push(`videoTransform.count : ${fmt(vtf.count || 0)}`);
(vtf.items || []).forEach((item) => {
  lines.push(`  ${pad(item.name, 48)} ${pad(fmt(item.count), 12, true)} ${pad(toGB(item.bandwidth), 10, true)}`);
});

// ── Result Type (Cache) ────────────────────────────────────────────────────

section("RESULT TYPE (Cache)");
const rt     = d.resultType || [];
const rtMap  = Object.fromEntries(rt.map((x) => [x.name, x.count]));
const hit    = rtMap.Hit  || 0;
const miss   = rtMap.Miss || 0;
const hitRate = hit + miss > 0 ? ((hit / (hit + miss)) * 100).toFixed(1) : "?";
lines.push(`Cache hit rate : ${hitRate}%  (Hit=${fmt(hit)}, Miss=${fmt(miss)})`);
rt.forEach((item) => {
  lines.push(`  ${pad(item.name, 15)} ${pad(fmt(item.count), 15, true)}  (${pct(item.count, reqTotal)})`);
});

// ── Status Codes ───────────────────────────────────────────────────────────

section("STATUS CODES");
(d.statusCodeWise || []).forEach((item) => {
  lines.push(`  ${pad(String(item.name), 10)} ${pad(fmt(item.count), 15, true)}  (${pct(item.count, reqTotal)})`);
});

// ── Error Codes ────────────────────────────────────────────────────────────

section("ERROR CODES");
(d.errorCodeWise || []).forEach((item) => {
  lines.push(`  [${pad(fmt(item.count), 8, true)}]  ${item.name}`);
});

// ── Top Images (bandwidth) ─────────────────────────────────────────────────

section("TOP IMAGES — BANDWIDTH WISE (top 30)");
lines.push(`${pad("URL", 85)} ${pad("BW(GB)", 7, true)} ${pad("Views", 10, true)} ${pad("BW/view(KB)", 12, true)} ${pad("Has tr=", 7, true)}`);
(d.topImages?.bandwidthWise || []).slice(0, 30).forEach((item) => {
  const bpvKB = item.views ? (item.bandwidth / item.views / 1024).toFixed(1) : "?";
  const hasTr = item.url.includes("tr=") || item.url.includes("imwidth") ? "YES" : "no";
  lines.push(
    `  ${pad(item.url.slice(0, 83), 85)} ${pad(toGB(item.bandwidth), 7, true)} ${pad(fmt(item.views), 10, true)} ${pad(bpvKB, 12, true)} ${pad(hasTr, 7, true)}`
  );
});

// ── Top Videos (bandwidth) ─────────────────────────────────────────────────

section("TOP VIDEOS — BANDWIDTH WISE (top 10)");
lines.push(`${pad("URL", 85)} ${pad("BW(GB)", 7, true)} ${pad("Views", 8, true)} ${pad("BW/view(MB)", 12, true)}`);
(d.topVideos?.bandwidthWise || []).slice(0, 10).forEach((item) => {
  const bpvMB = item.views ? (item.bandwidth / item.views / 1_048_576).toFixed(2) : "?";
  lines.push(
    `  ${pad(item.url.slice(0, 83), 85)} ${pad(toGB(item.bandwidth), 7, true)} ${pad(fmt(item.views), 8, true)} ${pad(bpvMB, 12, true)}`
  );
});

// ── Top 404s ───────────────────────────────────────────────────────────────

section("TOP 404s");
(d.top404?.t404 || []).slice(0, 20).forEach((item) => {
  lines.push(`  [${pad(fmt(item.views), 8, true)} views]  ${item.url}`);
});

// ── Top IPs ────────────────────────────────────────────────────────────────

section("TOP IPs (top 10)");
lines.push(`${pad("IP", 18)} ${pad("Requests", 12, true)} ${pad("%Total", 7, true)} ${pad("BW (GB)", 10, true)} ${pad("Avg (KB)", 10, true)}`);
(d.topIps || []).slice(0, 10).forEach((item) => {
  const avgKB = item.count ? (item.bandwidth / item.count / 1024).toFixed(1) : "?";
  lines.push(
    `  ${pad(item.name, 16)} ${pad(fmt(item.count), 12, true)} ${pad(pct(item.count, reqTotal), 7, true)} ${pad(toGB(item.bandwidth), 10, true)} ${pad(avgKB, 10, true)}`
  );
});

// ── VPU ────────────────────────────────────────────────────────────────────

section("VIDEO PROCESSING UNITS");
const vpu = d.videoProcessingUnits || {};
lines.push(`VPU total : ${vpu.total ?? 0}`);
const nonZeroDays = (vpu.dateWise || []).filter((day) =>
  Object.values(day.vpuUsage || {}).some((v) => v > 0)
);
if (nonZeroDays.length) {
  lines.push("Non-zero VPU days:");
  nonZeroDays.forEach((day) => {
    lines.push(`  ${day.date.slice(0, 10)}: ${JSON.stringify(day.vpuUsage)}`);
  });
} else {
  lines.push("All daily VPU entries are zero.");
}

// ── Output ─────────────────────────────────────────────────────────────────

console.log(lines.join("\n"));
