# Symbolic Following Path

## Purpose

SF-03 tests a second path beside direct audio following:

`audio -> transcription backend -> PerformanceEventV1 -> causal symbolic follower -> score position`

The transcription backend is deliberately replaceable. `TranscriptionAdapter` returns `PerformanceEventV1` events, whose timestamps, pitches and `ConfidenceV1.source` preserve confidence provenance without making the score follower depend on a particular AMT model.

## Baseline follower

`CausalSymbolicFollower` is intentionally small and inspectable. It:

- consumes note/chord pitch events in arrival order;
- moves only forward through the symbolic score;
- uses bounded score-event lookahead;
- emits no position for unmatched observations;
- can explicitly reject observations below a configured confidence threshold;
- propagates transcription-event confidence instead of inventing follower confidence;
- records unmatched observations, skipped score events and low-confidence rejections.

It is a research baseline, not a production-grade polyphonic matcher.

## Oracle benchmark policy

The repository-owned synthetic oracle generator produces perfect `PerformanceEventV1` events for the same 16-note material used by the Matchmaker baseline. Its confidence source is explicitly `synthetic_oracle_ground_truth` and is marked uncalibrated because the value describes benchmark construction certainty, not an AMT probability.

Oracle results are an architecture upper bound only. They must not be reported as transcription-model performance.

## SF-03 exit evidence

The comparison benchmark must run both:

1. direct Matchmaker audio-only alignment; and
2. oracle transcription -> ST causal symbolic following,

on the same score material and evaluate both with the same expected-onset metrics. SF-03 remains active until this benchmark and the core tests are green in CI and the exact output is preserved under `benchmarks/reports/`.
