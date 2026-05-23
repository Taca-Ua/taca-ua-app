/**
 * THROUGHPUT TEST — Maximum Sustainable RPS (Slide 3)
 *
 * Goal: Find the maximum throughput the Public API can sustain before errors
 *       appear. Gradually ramps concurrency from low to high, holding at each
 *       step to measure stable RPS. The point where error_rate exceeds the
 *       threshold identifies the breaking point.
 *
 * Run:
 *   k6 run tests/performance/throughput.js
 *
 * With JSON output for charting:
 *   k6 run --out json=results/throughput.json tests/performance/throughput.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";
import { makeSummary } from "./_report.js";

const errorRate = new Rate("error_rate");
const reqDuration = new Trend("req_duration", true);

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 10 },
    { duration: "30s", target: 30 },
    { duration: "1m", target: 30 },
    { duration: "30s", target: 60 },
    { duration: "1m", target: 60 },
    { duration: "30s", target: 100 },
    { duration: "1m", target: 100 },
    { duration: "30s", target: 150 },
    { duration: "1m", target: 150 },
    { duration: "30s", target: 200 },
    { duration: "1m", target: 200 },
    { duration: "30s", target: 250 },
    { duration: "1m", target: 250 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    // Test is considered broken when error rate exceeds 1%
    error_rate: ["rate<0.01"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;
const SEASON_ID = __ENV.SEASON_ID || "2";

const ENDPOINTS = [
  `${API}/tournaments?page=1&page_size=20`,
  `${API}/matches?page=1&page_size=20`,
  `${API}/ranking/general?season_id=${SEASON_ID}`,
  `${API}/ranking/modality?season_id=${SEASON_ID}`,
  `${API}/teams?page=1&page_size=20`,
  `${API}/nucleos`,
];

export default function () {
  const url = ENDPOINTS[__ITER % ENDPOINTS.length];

  const res = http.get(url);
  reqDuration.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "status 200": (r) => r.status === 200 });
}

export function handleSummary(data) {
  return makeSummary("throughput", data);
}
