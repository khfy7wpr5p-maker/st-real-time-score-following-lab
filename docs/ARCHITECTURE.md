# Architecture

## High-level flow

`Live Performance → Audio/MIDI → ST Bounded Ingress → Observation/Backend Adapter → Follower Adapter → Score Position + Tempo + Confidence → Alignment → Performance Evidence`

## Boundaries

1. **Score truth** — validated symbolic score/timeline and semantic addresses.
2. **ST stream ingress** — bounded capacity, explicit overflow behavior, sequence IDs and canonical monotonic arrival timestamps.
3. **Observation/backend bridge** — converts ST-owned packets into backend-specific byte/feature contracts without transferring clock authority.
4. **Follower adapter** — ST-owned boundary around replaceable algorithms/backends.
5. **Score timeline mapping** — converts backend-native global beat estimates into canonical score addresses.
6. **Tempo** — independently inspectable tempo/beat state.
7. **Alignment** — score-event ↔ performance-event correspondence and recovery.
8. **Performance evidence** — pitch/timing/duration/missing/extra evidence, not pedagogical authority.

## Canonical contracts

Stable research contracts remain ST-owned: `score_position_v1`, `observation_v1`, `tempo_state_v1`, `confidence_v1`, `alignment_v1` and `performance_event_v1`.

## Follower adapter layer

`MatchmakerAdapter` pins the currently evaluated backend to `pymatchmaker==0.3.0`, normalizes backend alignment-path representation drift, and never fabricates missing confidence. `run_stream` accepts custom backend streams while allowing follower-emission timestamps to come from the ST monotonic clock.

## Realtime streaming layer

`BoundedStreamIngress` owns accepted/rejected/dropped accounting and timestamps every accepted payload. `ByteQueueBridge` forwards raw bytes into a bounded backend queue and measures ST-ingress-to-backend-queue transport latency. Backend queue stalls are surfaced as errors after a retry budget rather than converted into silent data loss.

The default overflow policy is `reject_newest`, particularly for MIDI where arbitrary byte loss can damage note state. `drop_oldest` is available only as an explicit policy for observation types where freshness is preferable.

## Time model

ST canonical realtime timing uses stream-relative monotonic seconds. Wall-clock time is not an ST alignment/latency primitive. Third-party backends may maintain their own clocks internally, but those clocks do not replace ST arrival/emission timing.

## Research-to-production rule

Python remains authoritative for experimentation. C++ realtime extraction is considered only after one or more paths show reproducible accuracy, latency, recovery and robustness evidence.
