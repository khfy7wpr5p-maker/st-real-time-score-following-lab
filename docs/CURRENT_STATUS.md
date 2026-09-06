# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent benchmark evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime streaming evidence; physical microphone validation remains environment-specific**.
- SF-03 Symbolic Following Path: **active; implementation added, comparison evidence pending CI**.

## SF-03 implemented scope

- Backend-neutral `TranscriptionAdapter` / `TranscriptionRunResult` boundary using existing `PerformanceEventV1` note-event contracts.
- Forward-only `CausalSymbolicFollower` with bounded lookahead, explicit unmatched/skip counters and optional confidence rejection.
- Confidence is propagated from transcription events; follower confidence is not fabricated.
- Repository-owned benchmark-only oracle transcription fixture.
- Same-material comparison benchmark: Matchmaker audio-only versus oracle transcription -> symbolic following using common expected-onset metrics.
- Regression tests for complete following, unmatched observations, missing-event recovery and confidence filtering.

## Evidence limits

- The oracle transcription path is an architecture upper bound, not an AMT model result.
- The audio comparison uses deterministic synthesized audio, not a musician or microphone.
- The first SF-03 implementation is monophonic/chord-pitch-event matching, not instrument-robust polyphonic transcription.
- SF-03 remains active until CI is green and exact comparison output is committed as permanent evidence.

## Next safe action

Run SF-03 CI. If core tests and the Matchmaker comparison benchmark are green, preserve exact metrics under `benchmarks/reports/`, update the roadmap/status, and close SF-03 without claiming real transcription quality.
