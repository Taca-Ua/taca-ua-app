/**
 * LATENCY TEST — Response Time Metrics (Slide 2)
 *
 * Goal: Measure p50/p95/p99 response times per endpoint under a realistic
 *       steady load. A fixed number of virtual users runs for a sustained
 *       duration so that Grafana/k6 Cloud can produce clean percentile graphs.
 *
 * Run:
 *   k6 run tests/performance/latency.js
 *
 * With HTML report (requires xk6-reporter or k6 --out):
 *   k6 run --out json=results/latency.json tests/performance/latency.js
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";
import { makeSummary } from "./_report.js";

// ── Custom per-endpoint latency metrics ──────────────────────────────────────
const latencyTournaments = new Trend("latency_tournaments", true);
const latencyMatches = new Trend("latency_matches", true);
const latencyGeneralRank = new Trend("latency_general_rank", true);
const latencyModalityRank = new Trend("latency_modality_rank", true);
const latencyTeams = new Trend("latency_teams", true);
const latencyNucleos = new Trend("latency_nucleos", true);
const errorRate = new Rate("error_rate");

export const options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "3m", target: 20 },
    { duration: "15s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    latency_tournaments: ["p(95)<500", "p(99)<1000"],
    latency_matches: ["p(95)<500", "p(99)<1000"],
    latency_general_rank: ["p(95)<500", "p(99)<1000"],
    latency_modality_rank: ["p(95)<500", "p(99)<1000"],
    latency_teams: ["p(95)<500", "p(99)<1000"],
    latency_nucleos: ["p(95)<300", "p(99)<600"],
    error_rate: ["rate<0.01"],
  },
  insecureSkipTLSVerify: true,
};

const BASE = __ENV.BASE_URL || "https://192.168.1.70";
const API = `${BASE}/api/public`;
const SEASON_ID = __ENV.SEASON_ID || "2";

export default function () {
  let res;

  res = http.get(`${API}/tournaments?page=1&page_size=20`);
  latencyTournaments.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "tournaments 200": (r) => r.status === 200 });

  sleep(0.3);

  res = http.get(`${API}/matches?page=1&page_size=20`);
  latencyMatches.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "matches 200": (r) => r.status === 200 });

  sleep(0.3);

  res = http.get(`${API}/ranking/general?season_id=${SEASON_ID}`);
  latencyGeneralRank.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "general ranking 200": (r) => r.status === 200 });

  sleep(0.3);

  res = http.get(`${API}/ranking/modality?season_id=${SEASON_ID}`);
  latencyModalityRank.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "modality ranking 200": (r) => r.status === 200 });

  sleep(0.3);

  res = http.get(`${API}/teams?page=1&page_size=20`);
  latencyTeams.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "teams 200": (r) => r.status === 200 });

  sleep(0.3);

  res = http.get(`${API}/nucleos`);
  latencyNucleos.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  check(res, { "nucleos 200": (r) => r.status === 200 });

  sleep(1);
}

export function handleSummary(data) {
  return makeSummary("latency", data);
}
