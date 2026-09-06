from __future__ import annotations

from pathlib import Path

import pytest

from st_score_following.integrations import StradiCsvOutputAdapter
from st_score_following.symbolic import (
    CausalSymbolicFollower,
    SymbolicScoreEvent,
)


FIXTURE = Path(__file__).parent / "fixtures" / "stradi_synthetic_violin_output.csv"
SCORE = tuple(
    SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
    for index, pitch in enumerate((69, 71, 72, 74, 76))
)


def test_stradi_csv_maps_events_without_fabricating_confidence() -> None:
    result = StradiCsvOutputAdapter(backend_version="research-candidate").load_csv(FIXTURE)

    assert len(result.events) == 5
    assert result.events[0].observed_at_s == pytest.approx(0.0)
    assert result.events[-1].midi_pitches == (76,)
    assert all(event.confidence is None for event in result.events)
    assert result.metadata["confidence_available"] is False


def test_symbolic_follower_accepts_unavailable_confidence_when_no_threshold() -> None:
    transcription = StradiCsvOutputAdapter().load_csv(FIXTURE)
    result = CausalSymbolicFollower(SCORE).run_events(transcription.events)

    assert [update.score_beat for update in result.updates] == [0.0, 1.0, 2.0, 3.0, 4.0]
    assert all(update.confidence is None for update in result.updates)
    assert result.backend_metrics["unavailable_confidence"] == 5
    assert result.confidence_available is False


def test_confidence_gate_rejects_events_when_confidence_is_unavailable() -> None:
    transcription = StradiCsvOutputAdapter().load_csv(FIXTURE)
    result = CausalSymbolicFollower(SCORE, min_event_confidence=0.5).run_events(
        transcription.events
    )

    assert result.updates == ()
    assert result.backend_metrics["unavailable_confidence_rejections"] == 5


def test_tempo_variation_timestamps_are_preserved() -> None:
    transcription = StradiCsvOutputAdapter().load_csv(FIXTURE)
    result = CausalSymbolicFollower(SCORE).run_events(transcription.events)

    assert [point.performance_time_s for point in result.alignment_path] == pytest.approx(
        [0.0, 0.47, 1.02, 1.57, 2.18]
    )
