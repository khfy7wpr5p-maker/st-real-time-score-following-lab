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

## Fail-soft cases

Repository-owned deterministic research covers:

- clean duet with a stable 20 ms part offset;
- one dropped observation in part B;
- a pause in part B while part A continues;
- part B advancing/skipping score events while part A remains on its own path.

The design requirement is that disruption in one part must not overwrite or invalidate the other part's independent alignment result.

## Authority boundary

The report is marked `duet_research_not_ensemble_authority`.

SF-09 does not establish:

- quartet or orchestra behavior;
- source separation from a mono acoustic mixture;
- calibrated shared confidence;
- conductor intent;
- pedagogical grading.

Those require later independent evidence.
