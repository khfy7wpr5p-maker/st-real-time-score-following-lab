from __future__ import annotations

import json

from st_score_following import (
    InstrumentFamily,
    MixedEnsembleAnalyzer,
    MixedEnsemblePartInputV1,
    ObservationPathKind,
    ObservationTimingBasis,
    PerformanceEventV1,
    SymbolicScoreEvent,
)

PITCHES = {
    "piano": (60, 62, 64, 65, 67, 69, 71, 72),
    "guitar": (52, 54, 55, 57, 59, 60, 62, 64),
    "violin": (67, 69, 71, 72, 74, 76, 77, 79),
    "voice": (55, 57, 59, 60, 62, 64, 65, 67),
}
CONFIG = {
    "piano": (InstrumentFamily.PIANO, ObservationPathKind.DIRECT_MIDI, 0.0),
    "guitar": (InstrumentFamily.GUITAR, ObservationPathKind.TRANSCRIPTION_SYMBOLIC, 0.02),
    "violin": (InstrumentFamily.VIOLIN, ObservationPathKind.EXTERNAL_EVENT_ADAPTER, 0.035),
    "voice": (InstrumentFamily.VOICE, ObservationPathKind.SYNTHETIC_ORACLE, 0.05),
}


def _part(
    name: str,
    *,
    indices: tuple[int, ...] = tuple(range(8)),
    timing_basis: ObservationTimingBasis = ObservationTimingBasis.PERFORMANCE_ONSET,
    shift_after: int | None = None,
    shift_s: float = 0.0,
    use_score_time: bool = True,
) -> MixedEnsemblePartInputV1:
    family, path, offset = CONFIG[name]
    score = tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(PITCHES[name])
    )
    events = []
    for ordinal, score_index in enumerate(indices):
        base_index = score_index if use_score_time else ordinal
        observed_at_s = base_index * 0.5 + offset
        if shift_after is not None and score_index >= shift_after:
            observed_at_s += shift_s
        events.append(
            PerformanceEventV1(
                event_id=f"{name}-{ordinal}-{score_index}",
                observed_at_s=observed_at_s,
                duration_s=0.2,
                midi_pitches=(PITCHES[name][score_index],),
                confidence=None,
            )
        )
    return MixedEnsemblePartInputV1(
        part_id=f"part-{name}",
        performer_id=f"performer-{name}",
        channel_id=f"channel-{name}",
        instrument_family=family,
        observation_path=path,
        timing_basis=timing_basis,
        path_source=f"repository_fixture:{path.value}",
        score_events=score,
        observations=tuple(events),
    )


def _case(name: str, parts: tuple[MixedEnsemblePartInputV1, ...]) -> dict[str, object]:
    report = MixedEnsembleAnalyzer(parts).run()
    return {
        "name": name,
        "authority_boundary": report.authority_boundary,
        "parts": [
            {
                "part_id": part.part_id,
                "instrument_family": part.instrument_family.value,
                "observation_path": part.observation_path.value,
                "timing_basis": part.timing_basis.value,
                "matched_events": part.matched_events,
                "final_score_beat": part.final_score_beat,
                "forward_skipped_score_events": part.forward_skipped_score_events,
                "pause_gaps": part.pause_gaps,
            }
            for part in report.parts
        ],
        "summary": report.summary.to_dict(),
        "timing_abstentions": [item.reason for item in report.timing_abstentions],
    }


def main() -> None:
    clean = tuple(_part(name) for name in CONFIG)
    unverified_voice = tuple(
        _part(name, timing_basis=ObservationTimingBasis.UNVERIFIED)
        if name == "voice"
        else _part(name)
        for name in CONFIG
    )
    unverified_voice_plus_pause = tuple(
        _part(name, timing_basis=ObservationTimingBasis.UNVERIFIED)
        if name == "voice"
        else _part(name, shift_after=4, shift_s=1.6)
        if name == "guitar"
        else _part(name)
        for name in CONFIG
    )
    dropped_guitar = tuple(
        _part(name, indices=(0, 1, 2, 4, 5, 6, 7))
        if name == "guitar"
        else _part(name)
        for name in CONFIG
    )
    advanced_voice = tuple(
        _part(name, indices=(0, 1, 4, 5, 6, 7), use_score_time=False)
        if name == "voice"
        else _part(name)
        for name in CONFIG
    )
    output = {
        "schema": "st.score_following.mixed_ensemble_benchmark.v1",
        "boundaries": [
            "instrument family and observation path provenance remain explicit",
            (
                "unverified timing paths keep independent score following but abstain "
                "from shared timing evidence"
            ),
            "shared position uses only recent timing-comparable paths",
            "below quorum no mixed-ensemble shared position is fabricated",
            "synthetic oracle path is architecture evidence only",
            "channel-separated evidence does not establish acoustic mixture source separation",
            "shared confidence remains unavailable rather than fabricated",
        ],
        "cases": {
            "clean": _case("clean", clean),
            "unverified_voice_timing": _case("unverified_voice_timing", unverified_voice),
            "unverified_voice_plus_guitar_pause": _case(
                "unverified_voice_plus_guitar_pause",
                unverified_voice_plus_pause,
            ),
            "dropped_guitar_event": _case("dropped_guitar_event", dropped_guitar),
            "advanced_voice": _case("advanced_voice", advanced_voice),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
