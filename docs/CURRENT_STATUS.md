# Current Status

Date: 2026-09-07

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime evidence**.
- SF-03 Symbolic Following Path: **complete; audio-vs-oracle-symbolic comparison + permanent evidence**.
- SF-04 Solo Violin: **active external-evidence gate; autonomous STRAdi interface/preflight implemented, real model/data evidence gated by asset/audio usage confirmation**.
- SF-05 Classical Guitar: **complete for repository-owned structural synthetic evidence; real-corpus validation remains rights-gated**.
- SF-06 Robustness and Recovery: **complete for repository-owned deterministic symbolic recovery evidence**.
- SF-07 Performance Alignment: **complete for repository-owned deterministic post-performance analysis/export evidence**.
- SF-08 Performance Error Intelligence Foundation: **next active autonomous stage**.

## SF-04 narrow gate

- STRAdi-style CSV output is adapted into ST contracts without importing the legacy PyTorch stack into core.
- Missing external confidence remains explicitly unavailable rather than fabricated.
- No checkpoint or KRAISLER audio is materialized while applicable asset/audio terms remain unconfirmed.

SF-04 is not globally blocking the roadmap; only its real violin evidence exit is gated.

## SF-05 evidence

The repository-owned classical-guitar fixture exercises 16 onset positions with 4 chord onsets, 12 arpeggio onsets under sustained whole-measure bass, and explicit voice overlap.

Final SF-05 CI `34088140925` passed Python 3.11/3.12 Ruff + pytest, Matchmaker integrations, and all benchmark steps.

On the deterministic synthetic fixture:
- Matchmaker Arzt/chroma: 16/16 expected events, 0 ms mean/P95 onset error.
- Matchmaker Arzt/CQT: 16/16 expected events, 0 ms mean/P95 onset error.
- ST synthetic-oracle symbolic path: 16/16 expected events, 0 ms mean/P95 onset error.

These results establish structural pipeline behavior only. They do not establish real nylon-string timbre robustness, real performer generalization, or AMT accuracy.

## SF-06 evidence

`RecoveryAwareSymbolicFollower` is a separate recovery backend with bounded forward/backward search and explicit global re-lock only for initial acquisition, long gaps, or configured mismatch recovery.

The repository-owned suite contains clean control plus wrong note, missing note, extra note, pause, restart, repeat, skip, backward jump, tempo change, and rubato.

Evidence:
- 11/11 scenarios passed.
- 188/188 valid event-to-score mappings correct.
- 2/2 injected noise observations rejected.
- one explicit global restart re-lock.
- maximum declared re-lock: 2.0 s / 2 observations across aggregate dimensions; the 2.0 s is injected pause silence, not CPU latency.
- every accepted match exposes an audit record; confidence is propagated only when available and never fabricated.

See `benchmarks/reports/SF06_ROBUSTNESS_RECOVERY.md` and `docs/SF06_ROBUSTNESS_RECOVERY.md`.

## SF-07 evidence

SF-07 adds ST-owned post-performance alignment records with explicit provenance and optional confidence, plus stable JSON/CSV export.

Final implementation CI `34103541246` passed Python 3.11/3.12 Ruff + full pytest, the independent performance-alignment benchmark, SF-06 recovery regression, and the full Matchmaker/SF-01/SF-02/SF-03/SF-05 regression chain.

Repository-owned benchmark evidence at 120 BPM / 40 ms timing tolerance:
- clean: 8 points, 1 segment, 8/8 on-time, 7 local-tempo samples at 120 BPM;
- expressive: 6 points, 1 early / 3 on-time / 2 late, mean absolute segment deviation 36.667 ms, P95 90 ms, local-tempo range about 98.361–146.341 BPM;
- pause: 5 points, 2 segments, one explicit performance-gap boundary, no tempo estimate across the pause;
- backward jump: 6 points, 2 segments, one explicit score-discontinuity boundary, no negative/cross-boundary tempo.

Missing confidence remains null/blank in exports rather than being fabricated. These are deterministic post-processing fixtures and are not real musician performance-quality claims.

See `benchmarks/reports/SF07_PERFORMANCE_ALIGNMENT.md` and `docs/SF07_PERFORMANCE_ALIGNMENT.md`.

## Current autonomous direction

Proceed to SF-08 Performance Error Intelligence Foundation. Build on SF-07 records to define evidence-backed, non-authoritative error/deviation events and aggregation contracts while preserving confidence provenance, abstention, auditability, and the boundary between measured performance facts and pedagogical interpretation.
