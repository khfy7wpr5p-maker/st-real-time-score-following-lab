# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime evidence**.
- SF-03 Symbolic Following Path: **complete; audio-vs-oracle-symbolic comparison + permanent evidence**.
- SF-04 Solo Violin: **active; autonomous STRAdi interface/preflight implemented, real model/data evidence gated by asset/audio usage confirmation**.

## SF-04 autonomous progress

- STRAdi-style CSV output adapter maps onset/offset/MIDI events into ST contracts without importing STRAdi/PyTorch into core.
- `PerformanceEventV1` now permits explicit unavailable confidence (`None`) rather than forcing a fabricated number.
- `CausalSymbolicFollower` propagates unavailable confidence and explicitly rejects it when a positive confidence threshold is configured.
- Repository-owned synthetic STRAdi-format fixture covers mapping, symbolic feed and irregular timing.
- Dataset candidate manifest records that no checkpoint or KRAISLER audio has been downloaded/copied.
- STRAdi source-code license is recorded as Apache-2.0; checkpoint asset terms and KRAISLER example-audio rights remain separate confirmation gates.

## Current boundary

SF-04 architecture work can continue without third-party data, but its final exit criterion requires reproducible violin evidence. Synthetic CSV evidence must not be presented as violin transcription accuracy.

See `docs/SF04_VIOLIN_PREFLIGHT.md` and `datasets/manifests/stradi_research_candidate.json`.
