/**
 * SMOKE TEST — Sanity Check (run before any heavy test)
 *
 * Goal: Verify the system is up and all tested endpoints respond correctly
 *       under minimal load (1 VU, ~30 s). Run this first to confirm the
 *       stack is healthy before wasting time on heavier test runs.
 *
 * Run:
 *   k6 run tests/performance/smoke.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { makeSummary } from "./_report.js";

export const options = {
  vus: 1,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate==0"],
    http_req_duration: ["p(99)<1000"],
  },
  insecureSkipTLSVerify: true,
};

const BASE = __ENV.BASE_URL || "https://192.168.1.70";
const API = `${BASE}/api/public`;
const SEASON_ID = __ENV.SEASON_ID || "2";

export default function () {
  const endpoints = [
    { url: `${API}/nucleos`, name: "nucleos" },
    { url: `${API}/teams`, name: "teams" },
    { url: `${API}/tournaments`, name: "tournaments" },
    { url: `${API}/matches`, name: "matches" },
    { url: `${API}/ranking/general?season_id=${SEASON_ID}`, name: "ranking_general" },
    { url: `${API}/ranking/modality?season_id=${SEASON_ID}`, name: "ranking_modality" },
    { url: `${API}/regulations`, name: "regulations" },
  ];

  for (const ep of endpoints) {
    const res = http.get(ep.url);
    check(res, {
      [`${ep.name} status 200`]:(r) => r.status === 200,
      [`${ep.name} has body`]:(r) => r.body && r.body.length > 0,
      [`${ep.name} content-type json`]:(r) => r.headers["Content-Type"] &&
                                        r.headers["Content-Type"].includes("application/json"),
    });
    sleep(0.5);
  }
}

export function handleSummary(data) {
  return makeSummary("smoke", data);
}
