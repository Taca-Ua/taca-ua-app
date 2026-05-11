/**
 * THROUGHPUT TEST — Requests per Second (Slide 3)
 *
 * Goal: Find the maximum stable throughput (RPS) the Public API can sustain
 *       before latency degrades. Gradually increases concurrency and records
 *       requests/sec at each step.
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
    { duration: "30s", target: 5 },
    { duration: "1m", target: 5 },
    { duration: "30s", target: 20 },
    { duration: "1m", target: 20 },
    { duration: "30s", target: 40 },
    { duration: "1m", target: 40 },
    { duration: "30s", target: 80 },
    { duration: "1m", target: 80 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    error_rate: ["rate<0.05"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;

const ENDPOINTS = [
  `${API}/tournaments?page=1&page_size=20`,
  `${API}/matches?page=1&page_size=20`,
  `${API}/ranking/general`,
  `${API}/ranking/modality`,
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
