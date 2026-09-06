# SF-01 Matchmaker Synthetic MIDI Baseline Evidence

Date: 2026-09-06

## Purpose

This report records the first reproducible external-backend score-following baseline for ST Real-Time Score Following Lab. It is a smoke/reproducibility result, not a claim about representative real-piano accuracy.

## Environment

- Backend: `pymatchmaker==0.3.0`
- Method: `pthmm`
- Input: synthetic MIDI
- Score: repository-owned synthetic MusicXML
- Fixture: `synthetic_piano_quarter_notes_v1`
- Notes/events: 16 quarter notes
- Performance duration represented by fixture: 8.0 s
- CI runner: Linux / GitHub Actions
- Python: 3.12.14
- CI run: `34055613788`
- Matchmaker job: `101546846848`

## Result

| Metric | Result |
|---|---:|
| Online updates | 16 |
| Final alignment points | 16 |
| Evaluated events | 16 |
| Failed events | 0 |
| Failure rate | 0.0 |
| Median absolute error | 0.0 ms |
| Mean absolute error | 0.0 ms |
| P95 absolute error | 0.0 ms |
| Within 50 ms | 100% |
| Within 100 ms | 100% |
| Within 250 ms | 100% |
| Within 500 ms | 100% |
| Wall duration | 0.01363167 s |
| Backend alignment duration | 0.00177312 s |
| Realtime factor | 0.00170396 |
| Calibrated confidence exposed | No |

## Interpretation

The clean synthetic sequence is intentionally trivial and exactly aligned. A 0 ms result therefore proves only that the adapter, synthetic fixture, Matchmaker backend and evaluation path agree on this deterministic case. It must not be generalized to real microphone audio, expressive piano, polyphony, rubato, recovery, noisy input or instrument-specific performance.

## Adapter evidence

The evaluated Matchmaker 0.3.0 source documentation describes the returned final alignment as an array-like `(2, T)` path. The installed PyPI wheel in CI returned a sequence of `(score_beat, performance_time_s)` pairs instead. The ST adapter now normalizes both forms. This is retained as evidence for keeping third-party follower behavior behind an ST-owned adapter boundary.

Matchmaker's high-level yielded score-position updates do not expose a calibrated confidence value. ST therefore records confidence as unavailable rather than fabricating one.

## Warnings observed

The successful CI run emitted non-fatal warnings from Partitura/HiddenMarkov, including a MusicXML metronome-direction parsing warning and a divide-by-zero warning while constructing log transition probabilities. They did not prevent the baseline from completing, but should remain visible in future backend upgrades/regressions.

## SF-01 conclusion

SF-01 exit criterion is satisfied: a reproducible offline/streaming-style Matchmaker baseline exists, is exercised by CI, and has an evidence report. The next safe stage is SF-02 realtime streaming foundation with bounded ingestion, monotonic ST timing and synthetic byte/MIDI streams before microphone hardware is required.
