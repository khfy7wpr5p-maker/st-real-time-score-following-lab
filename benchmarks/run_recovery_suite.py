from __future__ import annotations

import json

from st_score_following import RecoveryAwareSymbolicFollower
from st_score_following.evaluation import (
    evaluate_recovery_result,
    recovery_scenarios,
    recovery_score_events,
)


def run() -> dict[str, object]:
    scenario_outputs: list[dict[str, object]] = []
    total_valid = 0
    total_correct = 0
    total_noise = 0
    total_noise_rejected = 0
    global_relocks = 0
    max_relock_time = 0.0
    max_relock_observations = 0

    for scenario in recovery_scenarios():
        result = RecoveryAwareSymbolicFollower(recovery_score_events()).run_events(scenario.events)
        metrics = evaluate_recovery_result(result, scenario)
        relock_time = metrics.relock_performance_time_s
        relock_observations = metrics.relock_observations
        if relock_time is not None:
            max_relock_time = max(max_relock_time, relock_time)
        if relock_observations is not None:
            max_relock_observations = max(max_relock_observations, relock_observations)
        total_valid += metrics.valid_observations
        total_correct += metrics.correct_mappings
        total_noise += metrics.noise_observations
        total_noise_rejected += metrics.noise_rejected
        global_relocks += int(result.backend_metrics["global_relocks"])

        scenario_outputs.append(
            {
                **metrics.to_dict(),
                "follower": {
                    "matched_events": result.backend_metrics["matched_events"],
                    "unmatched_observations": result.backend_metrics["unmatched_observations"],
                    "pause_gaps": result.backend_metrics["pause_gaps"],
                    "forward_skipped_score_events": result.backend_metrics[
                        "forward_skipped_score_events"
                    ],
                    "backward_jumps": result.backend_metrics["backward_jumps"],
                    "restart_relocks": result.backend_metrics["restart_relocks"],
                    "global_relocks": result.backend_metrics["global_relocks"],
                },
            }
        )

    passed = sum(bool(output["passed"]) for output in scenario_outputs)
    return {
        "schema": "st.score_following.robustness_recovery.v1",
        "backend": "st-symbolic-recovery",
        "backend_version": "0.1.0",
        "method": "bounded_bidirectional_pitch_recovery",
        "scenario_count": len(scenario_outputs),
        "passed_scenarios": passed,
        "aggregate": {
            "valid_observations": total_valid,
            "correct_mappings": total_correct,
            "mapping_accuracy": total_correct / total_valid,
            "noise_observations": total_noise,
            "noise_rejected": total_noise_rejected,
            "noise_rejection_rate": (
                total_noise_rejected / total_noise if total_noise else 1.0
            ),
            "max_relock_performance_time_s": max_relock_time,
            "max_relock_observations": max_relock_observations,
            "global_relocks": global_relocks,
        },
        "failure_taxonomy": [
            {
                "scenario": scenario.name,
                "taxonomy": scenario.taxonomy,
                "fail_soft_policy": scenario.fail_soft_policy,
            }
            for scenario in recovery_scenarios()
        ],
        "scenarios": scenario_outputs,
        "metric_boundaries": [
            (
                "mapping_accuracy measures event-id truth mappings on repository-owned "
                "symbolic perturbation scenarios."
            ),
            (
                "relock_performance_time_s is measured on the synthetic performance timeline "
                "from each declared perturbation boundary to the first declared recovery target."
            ),
            (
                "For pause, relock performance time includes the injected silent interval; "
                "it is not CPU processing latency."
            ),
        ],
        "limitations": [
            "Reference pitches are intentionally unique to isolate recovery-state behavior.",
            "Input observations are synthetic symbolic truth, not microphone or AMT output.",
            "Repeated-pitch ambiguity and probabilistic candidate ranking remain future work.",
            "No follower confidence is synthesized; input oracle confidence is uncalibrated.",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
