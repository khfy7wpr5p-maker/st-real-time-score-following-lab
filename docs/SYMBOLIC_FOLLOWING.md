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

SF-03 is complete for the repository-owned synthetic comparison scope. Final CI run `34058190673` passed Python 3.11/3.12, all Matchmaker integration tests, and `run_symbolic_comparison.py`.

The direct audio path and oracle transcription -> symbolic path were evaluated on the same 16-event material with the same expected-onset metrics. Exact metrics, conditions and limitations are preserved in `benchmarks/reports/SF03_SYMBOLIC_COMPARISON.md`.

Real AMT accuracy, transcription latency and instrument robustness remain future evidence requirements.
