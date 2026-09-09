# SF-10 Quartet / Multi-Channel Ensemble

## Goal

Extend the evidence earned by SF-09 to exactly four independent symbolic channels without claiming arbitrary ensemble, mixed-acoustic, or orchestra authority.

## Identity and channel boundary

`QuartetPartInputV1` binds stable `part_id`, `performer_id`, and `channel_id` values to one symbolic score part and one ordered `PerformanceEventV1` stream. `QuartetAnalyzer` requires exactly four unique parts, performers, and channels.

Each part is processed by its own `RecoveryAwareSymbolicFollower`. No shared ensemble state can overwrite a part's independent alignment result.

## Quorum-based shared position

The default shared-position quorum is 3 of 4 recent parts.

For each accepted part update:

1. retain the latest score position independently per part;
2. mark old positions stale using the configured clock threshold;
3. exclude stale/unseen parts from the shared calculation while keeping their IDs visible;
4. if fewer than 3 recent parts remain, emit `insufficient_quorum` with `shared_score_beat = null` and no spread;
5. otherwise derive the median recent score position and spread;
6. classify the snapshot as `full_consensus`, `quorum_consensus`, or `divergent`.

This is intentionally stricter than SF-09's single-part fail-soft view. In a four-channel research setting, loss of quorum must not fabricate a global position.

Shared confidence remains unavailable. Per-part recovery scalars are not combined into an ensemble confidence.

## Pairwise timing evidence

All six part pairs are compared on common aligned score beats. `QuartetPairwiseAsynchronyPointV1` stores signed and absolute onset-time differences. Aggregate mean, median, P95, maximum and point counts are evidence only, not quality grades.

## Repository-owned evidence

Implementation CI `34395555183` passed all 8 jobs on `aa972dce56f9bd1a315f2af3e6066731ffd80ea2`, including Python 3.11/3.12 Ruff + full pytest, quartet and duet benchmarks, SF-06/SF-07/SF-08 regressions, and the complete Matchmaker/SF-01/SF-02/SF-03/SF-05 chain.

Deterministic cases:

- **clean**: every part matched 8/8 and ended at beat 7; 48 pairwise timing points; mean absolute asynchrony 27.5 ms, maximum 50 ms; 29 full-consensus, 1 quorum-consensus, 0 divergent, and 2 bootstrap insufficient-quorum snapshots;
- **drop one event**: A/B/C remain 8/8; D matches 7 and exposes one forward skip; all end at beat 7; 0 divergent snapshots;
- **pause one performer**: all parts still match 8/8; C exposes one pause gap; 2 divergent and 2 true post-bootstrap degraded insufficient-quorum snapshots; maximum spread 3 beats;
- **advance one performer**: A/B/C remain 8/8; D matches 6 and exposes two forward skips; 12 divergent snapshots; maximum spread 2 beats;
- **two-channel loss**: A/B continue to beat 7 while C/D stop at beat 2; 8 true post-bootstrap insufficient-quorum snapshots publish no shared beat or spread.

Permanent benchmark evidence: `benchmarks/reports/SF10_QUARTET_MULTICHANNEL.md`.

## Fail-soft conclusion

The deterministic evidence supports the intended architecture boundary:

- one part's failure does not overwrite another part's recovery result;
- three recent channels can provide a quorum view while a fourth is stale;
- disagreement above the configured threshold is explicit divergence;
- two active channels do not satisfy the default quartet quorum, so global position becomes unavailable while those channels remain independently usable;
- shared confidence remains unavailable.

These are repository-owned symbolic fixtures, not real acoustic quartet-performance claims.

## Authority boundary

The report is marked `quartet_multichannel_research_not_mixed_ensemble_authority`.

SF-10 does not establish:

- source separation from a mono microphone mixture;
- real-room quartet generalization;
- arbitrary N-part ensemble scaling;
- mixed-instrument ensemble behavior;
- orchestra/global conductor behavior;
- calibrated ensemble confidence;
- pedagogical grading.

Those require later independent evidence.
