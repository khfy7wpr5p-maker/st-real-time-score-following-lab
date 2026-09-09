# SF-09 Duet Research

## Goal

Establish a two-performer research boundary without collapsing two independent performance streams into one opaque follower.

## Part identity

`DuetPartInputV1` binds a stable `part_id`, `performer_id`, symbolic score-part reference and ordered `PerformanceEventV1` observation stream. A duet requires exactly two unique parts and two unique performer identities.

Each part is processed by its own `RecoveryAwareSymbolicFollower`. Single-performer contracts remain unchanged and continue to be the source of per-part alignment truth.

## Shared position

`DuetSharedPositionSnapshotV1` is a derived view, not a new score authority.

For every accepted part update:

1. keep the latest score position independently for each part;
2. mark a part stale when its latest update is older than the configured `stale_after_s`;
3. exclude stale or not-yet-seen parts from the shared position calculation;
4. take the median score beat of the remaining recent parts;
5. expose the score-position spread and classify the snapshot as `consensus`, `single_part`, or `divergent`.

This lets one performer continue to drive a usable research view when the other performer pauses or stops producing observations. The stale performer remains explicit in the snapshot and is not silently deleted.

Shared snapshot confidence is unavailable in this stage. Per-part scalar recovery confidence is not combined into a fabricated ensemble confidence.

## Inter-part asynchrony

`DuetAsynchronyPointV1` pairs occurrences of the same aligned score beat across both parts and records signed/absolute onset-time differences. Summary metrics include mean, median, P95 and maximum absolute asynchrony.

Asynchrony is a timing fact, not a quality grade. Large values after a pause or deliberate divergence are not automatically interpreted as mistakes.

## Repository-owned evidence

Implementation head CI `34394175788` passed all 7 jobs on `fa53b42c4f0826c2599ea2a99d39813f42eb1dd4` before the documentation-only closeout commit.

Deterministic cases:

- **clean**: both parts match 8/8 events and end at score beat 7.0; 8 common asynchrony points; mean/max absolute asynchrony about 20 ms; 15 consensus, 1 single-part, 0 divergent snapshots.
- **drop_one_event**: part A remains 8/8; part B matches 7 events and exposes one forward-skipped score event; both end at beat 7.0; 7 common asynchrony points; mean/max about 20 ms; 13 consensus, 2 single-part, 0 divergent snapshots.
- **pause_one_performer**: both parts still match all 8 events and end at beat 7.0; part B exposes one pause gap. Shared state records 6 consensus, 6 single-part and 4 divergent snapshots; maximum position spread is 4 beats; mean absolute asynchrony 957.5 ms and max 1520 ms.
- **advance_one_performer**: part A remains 8/8; part B matches 6 observations and exposes 2 forward-skipped score events; both end at beat 7.0. Shared state records 9 consensus, 2 single-part and 3 divergent snapshots; maximum spread 2 beats; mean absolute asynchrony 500 ms and max 980 ms.

The clean case can momentarily show a one-beat spread because snapshots are emitted at individual part-event arrival times; it remains within the configured consensus semantics and is not counted as divergence.

## Fail-soft conclusion

The deterministic evidence supports the intended architecture boundary:

- disruption in one performer/part does not overwrite the other part's independent recovery result;
- a stale performer can be excluded from the shared-position calculation while remaining visible in snapshot state;
- a dropped observation is surfaced as recovery evidence rather than silently corrupting the unaffected part;
- larger score-position disagreement is exposed as `divergent` rather than forced into false consensus;
- shared confidence remains unavailable.

These are repository-owned symbolic fixtures, not real acoustic duet-performance claims.

## Authority boundary

The report is marked `duet_research_not_ensemble_authority`.

SF-09 does not establish:

- quartet or orchestra behavior;
- source separation from a mono acoustic mixture;
- calibrated shared confidence;
- conductor intent;
- pedagogical grading.

Those require later independent evidence.

Permanent benchmark evidence: `benchmarks/reports/SF09_DUET_RESEARCH.md`.
