# Benchmarks

Benchmark definitions and lightweight reproducible runners live here. Large generated results should not be committed by default.

## SF-01 Matchmaker baseline

`run_matchmaker_baseline.py` creates a deterministic MIDI performance for the repository-owned
`tests/fixtures/synthetic_piano.musicxml` score, runs `pymatchmaker==0.3.0` with MIDI `pthmm`, and
prints a JSON report containing:

- backend/version/method,
- update and alignment-path counts,
- median/mean/p95 absolute onset alignment error,
- percentages within 50/100/250/500 ms,
- failure rate,
- wall runtime and realtime factor,
- explicit confidence availability and limitations.

This is a smoke/reproducibility baseline, not a claim of representative real-piano accuracy.

## SF-12 Orchestra global baseline

`run_orchestra_global.py` evaluates a repository-owned deterministic 32-point global score against aggregate pitch-class texture observations. Cases cover clean tracking, controlled dense-texture corruption, tempo/rubato timestamp variation, missing observations, forward skip, backward jump, and pause/restart.

The runner reports global score-position mapping error, explicit recovery transitions, and local Python matching CPU latency. Texture similarity is not calibrated confidence, and CPU matching latency is not end-to-end audio latency. The fixture does not establish real orchestral-audio performance or per-instrument transcription.
