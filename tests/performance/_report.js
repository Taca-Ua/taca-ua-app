/**
 * Shared report builder for all k6 test scripts.
 *
 * Usage in a test file:
 *
 *   import { buildReport } from "./_report.js";
 *
 *   export function handleSummary(data) {
 *     return makeSummary("latency", data);
 *   }
 */

export function makeSummary(testName, data) {
  const report = buildReport(testName, data);
  return {
    stdout: report,
    [`tests/performance/results/${testName}_report.txt`]: report,
  };
}

export function buildReport(testName, data) {
  const ts = new Date().toISOString();
  const durationMs = data.state?.testRunDurationMs ?? 0;
  const durationS = (durationMs / 1000).toFixed(1);

  function metric(name) { return data.metrics[name]; }

  function pct(name, p) {
    const m = metric(name);
    if (!m) return "  N/A   ";
    const v = m.values[`p(${p})`] ?? 0;
    return `${v.toFixed(1).padStart(7)} ms`;
  }

  function maxVal(name) {
    const m = metric(name);
    if (!m) return "  N/A   ";
    return `${(m.values.max ?? 0).toFixed(1).padStart(7)} ms`;
  }

  function rps(name) {
    const m = metric(name);
    if (!m) return "N/A";
    return `${(m.values.rate ?? 0).toFixed(2)} req/s`;
  }

  function total(name) {
    const m = metric(name);
    if (!m) return "N/A";
    return `${m.values.count ?? 0}`;
  }

  function errorPct(name) {
    const m = metric(name);
    if (!m) return "N/A";
    return `${((m.values.rate ?? 0) * 100).toFixed(2)} %`;
  }

  const thrLines = [];
  for (const [name, m] of Object.entries(data.metrics)) {
    if (!m.thresholds) continue;
    for (const [expr, result] of Object.entries(m.thresholds)) {
      const tag = result.ok ? "✓ PASS" : "✗ FAIL";
      thrLines.push(`    [${tag}]  ${name}: ${expr}`);
    }
  }
  const allPassed = thrLines.length === 0 || thrLines.every((l) => l.includes("PASS"));

  const epMetrics = Object.keys(data.metrics)
    .filter((k) => k.startsWith("latency_"))
    .sort();

  const HR = "─".repeat(62);
  const lines = [
    "",
    "═".repeat(62),
    `  ${testName.toUpperCase()} TEST REPORT   ${ts}`,
    "═".repeat(62),
    "",
    `  Duration : ${durationS} s`,
    `  Total requests : ${total("http_reqs")}`,
    `  Throughput : ${rps("http_reqs")}`,
    `  Error rate : ${errorPct("http_req_failed")}`,
    "",
    HR,
    "  Latency (all endpoints combined)",
    HR,
    `    p50 :${pct("http_req_duration", 50)}`,
    `    p95 :${pct("http_req_duration", 95)}`,
    `    p99 :${pct("http_req_duration", 99)}`,
    `    max :${maxVal("http_req_duration")}`,
    "",
  ];

  if (epMetrics.length > 0) {
    lines.push(HR);
    lines.push("  Per-endpoint p95");
    lines.push(HR);
    for (const name of epMetrics) {
      const label = name.replace("latency_", "").replace(/_/g, " ");
      lines.push(`    ${label.padEnd(22)}:${pct(name, 95)}`);
    }
    lines.push("");
  }

  lines.push(HR);
  lines.push("  Thresholds");
  lines.push(HR);
  if (thrLines.length === 0) {
    lines.push("    (none defined)");
  } else {
    lines.push(...thrLines);
  }
  lines.push("");
  lines.push(
    allPassed
      ? "  ✓  ALL THRESHOLDS PASSED"
      : "  ✗  SOME THRESHOLDS FAILED — check results above"
  );
  lines.push("═".repeat(62));
  lines.push("");

  return lines.join("\n");
}