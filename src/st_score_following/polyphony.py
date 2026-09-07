from __future__ import annotations

from collections.abc import Iterable

from .contracts import ConfidenceV1, PerformanceEventV1


def _cluster_confidence(events: list[PerformanceEventV1]) -> ConfidenceV1 | None:
    confidences = [event.confidence for event in events]
    if any(confidence is None for confidence in confidences):
        return None
    available = [confidence for confidence in confidences if confidence is not None]
    return ConfidenceV1(
        value=min(confidence.value for confidence in available),
        source="st_polyphonic_cluster:min_input",
        calibrated=False,
        reason="Minimum available input confidence; not a calibrated cluster probability.",
    )


def cluster_simultaneous_note_events(
    events: Iterable[PerformanceEventV1],
    *,
    onset_tolerance_s: float = 0.03,
) -> tuple[PerformanceEventV1, ...]:
    """Group near-simultaneous note events into onset-level polyphonic observations."""
    if onset_tolerance_s < 0:
        raise ValueError("onset_tolerance_s must be >= 0")

    ordered = sorted(events, key=lambda event: (event.observed_at_s, event.event_id))
    if not ordered:
        return ()

    groups: list[list[PerformanceEventV1]] = []
    current = [ordered[0]]
    anchor = ordered[0].observed_at_s
    for event in ordered[1:]:
        if event.observed_at_s - anchor <= onset_tolerance_s:
            current.append(event)
            continue
        groups.append(current)
        current = [event]
        anchor = event.observed_at_s
    groups.append(current)

    clustered: list[PerformanceEventV1] = []
    for index, group in enumerate(groups):
        onset_s = min(event.observed_at_s for event in group)
        pitches = tuple(sorted({pitch for event in group for pitch in event.midi_pitches}))
        if not pitches:
            raise ValueError("polyphonic clusters must contain at least one MIDI pitch")

        duration_s: float | None
        if all(event.duration_s is not None for event in group):
            end_s = max(event.observed_at_s + float(event.duration_s) for event in group)
            duration_s = end_s - onset_s
        else:
            duration_s = None

        clustered.append(
            PerformanceEventV1(
                event_id=f"polyphonic-cluster-{index:04d}",
                observed_at_s=onset_s,
                duration_s=duration_s,
                midi_pitches=pitches,
                confidence=_cluster_confidence(group),
            )
        )

    return tuple(clustered)
