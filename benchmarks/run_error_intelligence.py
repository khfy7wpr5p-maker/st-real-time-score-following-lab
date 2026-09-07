from __future__ import annotations

import json

from st_score_following import (
    AlignmentProvenanceV1,
    ConfidenceV1,
    PerformanceEventV1,
    RecoveryAwareSymbolicFollower,
    SymbolicScoreEvent,
    build_performance_alignment_report,
    build_performance_error_intelligence_report,
)


def run() -> dict[str, object]:
    score = tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate((60, 62, 64, 65, 67, 69))
    )
    c0 = ConfidenceV1(
        value=0.95,
        source="sf08_repository_fixture",
        calibrated=False,
        reason="synthetic provenance, not calibrated model confidence",
    )
    c2 = ConfidenceV1(
        value=0.70,
        source="sf08_repository_fixture",
        calibrated=False,
        reason="synthetic provenance, not calibrated model confidence",
    )
    c3 = ConfidenceV1(
        value=0.80,
        source="sf08_repository_fixture",
        calibrated=False,
        reason="synthetic provenance, not calibrated model confidence",
    )
    events = (
        PerformanceEventV1("event-0", 0.0, None, (60,), c0),
        PerformanceEventV1("event-unmatched", 0.25, None, (99,), None),
        PerformanceEventV1("event-2", 1.08, None, (64,), c2),
        PerformanceEventV1("event-3", 3.0, None, (65,), c3),
        PerformanceEventV1("event-back-1", 3.5, None, (62,), None),
        PerformanceEventV1("event-back-2", 4.0, None, (64,), None),
    )
    recovery = RecoveryAwareSymbolicFollower(
        score,
        pause_gap_s=1.5,
    ).run_events(events)
    alignment = build_performance_alignment_report(
        recovery.alignment_path,
        reference_bpm=120.0,
        provenance=AlignmentProvenanceV1(
            backend=recovery.backend,
            backend_version=recovery.backend_version,
            method=recovery.method,
            input_type=recovery.input_type,
            run_id="sf08-repository-owned",
        ),
        on_time_tolerance_ms=40.0,
        pause_gap_s=1.5,
        confidences=(c0, c2, c3, None, None),
    )
    report = build_performance_error_intelligence_report(
        alignment,
        recovery_result=recovery,
    )
    return {
        "schema": "st.score_following.error_intelligence_benchmark.v1",
        "fixture": {
            "score_events": len(score),
            "performance_observations": len(events),
            "accepted_alignment_points": len(recovery.alignment_path),
            "reference_bpm": 120.0,
            "timing_tolerance_ms": 40.0,
        },
        "recovery_metrics": {
            "matched_events": recovery.backend_metrics["matched_events"],
            "unmatched_observations": recovery.backend_metrics["unmatched_observations"],
            "forward_skipped_score_events": recovery.backend_metrics[
                "forward_skipped_score_events"
            ],
            "backward_jumps": recovery.backend_metrics["backward_jumps"],
            "pause_gaps": recovery.backend_metrics["pause_gaps"],
        },
        "error_intelligence_summary": report.summary.to_dict(),
        "event_kinds": [event.kind.value for event in report.events],
        "abstention_kinds": [item.kind.value for item in report.abstentions],
        "authority_boundary": report.authority_boundary,
        "json_bytes": len(report.to_json().encode("utf-8")),
        "csv_lines": len(report.to_csv().splitlines()),
        "interpretation_boundaries": [
            "unmatched observation is not auto-labeled wrong note or extra note",
            "missing confidence remains unavailable",
            "recovery scalar confidence is not promoted into calibrated provenance",
            "no severity score, student grade, or pedagogical authority is emitted",
            "articulation, dynamics, and musical intent remain explicit abstentions",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
