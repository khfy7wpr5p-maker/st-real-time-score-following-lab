# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **complete; real `pymatchmaker==0.3.0` CI integration and benchmark green**.
- SF-02 Realtime Microphone and Streaming Pipeline: **next; streaming foundation research prepared**.

## Implemented

- Python package bootstrap and canonical v1 score/observation/tempo/confidence/alignment contracts.
- Stream-relative monotonic clock and latency primitive.
- Ruff + pytest CI on Python 3.11 and 3.12.
- ST-owned follower adapter boundary.
- Version-pinned `pymatchmaker==0.3.0` adapter with lazy optional dependency loading.
- Matchmaker online score-beat update normalization and final score-beat/performance-time path normalization.
- Adapter compatibility for both documented array-like `(2, T)` and observed PyPI-wheel pair-list `(T, 2)` alignment representations.
- Synthetic 16-quarter-note MusicXML/MIDI baseline fixture generated without private or third-party data.
- Baseline alignment metrics and dedicated Matchmaker CI job.
- Permanent SF-01 evidence report under `benchmarks/reports/`.

## SF-01 evidence

Successful GitHub Actions run: `34055613788`, Matchmaker job `101546846848`.

- 16 online updates and 16 final alignment points.
- 16/16 expected synthetic events evaluated; 0 failed events.
- Median/mean/P95 absolute alignment error: 0.0 ms on this exact deterministic synthetic fixture.
- 100% within 50/100/250/500 ms.
- Wall duration: approximately 0.0136 s for an 8.0 s represented performance; reported realtime factor approximately 0.00170.
- Matchmaker high-level updates expose no calibrated confidence, so confidence remains explicitly unavailable.

These numbers are smoke/reproducibility evidence only. They are not representative real-piano, microphone, expressive-performance, polyphonic, rubato or recovery results.

## Known backend observations

The installed Matchmaker 0.3.0 wheel returned the final alignment as a sequence of `(score_beat, performance_time_s)` pairs despite upstream source documentation describing a `(2, T)` array-like path. The ST adapter accepts both forms and regression tests preserve this boundary.

The successful CI run also emitted non-fatal Partitura/HiddenMarkov warnings. They are recorded in the SF-01 evidence report rather than hidden.

## Next safe action

Begin SF-02 with an ST-owned bounded ingestion queue, explicit overflow behavior and monotonic arrival timestamps. Use synthetic MIDI/byte streams first, then bridge to Matchmaker byte-stream adapters without treating backend `time.time()` values as the canonical ST latency clock. Microphone-device testing can remain optional while the architecture and synthetic streaming path progress.
