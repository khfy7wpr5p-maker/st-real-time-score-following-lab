# SF-08 Performance Error Intelligence Foundation

## Goal

Convert already-supported alignment and recovery evidence into auditable performance-deviation events without turning research heuristics into a grading or pedagogical authority.

## Authority boundary

SF-08 separates three things:

1. **Observed/aligned facts** such as performance time, score position, segment boundaries and recovery audit counts.
2. **Derived evidence events** such as early/late timing, skipped score regions, unmatched observations and discontinuities.
3. **Unsupported interpretations** such as "wrong note", "extra note", articulation quality, dynamics quality, musical intent or a student grade.

The third category must abstain unless a later subsystem supplies sufficient evidence under its own contract.

## Evidence kinds

The initial ST-owned evidence taxonomy is:

- `timing_early`
- `timing_late`
- `unmatched_observation`
- `skipped_score_region`
- `score_discontinuity`
- `performance_gap`

No severity score is assigned. Counts and measured magnitudes are reported instead.

## Confidence

Confidence is optional and keeps its original `ConfidenceV1` provenance when it already exists on an SF-07 alignment point. A scalar recovery confidence value is not promoted into a new `ConfidenceV1` because its source/calibration provenance would be incomplete.

Missing confidence remains missing.

## Unmatched observations

An unmatched recovery observation is evidence that the recovery follower did not associate an observation with a score event. It is **not** sufficient to distinguish:

- a wrong played note,
- an extra note,
- an ornament,
- an upstream transcription error,
- or another unsupported cause.

SF-08 therefore emits `unmatched_observation` and an explicit `unmatched_observation_semantics` abstention.

## Skipped score regions

A `forward_skip` recovery audit transition can support a derived skipped-score-region event. SF-08 records the skipped score-index interval and count. It does not claim why the region was skipped.

## Timing and discontinuities

SF-07 remains the authority for segment-aware timing facts. SF-08 consumes those records and emits:

- `timing_early` / `timing_late` only when SF-07 classified the point outside its explicit tolerance;
- `performance_gap` for SF-07 pause boundaries;
- `score_discontinuity` for repeats/backward/restart-like non-forward score movement.

Segment re-anchoring remains in SF-07; SF-08 does not recompute cross-boundary tempo.

## Abstentions

The initial foundation always keeps unsupported domains explicit:

- pitch-error identity for the complete performance,
- articulation,
- dynamics,
- musical intent,
- pedagogical grade.

When unmatched observations exist, unmatched-observation semantics is added as an additional abstention.

## Export and aggregation

`PerformanceErrorIntelligenceReportV1` provides:

- schema-versioned JSON;
- row-oriented CSV for evidence events;
- counts by evidence kind;
- timing-event mean/max absolute deviation;
- confidence availability counts;
- unmatched-observation count;
- skipped-score-event count;
- discontinuity/gap event counts;
- explicit abstention records;
- a fixed authority boundary: `research_evidence_not_pedagogical_authority`.

This layer is designed for rehearsal review, debugging and later research. It is not a student-scoring API.
