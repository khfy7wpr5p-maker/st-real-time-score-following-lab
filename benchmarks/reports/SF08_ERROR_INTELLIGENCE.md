# SF-08 Performance Error Intelligence Evidence

Date: 2026-09-07

## Scope

SF-08 converts evidence already supported by SF-06 recovery audit records and SF-07 post-performance alignment into auditable performance-deviation events. It does not infer unsupported causes, assign severity scores, grade students, or act as pedagogical authority.

## Contracts and taxonomy

The ST-owned foundation adds:

- `PerformanceEvidenceEventV1`;
- `EvidenceAbstentionV1`;
- `PerformanceErrorIntelligenceSummaryV1`;
- `PerformanceErrorIntelligenceReportV1`;
- `EvidenceKind` for timing early/late, unmatched observations, skipped score regions, score discontinuities and performance gaps;
- `AbstentionKind` for unsupported pitch-error identity, unmatched-observation semantics, articulation, dynamics, musical intent and pedagogical grading;
- stable JSON/CSV export;
- fixed authority boundary `research_evidence_not_pedagogical_authority`.

## Event-level auditability hardening

When the original `PerformanceEventV1` observation stream is available and the recovery run has no confidence-based rejections, SF-08 reconciles recovery match event IDs against the source observation IDs. This allows unmatched observations to retain their source event ID, timestamp and original confidence provenance.

If event identity cannot be reconciled safely, SF-08 falls back to aggregate unmatched evidence instead of guessing.

An unmatched observation remains an `unmatched_observation`; it is not promoted to `wrong_note` or `extra_note` because the current evidence cannot distinguish performance error, ornament, transcription error or another cause.

## Validation

Hardened implementation head `27beecccb8f99256c929ffad79527db0c706867a` was validated by GitHub Actions CI run `34105618113`:

- Python 3.11 Ruff + full pytest: success;
- Python 3.12 Ruff + full pytest: success;
- SF-06 robustness/recovery benchmark: success;
- SF-07 performance-alignment benchmark: success;
- SF-08 error-intelligence benchmark: success;
- Matchmaker integrations and SF-01/SF-02/SF-03/SF-05 benchmark regression chain: success.

All 6 CI jobs passed.

## Repository-owned deterministic benchmark

Fixture:

- 6 score events;
- 6 performance observations;
- 5 accepted alignment points;
- reference tempo 120 BPM;
- timing tolerance 40 ms.

Recovery evidence:

- 5 matched events;
- 1 unmatched observation;
- 1 forward-skipped score event;
- 1 backward jump;
- 1 pause gap.

SF-08 output contains 5 evidence events:

1. `timing_late`: 1 event, about 80 ms segment-relative deviation;
2. `performance_gap`: 1 event;
3. `score_discontinuity`: 1 event;
4. `unmatched_observation`: 1 event, reconciled to source event `event-unmatched` at 0.25 s;
5. `skipped_score_region`: 1 event covering one skipped score event.

Confidence evidence:

- 2 evidence events retain explicit source confidence provenance;
- 3 evidence events have confidence unavailable;
- no unavailable confidence is fabricated;
- naked recovery scalar confidence is not converted into a new calibrated `ConfidenceV1`.

Timing summary:

- 1 timing event;
- mean absolute timing deviation: about 80 ms;
- max absolute timing deviation: about 80 ms.

## Abstention evidence

The benchmark emits 6 explicit abstentions:

- `pitch_error_identity`;
- `articulation`;
- `dynamics`;
- `musical_intent`;
- `pedagogical_grade`;
- `unmatched_observation_semantics`.

The report contains no grade, severity score or student-performance authority field.

## Export evidence

The benchmark emits schema-versioned JSON plus row-oriented CSV. The captured deterministic run produced 5 evidence rows plus the CSV header. Missing confidence remains blank in CSV and null in structured output.

## Interpretation boundaries

- This is deterministic repository-owned research evidence, not real-student validation.
- Timing classification inherits the explicit SF-07 tolerance and segmentation semantics.
- Recovery evidence identifies alignment behavior, not the musical cause of that behavior.
- Pitch correctness, articulation, dynamics and musical intent require independent future evidence contracts.
- SF-08 is not a grading engine.

## Exit decision

SF-08 exit criteria are satisfied for the evidence-first error-intelligence foundation. The roadmap can advance autonomously to SF-09 Duet Research while SF-04 real violin evidence remains a separate narrow rights gate.
