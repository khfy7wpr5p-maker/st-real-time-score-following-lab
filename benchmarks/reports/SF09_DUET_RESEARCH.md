# SF-09 Duet Research Evidence

Date: 2026-09-09

## Scope

This report records repository-owned deterministic evidence for two independent symbolic performer/part streams. It validates architecture and fail-soft semantics only. It is not real acoustic duet validation and not ensemble/orchestra authority.

Authority boundary: `duet_research_not_ensemble_authority`.

## Validation

Implementation head: `fa53b42c4f0826c2599ea2a99d39813f42eb1dd4`.

GitHub Actions CI `34394175788` passed all 7 jobs:

- Python 3.11: Ruff + full pytest — success;
- Python 3.12: Ruff + full pytest — success;
- duet-research benchmark — success;
- robustness/recovery benchmark — success;
- performance-alignment benchmark — success;
- error-intelligence benchmark — success;
- Matchmaker integrations and SF-01/SF-02/SF-03/SF-05 regression benchmarks — success.

The earlier CI `34106708210` already showed the duet runtime benchmark passing; its core matrix failure was limited to import-block formatting in two newly added files. Commit `fa53b42c4f0826c2599ea2a99d39813f42eb1dd4` fixed only that lint formatting and CI `34394175788` then passed fully.

## Invariants under test

1. Each performer/part is followed independently.
2. Shared position is a derived median view, not score authority.
3. Stale parts are excluded from the shared calculation rather than blocking another active part.
4. Divergence is exposed as position spread/status instead of silently forcing consensus.
5. Shared confidence remains unavailable rather than fabricated.
6. Duet evidence is not generalized to quartet or orchestra behavior.

## Deterministic cases

### Clean

- part A: 8 matched events, final score beat 7.0, 0 forward skips, 0 pause gaps, 0 unmatched observations;
- part B: 8 matched events, final score beat 7.0, 0 forward skips, 0 pause gaps, 0 unmatched observations;
- common asynchrony points: 8;
- mean absolute asynchrony: ~20 ms;
- maximum absolute asynchrony: ~20 ms;
- snapshots: 16 total = 15 consensus + 1 single-part + 0 divergent;
- maximum observed position spread: 1 beat.

The transient 1-beat spread comes from per-event arrival ordering and remains inside consensus semantics; it is not counted as divergence.

### One dropped event in part B

- part A: 8 matched events, final score beat 7.0;
- part B: 7 matched events, final score beat 7.0, 1 forward-skipped score event;
- common asynchrony points: 7;
- mean/max absolute asynchrony: ~20 ms;
- snapshots: 15 total = 13 consensus + 2 single-part + 0 divergent;
- maximum position spread: 1 beat.

The unaffected part keeps its complete alignment while the affected part exposes the skip explicitly.

### Pause in part B

- part A: 8 matched events, final beat 7.0, 0 pause gaps;
- part B: 8 matched events, final beat 7.0, 1 pause gap;
- common asynchrony points: 8;
- mean absolute asynchrony: 957.5 ms;
- median absolute asynchrony: ~1520 ms;
- P95/max absolute asynchrony: 1520 ms;
- snapshots: 16 total = 6 consensus + 6 single-part + 4 divergent;
- maximum position spread: 4 beats.

Large asynchrony after the injected pause is a timeline fact, not CPU latency and not a performance-quality grade. Single-part snapshots demonstrate that one active part can continue to provide a derived position while the other is stale.

### Part B advances/skips

- part A: 8 matched events, final beat 7.0;
- part B: 6 matched events, final beat 7.0, 2 forward-skipped score events;
- common asynchrony points: 6;
- mean absolute asynchrony: 500 ms;
- median absolute asynchrony: 500 ms;
- P95/max absolute asynchrony: 980 ms;
- snapshots: 14 total = 9 consensus + 2 single-part + 3 divergent;
- maximum position spread: 2 beats.

The shared view exposes disagreement as divergence while both independent part results remain available.

## Confidence and interpretation

`shared_confidence_available` is false in every case. SF-09 does not combine unrelated per-part recovery scalars into an ensemble confidence.

Asynchrony, forward skips, stale states and position spread are research evidence. They are not automatically labeled as wrong notes, poor ensemble playing, conductor disagreement, or pedagogical grades.

## Exit assessment

SF-09 passes the repository-owned deterministic exit for:

- independent two-part tracking;
- derived shared-position semantics;
- stale-part fail-soft behavior;
- explicit divergence;
- inter-part asynchrony measurement;
- preservation of unavailable shared confidence;
- prior-stage regression safety.

SF-10 must independently earn N-part/quartet evidence. Mono acoustic mixture separation, real-room recordings, quartet/orchestra generalization and calibrated ensemble confidence remain outside this result.
