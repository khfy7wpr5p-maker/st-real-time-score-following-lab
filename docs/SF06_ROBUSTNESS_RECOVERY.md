# SF-06 Robustness and Recovery

## Goal

Measure explicit fail-soft recovery behavior rather than assuming a follower remains locked under performance deviations.

## Recovery backend

`RecoveryAwareSymbolicFollower` is separate from the SF-03/SF-05 causal baseline. It uses:
- bounded forward and backward score search around the current position;
- exact pitch-set similarity by default, with a configurable similarity threshold;
- explicit unmatched-observation abstention;
- bounded forward skips for missing/skip behavior;
- bounded backward re-lock for repeats and backward jumps;
- global search only for initial acquisition, long-gap recovery, or a configured mismatch streak;
- propagated input confidence only; no synthesized follower confidence.

Every accepted match is stored as an auditable record containing event id, score index/beat, observed time, similarity, transition type, search scope, gap and propagated confidence.

## Repository-owned scenario suite

The suite contains clean control plus the required perturbations:
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

The reference pitch sequence is intentionally unique so SF-06 measures recovery-state behavior without hiding ambiguity behind repeated pitch classes.

## Metrics

- valid event-to-score mapping accuracy;
- injected-noise rejection rate;
- missed and wrong mappings;
- scenario pass/fail;
- performance-timeline re-lock interval at declared recovery boundaries;
- observations required to reach the declared recovery target;
- forward skips, backward jumps, pause gaps, restart/global re-lock counters;
- explicit failure taxonomy and fail-soft policy for each scenario.

Re-lock performance time is not CPU latency. In the pause scenario it intentionally includes injected silence.

## Interpretation boundary

This stage validates deterministic symbolic recovery logic. It does not establish microphone robustness, transcription robustness, repeated-pitch disambiguation or real-performance recovery quality. Those require instrument/audio evidence later.
