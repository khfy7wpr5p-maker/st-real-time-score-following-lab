# SF-12 Orchestra Global Score Following

Date: 2026-09-12

## Scope

SF-12 establishes a repository-owned deterministic baseline for **global orchestra measure/beat tracking only**. The follower consumes an aggregate pitch-class texture fingerprint for each observation and maps it to an ordered global score position. It does not emit or infer per-instrument transcription, section identity, source separation, conductor intent, or pedagogical judgment.

Authority boundary:

`global_measure_beat_research_not_per_instrument_transcription_authority`

## Implementation

`OrchestraGlobalFollower` operates over `OrchestraGlobalScorePointV1` and `OrchestraGlobalObservationV1`.

- score points carry global `measure_index`, `beat_in_measure`, `score_beat`, and an aggregate pitch-class texture fingerprint;
- observations carry event time, aggregate pitch-class texture, and optional source confidence;
- texture matching uses Jaccard similarity as a matching score only; it is **not** promoted to calibrated confidence;
- normal recovery uses bounded forward/backward search;
- initial acquisition and long-gap restart use global search first;
- a configured mismatch streak may trigger global re-lock;
- missing source confidence remains unavailable; a positive confidence gate abstains rather than inventing confidence;
- per-observation `processing_latency_ms` measures only local Python CPU matching work.

## Deterministic benchmark

Runner: `python benchmarks/run_orchestra_global.py`

Implementation CI: `34678255101`

Implementation head: `7f023613697a3ae999bb0f2ebc6fd86d5adbde72`

Environment captured by GitHub Actions: Ubuntu 24.04, Python 3.12.14.

The score fixture contains 32 global score points = 8 synthetic 4/4 measures. Each point owns a deterministic aggregate five-pitch-class texture signature. The dense-texture proxy removes one expected pitch class and injects one extra pitch class per observation.

| Scenario | Observations | Correct mappings | Mapping failures | Median position error | Recovery evidence | Median CPU match latency | P95 CPU match latency | Max CPU match latency |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| clean | 32 | 32 | 0 | 0 beats | n/a | 0.020669 ms | 0.025780 ms | 0.069827 ms |
| dense texture proxy | 32 | 32 | 0 | 0 beats | n/a | 0.020151 ms | 0.021511 ms | 0.041164 ms |
| tempo drift / rubato timestamps | 32 | 32 | 0 | 0 beats | n/a | 0.020250 ms | 0.021397 ms | 0.040073 ms |
| two missing observations | 30 | 30 | 0 | 0 beats | 2 forward-skipped score points exposed | 0.019593 ms | 0.020966 ms | 0.039271 ms |
| forward skip | 26 | 26 | 0 | 0 beats | first post-skip observation correct; 6 skipped points exposed | 0.018178 ms | 0.020761 ms | 0.038528 ms |
| backward jump | 34 | 34 | 0 | 0 beats | first post-jump observation correct; 1 backward jump exposed | 0.019798 ms | 0.020629 ms | 0.038242 ms |
| pause then restart | 32 | 32 | 0 | 0 beats | first post-pause observation correct; 1 pause + 1 restart/global re-lock | 0.017990 ms | 0.020330 ms | 0.044006 ms |

Across these deterministic observations, the received-event mapping failure rate is 0.0. Forward skip, backward jump, and pause/restart cases re-acquire the declared target on the first observation after the discontinuity, so the benchmark records one recovery observation and 0.0 seconds of additional recovery delay beyond that observation.

All benchmark observations intentionally carry no calibrated confidence. `confidence_available_matches` therefore remains 0 and no follower confidence is synthesized from texture similarity.

## What the evidence supports

The evidence supports the following narrow claims:

1. The ST contract can represent a global orchestral score position independently of per-instrument transcription.
2. The deterministic aggregate-texture matcher preserves exact global measure/beat identity on the repository-owned clean and controlled dense-texture proxies.
3. Bounded recovery can expose missing score positions and recover controlled forward/backward discontinuities.
4. Long-gap restart performs global re-lock before local continuation, preventing a nearby similar texture from silently shadowing an explicit restart.
5. Confidence unavailability remains explicit.
6. Local matching CPU cost is directly measurable and very small on this 32-point synthetic fixture.

## What the evidence does not support

This report does **not** establish:

- robustness on real orchestral audio or real concert-room acoustics;
- microphone, feature-extraction, transcription/model, driver, browser, network, or end-to-end latency;
- percent-within-50/100/250/500-ms acoustic alignment accuracy, because the synthetic global-position proxy does not provide a real-audio onset ground truth suitable for that metric;
- per-instrument or section transcription;
- acoustic source separation;
- reliable tracking under arbitrary repeated orchestral textures at large score scale;
- calibrated global confidence;
- conductor gesture/intent inference;
- production readiness or pedagogical authority.

Real orchestral audio validation remains dataset/license-gated. Per project governance, that narrow gate does not block repository-owned structural research.

## Stage disposition

SF-12 is **complete for repository-owned deterministic global measure/beat structural evidence with a well-characterized real-audio limitation**. This satisfies the stage exit without claiming that real orchestral score following is solved.

The next autonomous research stage is SF-13 Orchestra Section Research.
