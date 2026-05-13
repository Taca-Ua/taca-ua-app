/**
 * STRESS TEST — Find the Breaking Point (Slides 5 & 6)
 *
 * Goal: Push the system beyond its capacity to:
 *   1. Identify at what concurrency level errors start appearing
 *   2. Identify what breaks (CPU, DB connections, memory)
 *   3. Verify the system recovers after load is removed
 *
 * Run:
 *   k6 run tests/performance/stress.js
 *
 * With JSON output for charting:
 *   k6 run --out json=results/stress.json tests/performance/stress.js
 *
 * NOTE: This test is expected to cause errors at peak load.
 *       The threshold below flags the point where the system is considered
 *       "broken" for reporting purposes.
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";
import { makeSummary } from "./_report.js";

const errorRate = new Rate("error_rate");
const reqDuration = new Trend("req_duration", true);

export const options = {
  stages: [
    { duration: "1m", target: 30 },
    { duration: "1m", target: 80 },
    { duration: "2m", target: 200 },
    { duration: "1m", target: 300 },
    { duration: "2m", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(99)<2000"],
    error_rate: ["rate<0.1"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;
const SEASON_ID = __ENV.SEASON_ID || "2";

const HEAVY_ENDPOINTS = [
  `${API}/ranking/general?season_id=${SEASON_ID}`,
  `${API}/ranking/modality?season_id=${SEASON_ID}`,
  `${API}/tournaments?page=1&page_size=50`,
  `${API}/matches?page=1&page_size=50`,
  `${API}/teams?page=1&page_size=50`,
];

export default function () {
  const url = HEAVY_ENDPOINTS[__ITER % HEAVY_ENDPOINTS.length];

  const res = http.get(url, { timeout: "10s" });
  reqDuration.add(res.timings.duration);
  errorRate.add(res.status !== 200);

  check(res, {
    "status 200": (r) => r.status === 200,
    "no server error": (r) => r.status < 500,
  });

  sleep(0.1);
}

export function handleSummary(data) {
  return makeSummary("stress", data);
}
