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

## Deterministic cases

Repository-owned SF-10 validation covers:

- clean quartet with stable per-channel offsets;
- one dropped event in part D;
- one paused performer while the other three channels continue;
- part D advancing/skipping two score events while other parts remain on their own paths;
- two-channel loss, leaving only two active parts and therefore deliberately dropping below the default 3-of-4 quorum.

## Authority boundary

The report is marked `quartet_multichannel_research_not_mixed_ensemble_authority`.

SF-10 does not establish:

- source separation from a mono microphone mixture;
- real-room quartet generalization;
- mixed-instrument ensemble behavior;
- orchestra/global conductor behavior;
- calibrated ensemble confidence;
- pedagogical grading.

Those require later independent evidence.
