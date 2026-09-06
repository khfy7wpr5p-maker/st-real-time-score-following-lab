# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent benchmark evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime streaming evidence; physical microphone validation remains environment-specific**.
- SF-03 Symbolic Following Path: **next autonomous stage**.

## SF-02 completed scope

- ST-owned bounded stream ingress with explicit `reject_newest` and `drop_oldest` policies.
- Per-packet sequence IDs and canonical monotonic arrival timestamps.
- Bounded backend bridge with observable queue pressure and explicit timeout/cancellation behavior.
- Mean/P95/max latency summaries for transport and ST ingress-to-follower-update boundaries.
- Timestamp-observed backend queue that preserves Matchmaker's plain byte contract.
- Matchmaker custom-stream adapter with live-input `on_ready` lifecycle hook after score preprocessing.
- Real `pymatchmaker==0.3.0` synthetic Web-MIDI byte-stream integration.
- Realtime-paced float32 PCM `BytesAudioStream` integration at 44.1 kHz / nominal 30 frames/s.
- Consumer-complete cancellation so a producer cannot keep filling a bounded queue after the follower reaches score end.

## SF-02 evidence

Final evidence run `34057173502` passed Python 3.11/3.12 core CI, three Matchmaker integration tests, and all baseline/streaming benchmarks.

Synthetic PCM reached score beat 15.0 with 226 position updates. Ingress depth remained at most 1/4 with zero rejected/dropped chunks; ST ingress-to-follower-update latency was mean 2.852 ms, P95 2.969 ms and max 7.038 ms. MIDI byte streaming reached beat 15.0 with 16 updates; all 32 payloads were ultimately accepted and forwarded.

Exact results and measurement boundaries are in `benchmarks/reports/SF02_REALTIME_STREAMING.md`.

## Evidence limits

- No physical microphone or acoustic-room path is claimed.
- The PCM fixture is deterministically rendered from repository-owned synthetic score material.
- The reported pipeline latency begins at ST ingress; hardware/ADC/browser/network latency is outside the boundary.
- Matchmaker does not provide calibrated confidence for these updates, so confidence remains unavailable rather than fabricated.
- SF-02 is transport/realtime architecture evidence, not violin/guitar/orchestra robustness evidence.

## Next safe action

Proceed autonomously to SF-03. Add an ST-owned transcription-observation adapter contract and a comparable audio-only vs symbolic-observation benchmark without assuming that symbolic following is automatically superior. Use synthetic/oracle observations only as architecture evidence until a real transcription model is separately validated.
