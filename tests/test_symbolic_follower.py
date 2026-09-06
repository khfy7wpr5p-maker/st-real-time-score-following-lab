from __future__ import annotations

import pytest

from st_score_following import CausalSymbolicFollower, ConfidenceV1, PerformanceEventV1
from st_score_following.evaluation import oracle_performance_events, synthetic_score_events


def _event(event_id: str, onset_s: float, pitch: int, confidence: float = 1.0) -> PerformanceEventV1:
    return PerformanceEventV1(
        event_id=event_id,
        observed_at_s=onset_s,
        duration_s=0.5,
        midi_pitches=(pitch,),
        confidence=ConfidenceV1(
            value=confidence,
            source="unit_test",
            calibrated=False,
        ),
    )


def test_oracle_events_follow_complete_synthetic_score() -> None:
    result = CausalSymbolicFollower(synthetic_score_events()).run_events(
        oracle_performance_events()
    )

    assert len(result.updates) == 16
    assert result.updates[-1].score_beat == pytest.approx(15.0)
    assert result.backend_metrics["matched_events"] == 16
    assert result.backend_metrics["unmatched_observations"] == 0
    assert result.confidence_available is True


def test_unmatched_observation_does_not_advance_score() -> None:
    follower = CausalSymbolicFollower(synthetic_score_events(), lookahead_events=1)
    events = (_event("wrong", 0.0, 99), _event("first", 0.5, 60))

    result = follower.run_events(events)

    assert [update.score_beat for update in result.updates] == [0.0]
    assert result.backend_metrics["unmatched_observations"] == 1


def test_missing_score_event_recovers_with_bounded_lookahead() -> None:
    follower = CausalSymbolicFollower(synthetic_score_events(), lookahead_events=2)
    events = (_event("first", 0.0, 60), _event("third", 1.0, 64))

    result = follower.run_events(events)

    assert [update.score_beat for update in result.updates] == [0.0, 2.0]
    assert result.backend_metrics["skipped_score_events"] == 1


def test_low_confidence_observation_can_be_rejected_explicitly() -> None:
    follower = CausalSymbolicFollower(
        synthetic_score_events(),
        min_event_confidence=0.5,
    )

    result = follower.run_events((_event("weak", 0.0, 60, confidence=0.2),))

    assert result.updates == ()
    assert result.backend_metrics["low_confidence_rejections"] == 1
