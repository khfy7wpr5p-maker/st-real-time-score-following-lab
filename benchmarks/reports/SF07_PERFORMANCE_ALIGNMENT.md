# SF-07 Performance Alignment Evidence

Date: 2026-09-07

## Scope

SF-07 converts an already-produced follower alignment path into stable post-performance rehearsal-review records. It does not replace the realtime follower and does not invent missing confidence.

## Implementation

The stage adds:
- `AlignmentProvenanceV1` for backend/method/input provenance;
- `PerformanceAlignmentPointV1` with score beat/time, performance time, absolute and segment-relative deviation, timing class, local tempo, boundary reason and optional confidence;
- `PerformanceAlignmentSummaryV1` for timing and tempo summaries;
- `PerformanceAlignmentReportV1` with schema-versioned JSON and CSV export;
- segment boundaries for non-forward score movement and long performance gaps;
- local-tempo calculation only inside valid forward-moving segments.

## Validation

Implementation head `d0a8be24f0a057642695c0d69ab63038e2f66957` was validated by GitHub Actions CI run `34103541246`:
- Python 3.11 Ruff + full pytest: success;
- Python 3.12 Ruff + full pytest: success;
- independent performance-alignment benchmark: success;
- SF-06 robustness/recovery regression: success;
- Matchmaker integration and SF-01/SF-02/SF-03/SF-05 benchmark regression chain: success.

The first CI attempt exposed one Ruff-only line-length error in a test. The implementation benchmark itself passed. The formatting error was fixed without changing alignment behavior, then the full matrix passed.

## Repository-owned benchmark evidence

Reference tempo: 120 BPM. Timing-class tolerance: 40 ms.

### Clean case
- 8 alignment points;
- 1 segment;
- 8 on-time, 0 early, 0 late;
- 7 local-tempo samples;
- mean/min/max local tempo: 120 BPM;
- mean/median/P95 absolute segment-relative deviation: 0 ms.

### Expressive case
- 6 alignment points;
- 1 segment;
- 1 early, 3 on-time, 2 late;
- mean absolute segment-relative deviation: 36.667 ms;
- median: 35 ms;
- P95: 90 ms;
- 5 local-tempo samples;
- local tempo range: about 98.361 to 146.341 BPM;
- mean local tempo: about 123.851 BPM.

### Pause case
- 5 alignment points;
- 2 segments;
- 1 explicit `performance_gap` boundary;
- no local-tempo sample is computed across the pause;
- remaining local-tempo samples are 120 BPM;
- all 5 points are on-time after segment re-anchoring.

### Backward-jump case
- 6 alignment points;
- 2 segments;
- 1 explicit `score_discontinuity` boundary;
- no negative or cross-discontinuity tempo is emitted;
- 4 valid local-tempo samples, all 120 BPM;
- all 6 points are on-time after segment re-anchoring.

## Export evidence

The benchmark emits schema-versioned JSON and row-oriented CSV. Missing confidence remains `null` in JSON and blank in CSV; no confidence value is synthesized.

## Interpretation boundaries

- These are deterministic repository-owned post-processing fixtures, not real musician quality evidence.
- Local tempo is an interval estimate between adjacent aligned score beats, not conductor ground truth.
- Segment-relative deviation intentionally re-anchors after pauses/repeats/backward jumps so global elapsed time does not falsely label a restarted section as late.
- `score_time_s` assumes the supplied score-beat unit is compatible with the reference BPM beat unit.
- SF-07 does not detect pitch, articulation, dynamics or musical-intent errors. Those belong to later error-intelligence research.

## Exit decision

SF-07 exit criteria are satisfied for the repository-owned deterministic post-performance alignment/export scope. The roadmap can advance autonomously to SF-08 Performance Error Intelligence Foundation while SF-04 real violin evidence remains a separate narrow rights gate.
