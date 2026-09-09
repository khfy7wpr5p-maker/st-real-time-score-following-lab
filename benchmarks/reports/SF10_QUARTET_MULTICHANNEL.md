# SF-10 Quartet / Multi-Channel Research Evidence

Date: 2026-09-09

## Scope

This report records repository-owned deterministic evidence for exactly four independent symbolic performer/part channels. It validates multi-channel architecture, quorum behavior and fail-soft semantics only. It is not mono-mixture source-separation evidence, real-room quartet validation, mixed-ensemble authority or orchestra authority.

Authority boundary: `quartet_multichannel_research_not_mixed_ensemble_authority`.

## Validation

Implementation head: `aa972dce56f9bd1a315f2af3e6066731ffd80ea2`.

GitHub Actions CI `34395555183` passed all 8 jobs:

- Python 3.11: Ruff + full pytest — success;
- Python 3.12: Ruff + full pytest — success;
- quartet-research benchmark — success;
- duet-research regression — success;
- robustness/recovery benchmark — success;
- performance-alignment benchmark — success;
- error-intelligence benchmark — success;
- Matchmaker integrations and SF-01/SF-02/SF-03/SF-05 regression benchmarks — success.

## Invariants under test

1. Exactly four unique part, performer and channel identities are retained.
2. Every part keeps its own `RecoveryAwareSymbolicFollower` result.
3. Shared position requires the configured 3-of-4 recent-part quorum.
4. Below quorum, `shared_score_beat` and spread remain unavailable rather than being fabricated from too few channels.
5. Divergence is exposed explicitly instead of being silently averaged into consensus.
6. All six part pairs contribute timing-asynchrony evidence where common aligned score beats exist.
7. Shared confidence remains unavailable rather than combining unrelated per-part recovery scalars.

## Deterministic cases

### Clean quartet

- all four parts: 8/8 matched events, final score beat 7.0;
- 48 pairwise asynchrony points across six part pairs;
- mean absolute pairwise asynchrony: 27.5 ms;
- median absolute pairwise asynchrony: 25 ms;
- P95 / maximum absolute pairwise asynchrony: 50 ms;
- snapshots: 32 total = 29 full-consensus + 1 quorum-consensus + 2 startup insufficient-quorum + 0 divergent;
- maximum position spread: 1 beat;
- maximum stale parts: 0.

The two insufficient-quorum snapshots are bootstrap snapshots before three channels have produced their first accepted positions. They are not channel-loss failures.

### One dropped event in part D

- parts A/B/C: 8/8 matched;
- part D: 7 matched, one explicit forward-skipped score event;
- all four final score positions reach beat 7.0;
- 45 pairwise asynchrony points;
- mean absolute asynchrony: about 27.22 ms; maximum: 50 ms;
- snapshots: 31 total = 25 full-consensus + 4 quorum-consensus + 2 startup insufficient-quorum + 0 divergent;
- maximum position spread: 1 beat.

The dropped event remains localized to part D and does not corrupt the other three independent part results.

### Pause in part C

- all four parts still match 8/8 events and finish at beat 7.0;
- part C exposes one pause gap;
- 48 pairwise asynchrony points;
- mean absolute asynchrony: 425 ms;
- median absolute asynchrony: 32.5 ms;
- P95 / maximum absolute asynchrony: about 1635 ms;
- snapshots: 32 total = 16 full-consensus + 10 quorum-consensus + 2 divergent + 4 insufficient-quorum;
- two of the insufficient-quorum snapshots are true post-bootstrap degraded states;
- maximum position spread: 3 beats.

Large timing deltas are injected timeline effects, not CPU latency and not a performance-quality grade.

### Part D advances/skips

- parts A/B/C: 8/8 matched;
- part D: 6 matched observations with two explicit forward-skipped score events;
- all four final score positions reach beat 7.0;
- 42 pairwise asynchrony points;
- mean absolute asynchrony: about 294.52 ms;
- median absolute asynchrony: 35 ms;
- P95 / maximum absolute asynchrony: about 985 ms;
- snapshots: 30 total = 12 full-consensus + 4 quorum-consensus + 12 divergent + 2 startup insufficient-quorum;
- maximum position spread: 2 beats.

The shared view exposes the disagreement through 12 divergent snapshots instead of forcing false consensus.

### Two-channel loss

- parts A/B continue 8/8 and finish at beat 7.0;
- parts C/D stop after 3 matched events and remain at beat 2.0;
- 23 pairwise asynchrony points remain available from overlapping evidence;
- maximum absolute asynchrony on those overlapping points: 50 ms;
- snapshots: 22 total = 11 full-consensus + 1 quorum-consensus + 10 insufficient-quorum + 0 divergent;
- 8 of the insufficient-quorum snapshots are true post-bootstrap degraded states after C and D become stale;
- maximum stale parts: 2.

For those degraded 2-of-4 states, the default 3-of-4 quorum is not met. The report deliberately publishes `shared_score_beat = null` and `spread_beats = null`. The two remaining independent part alignments continue, but no quartet-global position is invented.

## Confidence and interpretation

`shared_confidence_available` is false in every case. SF-10 does not combine per-part recovery scalars into an ensemble confidence.

Pairwise timing offsets, stale states, skips, quorum loss and score-position spread are research evidence. They are not automatically interpreted as ensemble quality, conductor disagreement, wrong-note identity or pedagogical grades.

## Exit assessment

SF-10 passes the repository-owned deterministic exit for:

- independent four-channel part following;
- stable part/performer/channel identity;
- explicit 3-of-4 quorum semantics;
- null shared position below quorum;
- full/quorum consensus and divergence states;
- six-pair timing evidence;
- fail-soft dropped-event, pause, advance and partial-channel-loss behavior;
- preservation of unavailable shared confidence;
- prior-stage regression safety.

SF-11 must independently earn mixed-ensemble evidence. Mono acoustic mixture separation, real-room recordings, arbitrary N-part scaling, conductor intent, orchestra generalization and calibrated ensemble confidence remain outside this result.
