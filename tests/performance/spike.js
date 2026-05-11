/**
 * SPIKE TEST — Sudden Burst Resilience
 *
 * Goal: Verify the system can survive an instantaneous surge with zero
 *       warm-up time. Unlike the peak test (which ramps gradually), this
 *       goes from idle to maximum VUs in one step, then drops back instantly.
 *
 * Scenario modelled:
 *   A push notification or viral share sends hundreds of users to the
 *   rankings page at the exact same moment.
 *
 * Key question answered:
 *   Does the system recover after the spike, or does it stay degraded?
 *
 * Run:
 *   k6 run tests/performance/spike.js
 *
 * With JSON output:
 *   k6 run --out json=tests/performance/results/spike.json tests/performance/spike.js
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
    { duration: "30s", target: 5 },
    { duration: "10s", target: 200 },
    { duration: "1m", target: 200 },
    { duration: "10s", target: 5 },
    { duration: "2m", target: 5 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    error_rate: ["rate<0.20"],
    http_req_failed: ["rate<0.20"],
    http_req_duration: ["p(95)<2000"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;

export default function () {
  const scenario = Math.random();

  if (scenario < 0.50) {
    const res = http.get(`${API}/ranking/general`, { timeout: "15s" });
    rankingLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, {
      "general ranking 200": (r) => r.status === 200,
      "general ranking no crash": (r) => r.status < 500,
    });
  } else if (scenario < 0.80) {
    const res = http.get(`${API}/tournaments?page=1&page_size=20`, { timeout: "15s" });
    listLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, {
      "tournaments 200": (r) => r.status === 200,
      "tournaments no crash": (r) => r.status < 500,
    });
  } else {
    const res = http.get(`${API}/ranking/modality`, { timeout: "15s" });
    rankingLatency.add(res.timings.duration);
    errorRate.add(res.status !== 200);
    check(res, {
      "modality ranking 200": (r) => r.status === 200,
      "modality ranking no crash": (r) => r.status < 500,
    });
  }

  sleep(0.5);
}

export function handleSummary(data) {
  return makeSummary("spike", data);
}
