import pytest

from st_score_following import RecoveryAwareSymbolicFollower
from st_score_following.evaluation import (
    evaluate_recovery_result,
    recovery_scenarios,
    recovery_score_events,
)

EXPECTED_SCENARIOS = {
    "clean",
    "wrong_note",
    "missing_note",
    "extra_note",
    "pause",
    "restart",
    "repeat",
    "skip",
    "backward_jump",
    "tempo_change",
    "rubato",
}


def test_recovery_suite_covers_required_scenarios() -> None:
    assert {scenario.name for scenario in recovery_scenarios()} == EXPECTED_SCENARIOS


@pytest.mark.parametrize(
    "scenario",
    recovery_scenarios(),
    ids=lambda scenario: scenario.name,
)
def test_recovery_follower_maps_all_scenario_truth(scenario: object) -> None:
    result = RecoveryAwareSymbolicFollower(recovery_score_events()).run_events(scenario.events)
    metrics = evaluate_recovery_result(result, scenario)

    assert metrics.passed
    assert metrics.mapping_accuracy == 1.0
    assert metrics.noise_rejection_rate == 1.0


def test_restart_uses_explicit_global_gap_relock() -> None:
    scenario = next(item for item in recovery_scenarios() if item.name == "restart")
    result = RecoveryAwareSymbolicFollower(recovery_score_events()).run_events(scenario.events)
    restart_match = next(
        match
        for match in result.backend_metrics["matches"]
        if match["event_id"] == "restart-new-0"
    )

    assert restart_match["transition"] == "restart"
    assert restart_match["search_scope"] == "global_gap"
    assert result.backend_metrics["global_relocks"] >= 1


def test_pause_preserves_lock_and_records_gap() -> None:
    scenario = next(item for item in recovery_scenarios() if item.name == "pause")
    result = RecoveryAwareSymbolicFollower(recovery_score_events()).run_events(scenario.events)
    metrics = evaluate_recovery_result(result, scenario)

    assert result.backend_metrics["pause_gaps"] == 1
    assert metrics.relock_performance_time_s == pytest.approx(2.0)
    assert metrics.relock_observations == 1


def test_repeat_and_backward_jump_are_auditable() -> None:
    for name in ("repeat", "backward_jump"):
        scenario = next(item for item in recovery_scenarios() if item.name == name)
        result = RecoveryAwareSymbolicFollower(recovery_score_events()).run_events(scenario.events)
        assert result.backend_metrics["backward_jumps"] >= 1
