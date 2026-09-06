# Score Following Model

A score follower consumes ordered timestamped observations and estimates a location on a canonical score timeline.

## Required output

A follower result must be representable as:

- score position,
- tempo/beat state when available,
- confidence/uncertainty,
- processing timestamp for latency measurement.

## Recovery is part of correctness

Followers will be evaluated on ordinary aligned playing and on loss-of-position cases: pause, restart, wrong/missing/extra notes, repeat, skip, backward jump, tempo drift and rubato.

## Parallel paths

Audio-feature following and transcription→symbolic following are both valid. Neither path is assumed superior before benchmark evidence.
