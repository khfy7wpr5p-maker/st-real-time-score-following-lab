# SF-06 Robustness and Recovery Evidence

Date: 2026-09-07

## Scope

This report records deterministic repository-owned symbolic recovery evidence. It measures recovery-state behavior and fail-soft policies; it does not claim microphone, AMT, repeated-pitch ambiguity, or real-performance robustness.

Backend: `st-symbolic-recovery` 0.1.0

Method: `bounded_bidirectional_pitch_recovery`

## Scenario coverage

The suite contains a clean control plus all required perturbations:

1. wrong note / pitch substitution;
2. missing note;
3. extra note;
4. pause;
5. restart from beginning;
6. local repeat;
7. forward skip;
8. backward jump;
9. tempo change;
10. rubato.

## CI evidence

Implementation run: `34088656310` after lint cleanup.

The independent recovery job and the Python 3.11/3.12 core jobs passed on the implementation head. Existing Matchmaker regression jobs are also retained in the workflow.

Initial runtime evidence was already produced in run `34088507375`; the exact aggregate values were reproduced by the recovery benchmark after the formatting-only cleanup.

## Aggregate results

- scenarios: 11
- passed scenarios: 11
- valid observations: 188
- correct mappings: 188
- mapping accuracy: 100%
- injected noise observations: 2
- injected noise rejected: 2
- noise rejection rate: 100%
- global re-locks: 1
- maximum declared re-lock observations: 2
- maximum declared re-lock performance time: 2.0 s

The 2.0 s maximum is the pause scenario and includes the deliberately injected silence. It is not CPU processing latency.

## Per-scenario results

| Scenario | Valid mapping | Noise rejection | Declared re-lock | Key recovery evidence |
|---|---:|---:|---:|---|
| clean | 16/16 | n/a | n/a | monotonic local lock |
| wrong_note | 15/15 | 1/1 | 0.5 s / 2 obs | unmatched substitution ignored; bounded forward recovery |
| missing_note | 15/15 | n/a | 0.5 s / 1 obs | one explicit skipped score event |
| extra_note | 16/16 | 1/1 | 0.25 s / 2 obs | inserted noise rejected without advancing |
| pause | 16/16 | n/a | 2.0 s / 1 obs | one temporal gap; local context preserved |
| restart | 26/26 | n/a | 0.0 s / 1 obs | one global gap re-lock and one restart re-lock |
| repeat | 20/20 | n/a | 0.0 s / 1 obs | one bounded backward jump |
| skip | 12/12 | n/a | 0.0 s / 1 obs | four forward-skipped score events |
| backward_jump | 20/20 | n/a | 0.0 s / 1 obs | one bounded backward jump |
| tempo_change | 16/16 | n/a | 0.0 s / 1 obs | position lock survives interval change |
| rubato | 16/16 | n/a | n/a | expressive timestamps preserved |

## Auditability

Every accepted observation records:
- event id;
- resolved score index and beat;
- observed time;
- pitch-set similarity;
- transition type;
- search scope;
- inter-observation gap;
- propagated confidence when available.

Unmatched observations are visible counters rather than silently moved or coerced into score positions.

## Confidence boundary

No follower confidence is invented. Repository-owned scenario inputs carry explicit uncalibrated oracle provenance. If an input confidence is unavailable, the follower preserves that unavailability.

## Limitations

The reference pitch sequence is intentionally unique so the stage isolates recovery-state mechanics. Repeated-pitch ambiguity, probabilistic candidate ranking, microphone capture, AMT errors, and real musician recovery remain future evidence work.

## Exit statement

SF-06 is complete for the repository-owned deterministic recovery benchmark and failure taxonomy. The next autonomous stage is SF-07 performance alignment.
