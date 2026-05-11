/**
 * SOAK TEST — Endurance / Memory Leak Detection
 *
 * Goal: Run at a moderate but sustained load for an extended period to
 *       detect slow resource leaks that only appear over time:
 *         - Memory growth (Python process not releasing objects)
 *         - DB connections not being returned to the pool (pool_size=10)
 *         - Response time gradually degrading ("slow rot")
 *         - File descriptor exhaustion
 *
 * Default duration: 30 minutes at 15 VUs.
 * Override duration: k6 run --duration 60m tests/performance/soak.js
 *
 * What to watch in Grafana while this runs:
 *   - Container memory (should be flat)
 *   - DB active connections (should stay below pool_size=10 + max_overflow=20)
 *   - p95 latency trend over time (should be flat, not rising)
 *
 * Run:
 *   k6 run tests/performance/soak.js
 *
 * With JSON output:
 *   k6 run --out json=tests/performance/results/soak.json tests/performance/soak.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";
import { makeSummary } from "./_report.js";

const errorRate = new Rate("error_rate");
const reqDuration = new Trend("req_duration", true);

export const options = {
  stages: [
    { duration: "2m", target: 15 },
    { duration: "26m", target: 15 },
    { duration: "2m", target: 0  },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    error_rate: ["rate<0.01"],
    http_req_failed: ["rate<0.01"],
  },
};

const BASE = __ENV.BASE_URL || "http://localhost";
const API = `${BASE}/api/public`;

const ENDPOINTS = [
  `${API}/nucleos`,
  `${API}/teams?page=1&page_size=20`,
  `${API}/tournaments?page=1&page_size=20`,
  `${API}/matches?page=1&page_size=20`,
  `${API}/ranking/general`,
  `${API}/ranking/modality`,
  `${API}/regulations`,
];

export default function () {
  const url = ENDPOINTS[__ITER % ENDPOINTS.length];

  const res = http.get(url);
  reqDuration.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, {
    "status 200": (r) => r.status === 200,
    "body not empty": (r) => r.body && r.body.length > 0,
  });

  sleep(1);
}

export function handleSummary(data) {
  return makeSummary("soak", data);
}
