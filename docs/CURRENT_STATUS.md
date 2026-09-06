# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent benchmark evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **active; bounded streaming foundation implemented, CI evidence pending**.

## SF-02 implemented on active branch

- ST-owned bounded stream ingress.
- Explicit `reject_newest` and `drop_oldest` overflow policies with counters.
- Per-packet sequence IDs and canonical monotonic arrival timestamps.
- Close/drain semantics that do not require sacrificing a queued payload for a sentinel.
- Bounded raw-byte backend bridge with explicit full-queue timeout behavior.
- Ingress-to-backend-queue transport-latency instrumentation.
- Matchmaker adapter support for custom streams and ST-clock follower emission timestamps.
- Real Matchmaker `BytesMidiStream` integration test using synthetic Web-MIDI-style note bytes.
- Streaming smoke benchmark that reports queue pressure, transport timing and score-position progress.

## Evidence level

SF-00 and SF-01 are validated. SF-02 is implemented but remains active until the new unit/integration tests and streaming benchmark are green in CI. The synthetic byte-stream test is not physical microphone evidence and does not claim full acoustic end-to-end latency.

## Next safe action

Run SF-02 CI. If the real Matchmaker byte-stream path is green, record the streaming benchmark output, then extend the input abstraction toward PCM/audio chunks and optional local microphone capture without making microphone hardware a CI dependency.
