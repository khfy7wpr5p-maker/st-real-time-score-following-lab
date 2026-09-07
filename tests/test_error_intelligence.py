import csv
import io
import json

import pytest

from st_score_following import (
    AbstentionKind,
    AlignmentProvenanceV1,
    ConfidenceV1,
    EvidenceKind,
    PerformanceEventV1,
    RecoveryAwareSymbolicFollower,
    SymbolicScoreEvent,
    build_performance_alignment_report,
    build_performance_error_intelligence_report,
)
from st_score_following.followers.base import AlignmentPoint


def _fixture_report():
    score = tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate((60, 62, 64, 65, 67, 69))
    )
    c0 = ConfidenceV1(
        value=0.95,
        source="sf08_fixture",
        calibrated=False,
        reason="deterministic fixture provenance",
    )
    c2 = ConfidenceV1(
        value=0.70,
        source="sf08_fixture",
        calibrated=False,
        reason="deterministic fixture provenance",
    )
    c3 = ConfidenceV1(
        value=0.80,
        source="sf08_fixture",
        calibrated=False,
        reason="deterministic fixture provenance",
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
            run_id="sf08-unit-fixture",
        ),
        on_time_tolerance_ms=40.0,
        pause_gap_s=1.5,
        confidences=(c0, c2, c3, None, None),
    )
    return build_performance_error_intelligence_report(
        alignment,
        recovery_result=recovery,
        observations=events,
    )


def test_error_intelligence_emits_only_supported_evidence_kinds() -> None:
    report = _fixture_report()
    kinds = [event.kind for event in report.events]

    assert kinds.count(EvidenceKind.TIMING_LATE) == 1
    assert kinds.count(EvidenceKind.UNMATCHED_OBSERVATION) == 1
    assert kinds.count(EvidenceKind.SKIPPED_SCORE_REGION) == 1
    assert kinds.count(EvidenceKind.PERFORMANCE_GAP) == 1
    assert kinds.count(EvidenceKind.SCORE_DISCONTINUITY) == 1
    assert report.summary.evidence_event_count == 5


def test_unmatched_observation_is_not_promoted_to_wrong_or_extra_note() -> None:
    report = _fixture_report()
    unmatched = next(
        event
        for event in report.events
        if event.kind is EvidenceKind.UNMATCHED_OBSERVATION
    )

    assert unmatched.count == 1
    assert unmatched.performance_time_s == pytest.approx(0.25)
    assert unmatched.source_reference == "recovery:event:event-unmatched"
    assert any(
        item.kind is AbstentionKind.UNMATCHED_OBSERVATION_SEMANTICS
        for item in report.abstentions
    )
    payload = report.to_json()
    assert '"kind": "wrong_note"' not in payload
    assert '"kind": "extra_note"' not in payload


def test_forward_skip_becomes_auditable_skipped_score_region() -> None:
    report = _fixture_report()
    skipped = next(
        event
        for event in report.events
        if event.kind is EvidenceKind.SKIPPED_SCORE_REGION
    )

    assert skipped.score_index_start == 1
    assert skipped.score_index_end == 1
    assert skipped.count == 1
    assert skipped.source_reference == "recovery:event:event-2"
    assert skipped.confidence is None


def test_timing_confidence_is_preserved_without_calibration_claim() -> None:
    report = _fixture_report()
    timing = next(
        event for event in report.events if event.kind is EvidenceKind.TIMING_LATE
    )

    assert timing.deviation_ms == pytest.approx(80.0)
    assert timing.confidence is not None
    assert timing.confidence.value == pytest.approx(0.70)
    assert timing.confidence.source == "sf08_fixture"
    assert not timing.confidence.calibrated


def test_boundaries_remain_facts_and_do_not_create_cross_boundary_tempo_claims() -> None:
    report = _fixture_report()
    boundary_kinds = {
        event.kind
        for event in report.events
        if event.kind in {
            EvidenceKind.PERFORMANCE_GAP,
            EvidenceKind.SCORE_DISCONTINUITY,
        }
    }

    assert boundary_kinds == {
        EvidenceKind.PERFORMANCE_GAP,
        EvidenceKind.SCORE_DISCONTINUITY,
    }
    assert report.summary.performance_gap_events == 1
    assert report.summary.score_discontinuity_events == 1


def test_summary_has_no_grade_or_severity_score() -> None:
    report = _fixture_report()
    summary = report.summary.to_dict()

    assert "grade" not in summary
    assert "score" not in summary
    assert "severity" not in summary
    assert report.authority_boundary == "research_evidence_not_pedagogical_authority"
    assert any(
        item.kind is AbstentionKind.PEDAGOGICAL_GRADE
        for item in report.abstentions
    )


def test_json_and_csv_are_stable_and_keep_missing_confidence_blank() -> None:
    report = _fixture_report()
    data = json.loads(report.to_json())
    rows = list(csv.DictReader(io.StringIO(report.to_csv())))

    assert data["summary"]["evidence_event_count"] == 5
    assert len(rows) == 5
    skipped_row = next(row for row in rows if row["kind"] == "skipped_score_region")
    assert skipped_row["confidence_value"] == ""
    assert skipped_row["confidence_source"] == ""


def test_clean_alignment_can_return_zero_evidence_with_explicit_abstentions() -> None:
    alignment = build_performance_alignment_report(
        (
            AlignmentPoint(score_beat=0.0, performance_time_s=0.0),
            AlignmentPoint(score_beat=1.0, performance_time_s=0.5),
        ),
        reference_bpm=120.0,
        provenance=AlignmentProvenanceV1(backend="clean-fixture"),
    )
    report = build_performance_error_intelligence_report(alignment)

    assert report.events == ()
    assert report.summary.evidence_event_count == 0
    assert report.summary.timing_event_count == 0
    assert report.summary.mean_absolute_timing_deviation_ms is None
    assert report.summary.abstention_count >= 5
