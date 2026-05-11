/**
 * PEAK TEST — Expected Maximum Real-World Load (Slide 6 complement)
 *
 * Goal: Simulate the realistic traffic spike that happens when results are
 *       published (e.g. end of a tournament day — many users refresh rankings
 *       and standings at the same time). Unlike the stress test, this does NOT
 *       try to break the system — it validates that the system meets its SLOs
 *       at the highest expected real load.
 *
 * Scenario modelled:
 *   - Normal day:        ~20 concurrent users
 *   - Results announced: spike to ~200 concurrent users for ~2 min
 *   - Settling back:     returns to normal
 *
 * Run:
 *   k6 run tests/performance/peak.js
 *
 * With JSON output:
 *   k6 run --out json=tests/performance/results/peak.json tests/performance/peak.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";
import { makeSummary } from "./_report.js";

const errorRate = new Rate("error_rate");
const rankingLatency = new Trend("latency_ranking", true);
const listLatency = new Trend("latency_list", true);

export const options = {
  stages: [
    { duration: "1m", target: 20 },
    { duration: "30s", target: 200 },
    { duration: "2m", target: 200 },
    { duration: "30s", target: 20 },
    { duration: "1m", target: 20 },
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1500"],
    latency_ranking: ["p(95)<600", "p(99)<1500"],
    latency_list: ["p(95)<400", "p(99)<800"],
    error_rate: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;

export default function () {
  const scenario = Math.random();

  if (scenario < 0.40) {
    const res = http.get(`${API}/ranking/general`);
    rankingLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, { "general ranking 200": (r) => r.status === 200 });

  } else if (scenario < 0.65) {
    const res = http.get(`${API}/ranking/modality`);
    rankingLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, { "modality ranking 200": (r) => r.status === 200 });

  } else if (scenario < 0.80) {
    const res = http.get(`${API}/tournaments?page=1&page_size=20`);
    listLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, { "tournaments 200": (r) => r.status === 200 });

  } else if (scenario < 0.92) {
    const res = http.get(`${API}/matches?page=1&page_size=20`);
    listLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, { "matches 200": (r) => r.status === 200 });

  } else {
    const res = http.get(`${API}/nucleos`);
    listLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, { "nucleos 200": (r) => r.status === 200 });
  }

  sleep(Math.random() * 2 + 0.5);
}

export function handleSummary(data) {
  return makeSummary("peak", data);
}
