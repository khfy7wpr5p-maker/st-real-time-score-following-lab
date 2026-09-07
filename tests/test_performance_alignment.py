import csv
import io
import json

import pytest

from st_score_following import (
    AlignmentProvenanceV1,
    ConfidenceV1,
    SegmentBoundaryReason,
    TimingClass,
    build_performance_alignment_report,
)
from st_score_following.followers.base import AlignmentPoint


def _path(beats: tuple[float, ...], times: tuple[float, ...]) -> tuple[AlignmentPoint, ...]:
    return tuple(
        AlignmentPoint(score_beat=beat, performance_time_s=time)
        for beat, time in zip(beats, times, strict=True)
    )


def _provenance() -> AlignmentProvenanceV1:
    return AlignmentProvenanceV1(
        backend="unit-test",
        backend_version="1",
        method="synthetic",
        input_type="symbolic",
    )


def test_clean_120_bpm_alignment_has_zero_deviation_and_one_segment() -> None:
    path = _path(tuple(float(i) for i in range(8)), tuple(i * 0.5 for i in range(8)))
    report = build_performance_alignment_report(
        path,
        reference_bpm=120.0,
        provenance=_provenance(),
    )

    assert report.summary.segment_count == 1
    assert report.summary.mean_absolute_segment_deviation_ms == pytest.approx(0.0)
    assert report.summary.p95_absolute_segment_deviation_ms == pytest.approx(0.0)
    assert report.summary.on_time_count == 8
    assert report.summary.local_tempo_samples == 7
    assert report.summary.mean_local_tempo_bpm == pytest.approx(120.0)
    assert report.summary.min_local_tempo_bpm == pytest.approx(120.0)
    assert report.summary.max_local_tempo_bpm == pytest.approx(120.0)


def test_expressive_timing_is_classified_from_segment_relative_deviation() -> None:
    path = _path(
        (0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
        (0.0, 0.45, 1.06, 1.48, 2.09, 2.50),
    )
    report = build_performance_alignment_report(
        path,
        reference_bpm=120.0,
        provenance=_provenance(),
        on_time_tolerance_ms=40.0,
    )

    classes = tuple(point.timing_class for point in report.points)
    assert TimingClass.EARLY in classes
    assert TimingClass.LATE in classes
    assert TimingClass.ON_TIME in classes
    timing_count = (
        report.summary.early_count
        + report.summary.on_time_count
        + report.summary.late_count
    )
    assert timing_count == 6


def test_pause_starts_new_segment_and_avoids_bogus_slow_tempo_sample() -> None:
    path = _path((0.0, 1.0, 2.0, 3.0, 4.0), (0.0, 0.5, 1.0, 3.5, 4.0))
    report = build_performance_alignment_report(
        path,
        reference_bpm=120.0,
        provenance=_provenance(),
        pause_gap_s=1.5,
    )

    assert report.summary.segment_count == 2
    assert report.summary.performance_gap_boundaries == 1
    assert report.points[3].boundary_reason is SegmentBoundaryReason.PERFORMANCE_GAP
    assert report.points[3].local_tempo_bpm is None
    tempos = [point.local_tempo_bpm for point in report.points if point.local_tempo_bpm]
    assert tempos == pytest.approx([120.0, 120.0, 120.0])


def test_backward_score_jump_starts_new_segment_without_negative_tempo() -> None:
    path = _path((0.0, 1.0, 2.0, 1.0, 2.0, 3.0), (0.0, 0.5, 1.0, 1.5, 2.0, 2.5))
    report = build_performance_alignment_report(
        path,
        reference_bpm=120.0,
        provenance=_provenance(),
    )

    assert report.summary.segment_count == 2
    assert report.summary.score_discontinuities == 1
    assert report.points[3].boundary_reason is SegmentBoundaryReason.SCORE_DISCONTINUITY
    assert report.points[3].local_tempo_bpm is None
    assert all(
        point.local_tempo_bpm is None or point.local_tempo_bpm > 0 for point in report.points
    )


def test_json_and_csv_exports_keep_missing_confidence_explicit() -> None:
    report = build_performance_alignment_report(
        _path((0.0, 1.0), (0.0, 0.5)),
        reference_bpm=120.0,
        provenance=_provenance(),
    )

    data = json.loads(report.to_json())
    assert data["points"][0]["confidence"] is None
    rows = list(csv.DictReader(io.StringIO(report.to_csv())))
    assert rows[0]["confidence_value"] == ""
    assert rows[0]["confidence_source"] == ""


def test_explicit_confidence_provenance_is_preserved() -> None:
    confidence = ConfidenceV1(
        value=0.7,
        source="unit_test_confidence",
        calibrated=False,
        reason="fixture",
    )
    report = build_performance_alignment_report(
        _path((0.0,), (0.1,)),
        reference_bpm=120.0,
        provenance=_provenance(),
        confidences=(confidence,),
    )

    assert report.points[0].confidence is confidence
    assert json.loads(report.to_json())["points"][0]["confidence"]["source"] == (
        "unit_test_confidence"
    )


def test_rejects_decreasing_performance_time() -> None:
    with pytest.raises(ValueError, match="non-decreasing"):
        build_performance_alignment_report(
            _path((0.0, 1.0), (1.0, 0.5)),
            reference_bpm=120.0,
            provenance=_provenance(),
        )
