# Architecture

## High-level flow

`Live Performance → Audio/MIDI → Observation Layer → Follower → ScorePosition + Tempo + Confidence → Alignment → Performance Evidence`

## Boundaries

1. **Score truth** — validated symbolic score/timeline and semantic addresses.
2. **Observation** — timestamped audio features, MIDI events or causal symbolic events.
3. **Follower** — replaceable algorithm producing estimated score position and uncertainty.
4. **Tempo** — independently inspectable tempo/beat state.
5. **Alignment** — score-event ↔ performance-event correspondence and recovery.
6. **Performance evidence** — pitch/timing/duration/missing/extra evidence, not pedagogical authority.

## Canonical contracts

The first stable research boundary is `src/st_score_following/contracts.py`:

- `score_position_v1`
- `observation_v1`
- `tempo_state_v1`
- `confidence_v1`
- `alignment_v1`
- `performance_event_v1`

Contracts are ST-owned even when algorithms behind them use external research libraries.

## Time model

All realtime modules use stream-relative monotonic seconds. Wall-clock time is not an alignment primitive. End-to-end latency is measured from observation/input timestamp to emitted result timestamp using the same monotonic domain.

## Research-to-production rule

Python remains authoritative for experimentation. C++ realtime extraction is considered only after one or more paths show reproducible accuracy, latency, recovery and robustness evidence.
