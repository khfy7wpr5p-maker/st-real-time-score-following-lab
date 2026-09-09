from __future__ import annotations

import json

from st_score_following import (
    PerformanceEventV1,
    QuartetAnalyzer,
    QuartetPartInputV1,
    SymbolicScoreEvent,
)

PART_PITCHES = {
    "part-a": (60, 62, 64, 65, 67, 69, 71, 72),
    "part-b": (48, 50, 52, 53, 55, 57, 59, 60),
    "part-c": (55, 57, 59, 60, 62, 64, 65, 67),
    "part-d": (72, 71, 69, 67, 65, 64, 62, 60),
}
OFFSETS = {"part-a": 0.0, "part-b": 0.02, "part-c": 0.035, "part-d": 0.05}


def _score(part_id: str) -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(PART_PITCHES[part_id])
    )


def _observations(
    part_id: str,
    score_indices: tuple[int, ...],
    *,
    use_score_time: bool = True,
    shift_after_score_index: int | None = None,
    shift_s: float = 0.0,
) -> tuple[PerformanceEventV1, ...]:
    items: list[PerformanceEventV1] = []
    for ordinal, score_index in enumerate(score_indices):
        base_index = score_index if use_score_time else ordinal
        observed_at_s = base_index * 0.5 + OFFSETS[part_id]
        if shift_after_score_index is not None and score_index >= shift_after_score_index:
            observed_at_s += shift_s
        items.append(
            PerformanceEventV1(
                event_id=f"{part_id}-{ordinal}-{score_index}",
                observed_at_s=observed_at_s,
                duration_s=0.2,
                midi_pitches=(PART_PITCHES[part_id][score_index],),
                confidence=None,
            )
        )
    return tuple(items)


def _part(
    part_id: str,
    score_indices: tuple[int, ...],
    *,
    use_score_time: bool = True,
    shift_after_score_index: int | None = None,
    shift_s: float = 0.0,
) -> QuartetPartInputV1:
    suffix = part_id[-1]
    return QuartetPartInputV1(
        part_id=part_id,
        performer_id=f"performer-{suffix}",
        channel_id=f"channel-{suffix}",
        score_events=_score(part_id),
        observations=_observations(
            part_id,
            score_indices,
            use_score_time=use_score_time,
            shift_after_score_index=shift_after_score_index,
            shift_s=shift_s,
        ),
    )


def _run_case(name: str, parts: tuple[QuartetPartInputV1, ...]) -> dict[str, object]:
    report = QuartetAnalyzer(parts).run()
    summary = report.summary.to_dict()
    return {
        "name": name,
        "authority_boundary": report.authority_boundary,
        "required_quorum_parts": report.required_quorum_parts,
        "parts": [
            {
                "part_id": part.part_id,
                "matched_events": part.matched_events,
                "final_score_beat": part.final_score_beat,
                "forward_skipped_score_events": part.forward_skipped_score_events,
                "pause_gaps": part.pause_gaps,
                "unmatched_observations": part.unmatched_observations,
            }
            for part in report.parts
        ],
        "summary": summary,
        "status_counts": {
            "full_consensus": summary["full_consensus_snapshots"],
            "quorum_consensus": summary["quorum_consensus_snapshots"],
            "divergent": summary["divergent_snapshots"],
            "insufficient_quorum": summary["insufficient_quorum_snapshots"],
            "degraded_insufficient_quorum": summary[
                "degraded_insufficient_quorum_snapshots"
            ],
        },
    }


def main() -> None:
    all_indices = tuple(range(8))
    clean = tuple(_part(part_id, all_indices) for part_id in PART_PITCHES)

    dropped = tuple(
        _part(part_id, tuple(index for index in all_indices if index != 3))
        if part_id == "part-d"
        else _part(part_id, all_indices)
        for part_id in PART_PITCHES
    )

    paused = tuple(
        _part(
            part_id,
            all_indices,
            shift_after_score_index=4,
            shift_s=1.6,
        )
        if part_id == "part-c"
        else _part(part_id, all_indices)
        for part_id in PART_PITCHES
    )

    advanced = tuple(
        _part(part_id, (0, 1, 4, 5, 6, 7), use_score_time=False)
        if part_id == "part-d"
        else _part(part_id, all_indices)
        for part_id in PART_PITCHES
    )

    two_channel_loss = tuple(
        _part(part_id, (0, 1, 2))
        if part_id in {"part-c", "part-d"}
        else _part(part_id, all_indices)
        for part_id in PART_PITCHES
    )

    output = {
        "schema": "st.score_following.quartet_multichannel_benchmark.v1",
        "boundaries": [
            "four channels retain independent part/performer identity",
            "shared position is published only when quorum is met",
            "below-quorum state does not fabricate shared score position",
            "divergence is exposed instead of silently forcing consensus",
            "pairwise asynchrony is timing evidence rather than a quality grade",
            "shared confidence remains unavailable rather than fabricated",
            "multi-channel quartet evidence does not establish mono-mixture separation",
        ],
        "cases": {
            "clean": _run_case("clean", clean),
            "drop_one_event": _run_case("drop_one_event", dropped),
            "pause_one_performer": _run_case("pause_one_performer", paused),
            "advance_one_performer": _run_case("advance_one_performer", advanced),
            "two_channel_loss": _run_case("two_channel_loss", two_channel_loss),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
