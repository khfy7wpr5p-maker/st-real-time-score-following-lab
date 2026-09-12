from __future__ import annotations

import json
from statistics import median

from st_score_following import (
    OrchestraGlobalFollower,
    OrchestraGlobalObservationV1,
    OrchestraGlobalScorePointV1,
)

SIGNATURES = (
    (0, 4, 5, 7, 8),
    (0, 2, 5, 8, 11),
    (1, 2, 3, 5, 6),
    (1, 3, 6, 8, 9),
    (2, 3, 5, 9, 10),
    (3, 5, 7, 8, 10),
    (1, 3, 4, 8, 11),
    (2, 3, 7, 8, 10),
    (1, 4, 6, 9, 11),
    (1, 2, 4, 7, 9),
    (0, 1, 4, 6, 8),
    (4, 5, 7, 10, 11),
    (0, 3, 5, 6, 11),
    (0, 1, 4, 7, 9),
    (3, 4, 5, 9, 10),
    (0, 4, 7, 8, 9),
    (1, 2, 6, 8, 9),
    (4, 5, 6, 10, 11),
    (3, 5, 6, 8, 11),
    (0, 1, 5, 8, 10),
    (2, 3, 4, 10, 11),
    (0, 4, 6, 7, 10),
    (1, 3, 6, 8, 11),
    (3, 4, 8, 9, 11),
    (0, 1, 2, 4, 5),
    (1, 2, 6, 7, 9),
    (0, 1, 4, 7, 11),
    (0, 2, 4, 7, 8),
    (0, 4, 5, 9, 10),
    (4, 5, 7, 8, 10),
    (0, 1, 4, 5, 8),
    (0, 1, 3, 9, 10),
)


def _score() -> tuple[OrchestraGlobalScorePointV1, ...]:
    return tuple(
        OrchestraGlobalScorePointV1(
            score_index=index,
            measure_index=index // 4 + 1,
            beat_in_measure=float(index % 4 + 1),
            score_beat=float(index),
            texture_pitch_classes=signature,
        )
        for index, signature in enumerate(SIGNATURES)
    )


def _dense_signature(index: int) -> tuple[int, ...]:
    values = set(SIGNATURES[index])
    values.remove(SIGNATURES[index][index % len(SIGNATURES[index])])
    extra = (index * 7 + 3) % 12
    while extra in values:
        extra = (extra + 1) % 12
    values.add(extra)
    return tuple(sorted(values))


def _events(
    sequence: list[int],
    *,
    dense: bool = False,
    intervals: list[float] | None = None,
    pause_before_ordinal: int | None = None,
) -> tuple[OrchestraGlobalObservationV1, ...]:
    observations = []
    at_s = 0.0
    for ordinal, score_index in enumerate(sequence):
        if pause_before_ordinal is not None and ordinal == pause_before_ordinal:
            at_s += 2.0
        signature = _dense_signature(score_index) if dense else SIGNATURES[score_index]
        observations.append(
            OrchestraGlobalObservationV1(
                event_id=f"obs-{ordinal}-{score_index}",
                observed_at_s=at_s,
                texture_pitch_classes=signature,
                confidence=None,
            )
        )
        interval = 0.5 if intervals is None else intervals[ordinal % len(intervals)]
        at_s += interval
    return tuple(observations)


def _case(
    name: str,
    sequence: list[int],
    *,
    dense: bool = False,
    intervals: list[float] | None = None,
    pause_before_ordinal: int | None = None,
    recovery_boundary_ordinal: int | None = None,
) -> dict[str, object]:
    observations = _events(
        sequence,
        dense=dense,
        intervals=intervals,
        pause_before_ordinal=pause_before_ordinal,
    )
    report = OrchestraGlobalFollower(_score()).run(observations)
    actual = {match.event_id: match.score_index for match in report.matches}
    errors = []
    failed = 0
    for ordinal, expected_index in enumerate(sequence):
        event_id = f"obs-{ordinal}-{expected_index}"
        observed_index = actual.get(event_id)
        if observed_index is None:
            failed += 1
            continue
        error = abs(observed_index - expected_index)
        errors.append(float(error))
        failed += error != 0
    recovery_observations = None
    additional_recovery_delay_s = None
    if recovery_boundary_ordinal is not None:
        boundary_expected = sequence[recovery_boundary_ordinal]
        boundary_event_id = f"obs-{recovery_boundary_ordinal}-{boundary_expected}"
        if actual.get(boundary_event_id) == boundary_expected:
            recovery_observations = 1
            additional_recovery_delay_s = 0.0
    return {
        "name": name,
        "observations": len(observations),
        "matched": report.summary.matched_observations,
        "mapping_failures": failed,
        "failure_rate": failed / len(observations),
        "median_absolute_position_error_beats": median(errors) if errors else None,
        "max_absolute_position_error_beats": max(errors, default=None),
        "recovery_observations": recovery_observations,
        "additional_recovery_delay_s": additional_recovery_delay_s,
        "summary": report.summary.to_dict(),
    }


def main() -> None:
    clean = list(range(32))
    dropped = [index for index in range(32) if index not in {9, 21}]
    forward_skip = list(range(12)) + list(range(18, 32))
    backward_jump = list(range(24)) + list(range(14, 24))
    restart = list(range(20)) + list(range(12))
    output = {
        "schema": "st.score_following.orchestra_global_benchmark.v1",
        "authority_boundary": (
            "global_measure_beat_research_not_per_instrument_transcription_authority"
        ),
        "evidence_scope": [
            "repository-owned deterministic aggregate pitch-class texture proxy",
            "global measure/beat position only",
            "processing latency is local CPU work, not microphone/model/end-to-end latency",
            "texture similarity is a matching score, not calibrated confidence",
            "no per-instrument transcription or source separation is inferred",
            "real dense orchestral audio robustness remains unproven",
        ],
        "cases": {
            "clean": _case("clean", clean),
            "dense_texture_proxy": _case("dense_texture_proxy", clean, dense=True),
            "tempo_drift_rubato": _case(
                "tempo_drift_rubato",
                clean,
                intervals=[0.41, 0.57, 0.46, 0.62, 0.44, 0.53],
            ),
            "missing_observations": _case("missing_observations", dropped),
            "forward_skip": _case(
                "forward_skip",
                forward_skip,
                recovery_boundary_ordinal=12,
            ),
            "backward_jump": _case(
                "backward_jump",
                backward_jump,
                recovery_boundary_ordinal=24,
            ),
            "restart_after_pause": _case(
                "restart_after_pause",
                restart,
                pause_before_ordinal=20,
                recovery_boundary_ordinal=20,
            ),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
