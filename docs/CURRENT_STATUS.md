# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent benchmark evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime streaming evidence; physical microphone validation remains environment-specific**.
- SF-03 Symbolic Following Path: **complete; same-material audio-vs-oracle-symbolic comparison is CI-green with permanent evidence**.
- SF-04 Solo Violin: **next; instrument evidence and dataset/license requirements must be audited before materialization**.

## SF-03 completed scope

- Backend-neutral `TranscriptionAdapter` / `TranscriptionRunResult` boundary using existing `PerformanceEventV1` contracts.
- Forward-only `CausalSymbolicFollower` with bounded lookahead, explicit unmatched/skip counters and optional confidence rejection.
- Confidence provenance is propagated from transcription events; follower confidence is not fabricated.
- Repository-owned benchmark-only oracle transcription fixture.
- Same-material comparison: Matchmaker audio-only versus oracle transcription -> symbolic following using common expected-onset metrics.
- Regression tests for complete following, unmatched observations, missing-event recovery and confidence filtering.
- SF-02 public latency exports were regression-checked and preserved during SF-03 integration.

## SF-03 evidence

Final CI run `34058190673` is green on Python 3.11/3.12 plus Matchmaker integration/benchmarks.

On the shared 16-event synthetic fixture:

- audio-only Matchmaker `arzt`: mean absolute error 20.833 ms, median 0 ms, P95 333.333 ms, 93.75% within 50/100/250 ms, 100% within 500 ms;
- oracle transcription -> ST symbolic follower: 16/16 matched, 0 failures, 0 ms mean/median/P95 error.

The symbolic result is an oracle architecture upper bound, not an AMT-model result. Exact evidence and limitations are in `benchmarks/reports/SF03_SYMBOLIC_COMPARISON.md`.

## Next safe action

Audit SF-04 Solo Violin against `DATASET_GOVERNANCE.md`: identify what can be validated with repository-owned/synthetic material and isolate any licensed external-data requirement as a narrow human gate. Do not substitute synthetic piano evidence for real violin robustness.
