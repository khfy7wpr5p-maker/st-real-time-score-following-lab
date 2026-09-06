# Streaming Pipeline

## Ownership boundary

ST owns ingestion capacity, overflow behavior and canonical monotonic arrival timestamps. Third-party follower streams remain adapters behind this boundary.

`producer → BoundedStreamIngress → ByteQueueBridge → backend byte queue → backend stream/processor → follower adapter`

## Bounded ingress

`BoundedStreamIngress` uses a fixed capacity and one explicit overflow policy:

- `reject_newest`: preserve already accepted events and tell the producer that the new item was not accepted. This is the default and is safer for MIDI, where silently dropping arbitrary bytes can corrupt musical state.
- `drop_oldest`: available for observation types where freshness is more valuable than preserving every accepted item.

Every accepted packet receives an increasing sequence ID and a `StreamClock` arrival timestamp. Closing an ingress is separate from payload data and wakes blocked consumers without needing to sacrifice an accepted packet for a sentinel.

## Backend bridge

`ByteQueueBridge` converts ST packets into the raw `bytes`/`None` queue contract expected by byte-stream backends such as Matchmaker `BytesMidiStream` and `BytesAudioStream`. The backend queue is also allowed to be bounded. If it stays full beyond the configured retry budget, the bridge raises instead of silently discarding data.

The bridge records ingress-to-backend-queue transport latency using the same ST monotonic clock. This is not called end-to-end performance latency: acoustic/device buffering, feature extraction and follower computation are separate components that must be instrumented independently.

## Matchmaker timing boundary

Matchmaker 0.3.0 byte streams use backend-owned wall-clock timing internally. ST does not adopt that wall clock as its canonical latency domain. `MatchmakerAdapter.run_stream` can stamp follower emissions with an injected ST monotonic clock while leaving backend-native performance timing available for backend-specific analysis.

## SF-02 evidence target

A repository-owned synthetic MIDI-byte producer must drive score-position updates through a bounded ST ingress and real Matchmaker byte stream in CI. Physical microphone/device capture remains a later optional validation path; it is not required to establish the safe streaming architecture.
