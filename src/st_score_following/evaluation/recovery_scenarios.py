from __future__ import annotations

from dataclasses import asdict, dataclass

from ..contracts import ConfidenceV1, PerformanceEventV1
from ..followers.base import FollowerRunResult
from ..symbolic import SymbolicScoreEvent

RECOVERY_PITCHES = (
    60,
    62,
    64,
    65,
    67,
    69,
    71,
    72,
    74,
    76,
    77,
    79,
    81,
    83,
    84,
    86,
)


@dataclass(frozen=True, slots=True)
class RecoveryTruth:
    event_id: str
    expected_score_index: int | None


@dataclass(frozen=True, slots=True)
class RecoveryScenario:
    name: str
    taxonomy: str
    events: tuple[PerformanceEventV1, ...]
    truth: tuple[RecoveryTruth, ...]
    perturbation_time_s: float | None
    recovery_target_event_id: str | None
    fail_soft_policy: str


@dataclass(frozen=True, slots=True)
class RecoveryScenarioMetrics:
    scenario: str
    taxonomy: str
    valid_observations: int
    noise_observations: int
    correct_mappings: int
    missed_valid_observations: int
    wrong_mappings: int
    noise_rejected: int
    mapping_accuracy: float
    noise_rejection_rate: float
    relock_performance_time_s: float | None
    relock_observations: int | None
    passed: bool
    fail_soft_policy: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def recovery_score_events() -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(RECOVERY_PITCHES)
    )


def _score_event(event_id: str, score_index: int, onset_s: float) -> PerformanceEventV1:
    return PerformanceEventV1(
        event_id=event_id,
        observed_at_s=onset_s,
        duration_s=0.4,
        midi_pitches=(RECOVERY_PITCHES[score_index],),
        confidence=ConfidenceV1(
            value=1.0,
            source="synthetic_recovery_oracle",
            calibrated=False,
            reason="Repository-owned scenario truth; not model confidence.",
        ),
    )


def _noise(event_id: str, onset_s: float) -> PerformanceEventV1:
    return PerformanceEventV1(
        event_id=event_id,
        observed_at_s=onset_s,
        duration_s=0.2,
        midi_pitches=(99,),
        confidence=ConfidenceV1(
            value=1.0,
            source="synthetic_recovery_noise",
            calibrated=False,
            reason="Injected perturbation truth; not model confidence.",
        ),
    )


def _build(
    *,
    name: str,
    taxonomy: str,
    items: list[tuple[PerformanceEventV1, int | None]],
    perturbation_time_s: float | None,
    recovery_target_event_id: str | None,
    fail_soft_policy: str,
) -> RecoveryScenario:
    ordered = sorted(items, key=lambda item: item[0].observed_at_s)
    return RecoveryScenario(
        name=name,
        taxonomy=taxonomy,
        events=tuple(item[0] for item in ordered),
        truth=tuple(RecoveryTruth(item[0].event_id, item[1]) for item in ordered),
        perturbation_time_s=perturbation_time_s,
        recovery_target_event_id=recovery_target_event_id,
        fail_soft_policy=fail_soft_policy,
    )


def _clean() -> RecoveryScenario:
    items = [(_score_event(f"clean-{index}", index, index * 0.5), index) for index in range(16)]
    return _build(
        name="clean",
        taxonomy="baseline",
        items=items,
        perturbation_time_s=None,
        recovery_target_event_id=None,
        fail_soft_policy="Maintain monotonic local lock.",
    )


def _wrong_note() -> RecoveryScenario:
    items = [(_score_event(f"wrong-{index}", index, index * 0.5), index) for index in range(5)]
    items.append((_noise("wrong-substitution-5", 2.5), None))
    items.extend(
        (_score_event(f"wrong-{index}", index, index * 0.5), index) for index in range(6, 16)
    )
    return _build(
        name="wrong_note",
        taxonomy="pitch_substitution",
        items=items,
        perturbation_time_s=2.5,
        recovery_target_event_id="wrong-6",
        fail_soft_policy="Ignore the unmatched substitution and preserve local score context.",
    )


def _missing_note() -> RecoveryScenario:
    items = [
        (_score_event(f"missing-{index}", index, index * 0.5), index)
        for index in range(16)
        if index != 5
    ]
    return _build(
        name="missing_note",
        taxonomy="deletion",
        items=items,
        perturbation_time_s=2.5,
        recovery_target_event_id="missing-6",
        fail_soft_policy="Permit a bounded forward skip when the next observed pitch is unambiguous.",
    )


def _extra_note() -> RecoveryScenario:
    items = [(_score_event(f"extra-{index}", index, index * 0.5), index) for index in range(16)]
    items.append((_noise("extra-noise", 2.25), None))
    return _build(
        name="extra_note",
        taxonomy="insertion",
        items=items,
        perturbation_time_s=2.25,
        recovery_target_event_id="extra-5",
        fail_soft_policy="Reject unmatched inserted observations without advancing score position.",
    )


def _pause() -> RecoveryScenario:
    items = []
    for index in range(16):
        onset = index * 0.5 + (2.0 if index >= 6 else 0.0)
        items.append((_score_event(f"pause-{index}", index, onset), index))
    return _build(
        name="pause",
        taxonomy="temporal_gap",
        items=items,
        perturbation_time_s=3.0,
        recovery_target_event_id="pause-6",
        fail_soft_policy="Do not advance during silence; resume from preserved local context.",
    )


def _restart() -> RecoveryScenario:
    items = [(_score_event(f"restart-pre-{index}", index, index * 0.5), index) for index in range(10)]
    items.extend(
        (_score_event(f"restart-new-{index}", index, 7.0 + index * 0.5), index)
        for index in range(16)
    )
    return _build(
        name="restart",
        taxonomy="restart_from_beginning",
        items=items,
        perturbation_time_s=7.0,
        recovery_target_event_id="restart-new-0",
        fail_soft_policy="After a long gap, permit explicit global re-lock instead of forcing monotonic advance.",
    )


def _repeat() -> RecoveryScenario:
    items = [(_score_event(f"repeat-pre-{index}", index, index * 0.5), index) for index in range(12)]
    items.extend(
        (_score_event(f"repeat-loop-{index}", index, 6.0 + (index - 4) * 0.5), index)
        for index in range(4, 8)
    )
    items.extend(
        (_score_event(f"repeat-post-{index}", index, 8.0 + (index - 12) * 0.5), index)
        for index in range(12, 16)
    )
    return _build(
        name="repeat",
        taxonomy="local_repeat",
        items=items,
        perturbation_time_s=6.0,
        recovery_target_event_id="repeat-loop-4",
        fail_soft_policy="Allow bounded backward re-lock for repeated score regions.",
    )


def _skip() -> RecoveryScenario:
    items = [(_score_event(f"skip-pre-{index}", index, index * 0.5), index) for index in range(6)]
    items.extend(
        (_score_event(f"skip-post-{index}", index, 3.0 + (index - 10) * 0.5), index)
        for index in range(10, 16)
    )
    return _build(
        name="skip",
        taxonomy="forward_jump",
        items=items,
        perturbation_time_s=3.0,
        recovery_target_event_id="skip-post-10",
        fail_soft_policy="Permit a bounded forward jump and record skipped score events explicitly.",
    )


def _backward_jump() -> RecoveryScenario:
    items = [
        (_score_event(f"backward-pre-{index}", index, index * 0.5), index) for index in range(11)
    ]
    items.extend(
        (_score_event(f"backward-post-{index}", index, 5.5 + (index - 7) * 0.5), index)
        for index in range(7, 16)
    )
    return _build(
        name="backward_jump",
        taxonomy="backward_jump",
        items=items,
        perturbation_time_s=5.5,
        recovery_target_event_id="backward-post-7",
        fail_soft_policy="Permit bounded backward re-lock and expose the discontinuity in audit metrics.",
    )


def _tempo_change() -> RecoveryScenario:
    items: list[tuple[PerformanceEventV1, int | None]] = []
    onset = 0.0
    for index in range(16):
        if index > 0:
            onset += 0.5 if index <= 7 else 0.32
        items.append((_score_event(f"tempo-{index}", index, onset), index))
    target_time = next(event.observed_at_s for event, _ in items if event.event_id == "tempo-8")
    return _build(
        name="tempo_change",
        taxonomy="tempo_change",
        items=items,
        perturbation_time_s=target_time,
        recovery_target_event_id="tempo-8",
        fail_soft_policy="Keep position matching causal and avoid forcing a fixed performance clock.",
    )


def _rubato() -> RecoveryScenario:
    intervals = (0.42, 0.58, 0.36, 0.64, 0.47, 0.53)
    items: list[tuple[PerformanceEventV1, int | None]] = []
    onset = 0.0
    for index in range(16):
        if index > 0:
            onset += intervals[(index - 1) % len(intervals)]
        items.append((_score_event(f"rubato-{index}", index, onset), index))
    return _build(
        name="rubato",
        taxonomy="expressive_timing",
        items=items,
        perturbation_time_s=None,
        recovery_target_event_id=None,
        fail_soft_policy="Preserve observed timing while matching position from symbolic content.",
    )


def recovery_scenarios() -> tuple[RecoveryScenario, ...]:
    return (
        _clean(),
        _wrong_note(),
        _missing_note(),
        _extra_note(),
        _pause(),
        _restart(),
        _repeat(),
        _skip(),
        _backward_jump(),
        _tempo_change(),
        _rubato(),
    )


def evaluate_recovery_result(
    result: FollowerRunResult,
    scenario: RecoveryScenario,
) -> RecoveryScenarioMetrics:
    raw_matches = result.backend_metrics.get("matches", [])
    if not isinstance(raw_matches, list):
        raise ValueError("recovery follower result must expose list-valued matches")
    predicted = {
        str(match["event_id"]): int(match["score_index"])
        for match in raw_matches
        if isinstance(match, dict)
    }
    truth = {item.event_id: item.expected_score_index for item in scenario.truth}

    valid_ids = [event_id for event_id, expected in truth.items() if expected is not None]
    noise_ids = [event_id for event_id, expected in truth.items() if expected is None]
    correct = sum(predicted.get(event_id) == truth[event_id] for event_id in valid_ids)
    missed = sum(event_id not in predicted for event_id in valid_ids)
    wrong = sum(
        event_id in predicted and predicted[event_id] != truth[event_id] for event_id in valid_ids
    )
    noise_rejected = sum(event_id not in predicted for event_id in noise_ids)
    mapping_accuracy = correct / len(valid_ids) if valid_ids else 1.0
    noise_rejection_rate = noise_rejected / len(noise_ids) if noise_ids else 1.0

    relock_time: float | None = None
    relock_observations: int | None = None
    if scenario.recovery_target_event_id is not None and scenario.perturbation_time_s is not None:
        target_id = scenario.recovery_target_event_id
        target_truth = truth[target_id]
        target_event = next(event for event in scenario.events if event.event_id == target_id)
        if predicted.get(target_id) == target_truth:
            relock_time = max(0.0, target_event.observed_at_s - scenario.perturbation_time_s)
            relock_observations = sum(
                scenario.perturbation_time_s <= event.observed_at_s <= target_event.observed_at_s
                for event in scenario.events
            )

    passed = (
        correct == len(valid_ids)
        and wrong == 0
        and noise_rejected == len(noise_ids)
    )
    return RecoveryScenarioMetrics(
        scenario=scenario.name,
        taxonomy=scenario.taxonomy,
        valid_observations=len(valid_ids),
        noise_observations=len(noise_ids),
        correct_mappings=correct,
        missed_valid_observations=missed,
        wrong_mappings=wrong,
        noise_rejected=noise_rejected,
        mapping_accuracy=mapping_accuracy,
        noise_rejection_rate=noise_rejection_rate,
        relock_performance_time_s=relock_time,
        relock_observations=relock_observations,
        passed=passed,
        fail_soft_policy=scenario.fail_soft_policy,
    )
