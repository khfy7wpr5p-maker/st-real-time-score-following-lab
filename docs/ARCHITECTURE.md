# Architecture

## High-level flow

`Live Performance → Audio/MIDI → Observation Layer → Follower Adapter → Score Position + Tempo + Confidence → Alignment → Performance Evidence`

## Boundaries

1. **Score truth** — validated symbolic score/timeline and semantic addresses.
2. **Observation** — timestamped audio features, MIDI events or causal symbolic events.
3. **Follower adapter** — ST-owned boundary around replaceable algorithms/backends.
4. **Score timeline mapping** — converts backend-native global beat estimates into canonical score addresses.
5. **Tempo** — independently inspectable tempo/beat state.
6. **Alignment** — score-event ↔ performance-event correspondence and recovery.
7. **Performance evidence** — pitch/timing/duration/missing/extra evidence, not pedagogical authority.

## Canonical contracts

The first stable research boundary is `src/st_score_following/contracts.py`:

- `score_position_v1`
- `observation_v1`
- `tempo_state_v1`
- `confidence_v1`
- `alignment_v1`
- `performance_event_v1`

Contracts are ST-owned even when algorithms behind them use external research libraries.

## Follower adapter layer

`src/st_score_following/followers/` owns backend-neutral research outputs:

- online global score-beat updates,
- backend/version/method identity,
- final score-beat ↔ performance-time alignment path,
- optional confidence only when the backend actually supplies it,
- wall/runtime evidence.

`MatchmakerAdapter` pins the currently evaluated backend to `pymatchmaker==0.3.0`. Matchmaker is
not forked and is not a runtime authority for the ST architecture.

A backend-native global score beat is not silently presented as a canonical measure/beat address.
Semantic score addressing is a separate score-timeline responsibility.

## Time model

All ST realtime modules use stream-relative monotonic seconds. Wall-clock time is not an alignment
primitive. Matchmaker's offline baseline additionally returns performance time in seconds on the
second row of its final alignment path.

## Research-to-production rule

Python remains authoritative for experimentation. C++ realtime extraction is considered only after
one or more paths show reproducible accuracy, latency, recovery and robustness evidence.
