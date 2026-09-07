# SF-07 Performance Alignment

## Goal

Turn follower alignment paths into stable post-performance records suitable for rehearsal review, later pedagogy/error intelligence, and portable JSON/CSV export.

## Why a separate schema

The existing realtime `AlignmentV1` requires confidence. Some current followers do not expose calibrated confidence. SF-07 therefore uses a separate post-performance export schema where confidence is optional and provenance remains explicit. Missing confidence is preserved as missing rather than replaced with a numeric guess.

## Time model

For a reference BPM, each score beat maps to canonical score time. Every alignment point records:
- score beat and canonical score time;
- absolute performance time;
- absolute performance-minus-score offset;
- segment-relative timing deviation;
- early/on-time/late class;
- local tempo when the preceding point belongs to the same valid forward-moving segment;
- optional confidence and its original provenance.

Segment-relative deviation re-anchors at each discontinuity. This prevents a repeated or restarted section from being mislabeled as uniformly late only because it occurs later on the global performance timeline.

## Segmentation

A new segment starts when:
1. score position does not move forward, covering repeat/backward/restart-like discontinuities; or
2. the performance-time gap reaches the configured pause threshold.

Local tempo is never computed across a segment boundary. This avoids negative BPM on backward jumps and artificial extremely slow BPM across pauses.

## Summary metrics

Reports include:
- point and segment counts;
- mean, median, and P95 absolute segment-relative deviation;
- early/on-time/late counts at an explicit tolerance;
- local-tempo sample count and mean/median/min/max;
- score-discontinuity and performance-gap boundary counts.

## Export

`PerformanceAlignmentReportV1.to_json()` emits schema-versioned structured output with provenance. `to_csv()` emits one row per alignment point and leaves unavailable confidence fields blank.

## Interpretation boundary

SF-07 is a post-performance analysis/export layer. It does not infer pitch mistakes, articulation quality, dynamics, or musical intent. Local tempo is an interval estimate between adjacent aligned score beats, not a hidden ground-truth conductor tempo. Score-time conversion assumes the supplied score beat and reference BPM use the same beat unit.
