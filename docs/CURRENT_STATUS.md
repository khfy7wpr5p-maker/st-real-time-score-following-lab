# Current Status

Date: 2026-09-07

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime evidence**.
- SF-03 Symbolic Following Path: **complete; audio-vs-oracle-symbolic comparison + permanent evidence**.
- SF-04 Solo Violin: **active; autonomous STRAdi interface/preflight implemented, real model/data evidence gated by asset/audio usage confirmation**.
- SF-05 Classical Guitar: **complete for repository-owned structural synthetic evidence; real-corpus validation remains rights-gated**.
- SF-06 Robustness and Recovery: **next active autonomous stage**.

## SF-04 narrow gate

- STRAdi-style CSV output is adapted into ST contracts without importing the legacy PyTorch stack into core.
- Missing external confidence remains explicitly unavailable rather than fabricated.
- No checkpoint or KRAISLER audio is materialized while applicable asset/audio terms remain unconfirmed.

SF-04 is not globally blocking the roadmap; only its real violin evidence exit is gated.

## SF-05 evidence

The repository-owned classical-guitar fixture exercises 16 onset positions with 4 chord onsets, 12 arpeggio onsets under sustained whole-measure bass, and explicit voice overlap.

Clean CI `34087889237` passed Python 3.11/3.12 Ruff + pytest, Matchmaker integrations, and all benchmark steps.

On the deterministic synthetic fixture:
- Matchmaker Arzt/chroma: 16/16 expected events, 0 ms mean/P95 onset error.
- Matchmaker Arzt/CQT: 16/16 expected events, 0 ms mean/P95 onset error.
- ST synthetic-oracle symbolic path: 16/16 expected events, 0 ms mean/P95 onset error.

These results establish structural pipeline behavior only. They do not establish real nylon-string timbre robustness, real performer generalization or AMT accuracy.

See `benchmarks/reports/SF05_CLASSICAL_GUITAR_SYNTHETIC.md`, `docs/SF05_CLASSICAL_GUITAR.md`, and `datasets/manifests/guitarset_research_candidate.json`.

## Current autonomous direction

Proceed to SF-06 robustness/recovery with repository-owned perturbation scenarios: wrong/missing/extra notes, pause, restart, repeat, skip, backward jump, tempo change and rubato. Keep fail-soft behavior and recovery metrics explicit.
