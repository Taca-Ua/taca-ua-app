# Performance Tests

k6-based performance test suite for the TACA Public API (`/api/public`).

## Scripts

| File | Duration | VUs | Purpose |
|------|----------|-----|---------|
| `smoke.js` | ~30 s | 1 | Sanity check — all endpoints must return 200. Run this first. |
| `latency.js` | ~4 min | 20 | Measures p50/p95/p99 response time per endpoint at steady load. |
| `throughput.js` | ~7 min | 5→80 | Staircase ramp to find max stable RPS before latency degrades. |
| `peak.js` | ~6 min | 10→100 | Gradual ramp to realistic maximum load; SLOs must hold throughout. |
| `spike.js` | ~5 min | 5→200 | Instant surge with no warm-up; tests burst resilience and recovery. |
| `stress.js` | ~7 min | 30→300 | Pushes system to failure; identifies bottleneck and verifies recovery. |
| `soak.js` | ~30 min | 15 | Sustained load to detect memory leaks, DB pool exhaustion, latency rot. |

### Test type comparison

| Type | Ramp | Goal | Errors expected? |
|------|------|------|-----------------|
| Smoke | — | Confirm stack is healthy | No |
| Latency | Gradual | Measure p50/p95/p99 | No |
| Throughput | Staircase | Find max RPS ceiling | No |
| Peak | Gradual (30 s) | Validate SLOs at expected max load | No (< 1 %) |
| Spike | Instant (10 s) | Test burst resilience & recovery | Yes (up to 20 % at peak) |
| Stress | Gradual (aggressive) | Find breaking point & bottleneck | Yes (intentional) |
| Soak | Gradual | Detect slow leaks over time | No |

### Recommended run order

```
smoke → latency → throughput → peak → spike → stress → soak
```

Run soak last — it takes 30 minutes.

---

## Prerequisites

### Install k6

```bash
sudo snap install k6

```

### Start the stack

```bash
docker compose -f docker-compose.dev.yml up -d
```

Populate the database with test data before running any test:

```bash
python tools/populate_db2.py
```

---

## Running the tests

Run from the repository root. All scripts accept a `BASE_URL` env var (default: `http://localhost`).

```bash
# Smoke
k6 run tests/performance/smoke.js

# Latency
k6 run tests/performance/latency.js

# Throughput
k6 run tests/performance/throughput.js

# Peak
k6 run tests/performance/peak.js

# Spike
k6 run tests/performance/spike.js

# Stress
k6 run tests/performance/stress.js

# Soak
k6 run tests/performance/soak.js
```

### Custom base URL (e.g. local network / hotspot)

```bash
k6 run -e BASE_URL=http://192.168.1.100 tests/performance/latency.js
```

### Save results as JSON (for charts/graphs)

```bash
mkdir -p tests/performance/results

k6 run --out json=tests/performance/results/smoke.json      tests/performance/smoke.js
k6 run --out json=tests/performance/results/latency.json    tests/performance/latency.js
k6 run --out json=tests/performance/results/throughput.json tests/performance/throughput.js
k6 run --out json=tests/performance/results/peak.json       tests/performance/peak.js
k6 run --out json=tests/performance/results/spike.json      tests/performance/spike.js
k6 run --out json=tests/performance/results/stress.json     tests/performance/stress.js
k6 run --out json=tests/performance/results/soak.json       tests/performance/soak.js
```

---

## Monitoring during tests

Grafana is accessible **directly** at:

```
http://localhost:3002
```

Login: `admin` / `admin`

### What to watch per test

| Test | Key panels |
|------|-----------|
| Latency | HTTP request duration histogram, p95/p99 per endpoint |
| Throughput | Requests/sec, active DB connections |
| Peak | p95 latency + error rate across the spike window |
| Spike | Error rate during burst, latency recovery after drop |
| Stress | CPU usage, DB connections (pool limit: 10 + 20 overflow), error rate |
| Soak | Memory per container over time, p95 latency trend (must stay flat) |

Logs are available in Grafana → Explore → Loki. Filter by `level=error` to spot failures during stress/spike runs.
