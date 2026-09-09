from __future__ import annotations

import json

from st_score_following import (
    DuetAnalyzer,
    DuetPartInputV1,
    PerformanceEventV1,
    SymbolicScoreEvent,
)

PART_A_PITCHES = (60, 62, 64, 65, 67, 69, 71, 72)
PART_B_PITCHES = (48, 50, 52, 53, 55, 57, 59, 60)


def _score(pitches: tuple[int, ...]) -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(pitches)
    )


def _events(
    prefix: str,
    pitches: tuple[int, ...],
    indices: tuple[int, ...],
    times: tuple[float, ...],
) -> tuple[PerformanceEventV1, ...]:
    return tuple(
        PerformanceEventV1(
            event_id=f"{prefix}-{index}",
            observed_at_s=time,
            duration_s=None,
            midi_pitches=(pitches[index],),
            confidence=None,
        )
        for index, time in zip(indices, times, strict=True)
    )


def _part(
    part_id: str,
    performer_id: str,
    prefix: str,
    pitches: tuple[int, ...],
    indices: tuple[int, ...],
    times: tuple[float, ...],
) -> DuetPartInputV1:
    return DuetPartInputV1(
        part_id=part_id,
        performer_id=performer_id,
        score_events=_score(pitches),
        observations=_events(prefix, pitches, indices, times),
    )


def _part_a() -> DuetPartInputV1:
    indices = tuple(range(8))
    return _part(
        "part-a",
        "performer-a",
        "a",
        PART_A_PITCHES,
        indices,
        tuple(index * 0.5 for index in indices),
    )


def _part_b(
    indices: tuple[int, ...],
    times: tuple[float, ...],
) -> DuetPartInputV1:
    return _part(
        "part-b",
        "performer-b",
        "b",
        PART_B_PITCHES,
        indices,
        times,
    )


def _case(
    name: str,
    part_b: DuetPartInputV1,
) -> dict[str, object]:
    report = DuetAnalyzer(
        (_part_a(), part_b),
        stale_after_s=0.75,
        divergence_threshold_beats=1.5,
    ).run()
    return {
        "name": name,
        "summary": report.summary.to_dict(),
        "parts": [
            {
                "part_id": part.part_id,
                "matched_events": part.matched_events,
                "unmatched_observations": part.unmatched_observations,
                "forward_skipped_score_events": part.forward_skipped_score_events,
                "pause_gaps": part.pause_gaps,
                "final_score_beat": part.final_score_beat,
            }
            for part in report.parts
        ],
        "shared_status_counts": {
            "consensus": report.summary.consensus_snapshots,
            "single_part": report.summary.single_part_snapshots,
            "divergent": report.summary.divergent_snapshots,
        },
        "max_position_spread_beats": report.summary.max_position_spread_beats,
        "common_asynchrony_points": report.summary.common_asynchrony_points,
        "mean_absolute_asynchrony_ms": report.summary.mean_absolute_asynchrony_ms,
        "max_absolute_asynchrony_ms": report.summary.max_absolute_asynchrony_ms,
        "authority_boundary": report.authority_boundary,
    }


def run() -> dict[str, object]:
    clean_indices = tuple(range(8))
    return {
        "schema": "st.score_following.duet_research_benchmark.v1",
        "cases": {
            "clean": _case(
                "clean",
                _part_b(
                    clean_indices,
                    tuple(index * 0.5 + 0.02 for index in clean_indices),
                ),
            ),
            "drop_one_event": _case(
                "drop_one_event",
                _part_b(
                    (0, 1, 2, 4, 5, 6, 7),
                    (0.02, 0.52, 1.02, 2.02, 2.52, 3.02, 3.52),
                ),
            ),
            "pause_one_performer": _case(
                "pause_one_performer",
                _part_b(
                    clean_indices,
                    (0.02, 0.52, 1.02, 3.02, 3.52, 4.02, 4.52, 5.02),
                ),
            ),
            "advance_one_performer": _case(
                "advance_one_performer",
                _part_b(
                    (0, 1, 2, 5, 6, 7),
                    (0.02, 0.52, 1.02, 1.52, 2.02, 2.52),
                ),
            ),
        },
        "boundaries": [
            "each part is followed independently",
            "shared position is a derived median view, not score authority",
            "stale parts are excluded from shared position rather than blocking the other part",
            "divergence is exposed as spread instead of silently forcing consensus",
            "shared confidence remains unavailable rather than fabricated",
            "duet evidence does not establish quartet or orchestra behavior",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
