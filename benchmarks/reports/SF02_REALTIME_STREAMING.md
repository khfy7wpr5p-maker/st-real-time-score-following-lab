# SF-02 Realtime Streaming Evidence

Date: 2026-09-06

## Decision

SF-02 exit evidence is satisfied for the repository-owned synthetic streaming paths. A bounded ST-owned stream can drive real Matchmaker score-position updates from both MIDI bytes and realtime-paced float32 PCM bytes. This is architecture and transport evidence, not a claim about physical microphone, room-acoustic, or instrument-robustness performance.

## Reproduction environment

- GitHub Actions run: `34057173502`
- Matchmaker job: `101551076203`
- Runner: Ubuntu 24.04
- Python: 3.12.14
- Backend: `pymatchmaker==0.3.0`
- FluidSynth runtime installed by CI
- Repository-owned synthetic MusicXML fixture; no external dataset or private recording

The same final branch also passed Ruff and pytest on Python 3.11 and 3.12.

## MIDI byte-stream result

Fixture: `synthetic_piano_midi_bytes_v1`, Matchmaker `pthmm`.

- 16 score-position updates; maximum score beat 15.0.
- 32 payloads accepted and 32 forwarded.
- Ingress bound: 8 packets; observed maximum depth: 8.
- `rejected_newest`: 2 transient attempts; the producer retried until all 32 payloads were accepted, so the final synthetic sequence lost no event.
- `dropped_oldest`: 0; backend target timeouts: 0.
- Bridge transport latency: mean 1.455 ms, P95 6.280 ms, max 7.413 ms.
- ST ingress-to-follower-update latency: 16 samples; mean 1.033 ms, P95 4.066 ms, max 7.354 ms.
- Matchmaker calibrated confidence: unavailable; no value was fabricated.

This producer is a synthetic Web-MIDI-style byte stress/smoke path, not a physical MIDI device benchmark.

## PCM audio-stream result

Fixture: `synthetic_rendered_score_pcm_v1`, Matchmaker `arzt`.

- Deterministically rendered audio duration: 7.6 s.
- Sample rate: 44.1 kHz; hop length: 1470; nominal input rate: 30 frames/s.
- Live input starts only after Matchmaker reference-score preprocessing completes.
- 226 score-position updates; maximum score beat 15.0.
- 227 PCM chunks accepted and forwarded.
- Ingress bound: 4 chunks; observed maximum depth: 1.
- `rejected_newest`: 0; `dropped_oldest`: 0; backend target timeouts: 0.
- Bridge transport latency: mean 0.060 ms, P95 0.077 ms, max 0.144 ms.
- ST ingress-to-follower-update latency: 226 samples; mean 2.852 ms, P95 2.969 ms, max 7.038 ms.
- Consumer-complete cancellation: true. This is expected because the follower reached the end of the score before a final producer tail/padded frame needed to be forwarded.
- Matchmaker calibrated confidence: unavailable; no value was fabricated.

## Latency boundary

Two different quantities are intentionally reported:

1. `transport_latency`: ST ingress acceptance -> enqueue into the backend byte queue.
2. `pipeline_latency`: ST ingress acceptance timestamp of the most recently backend-consumed packet -> follower score-position update emission.

These numbers exclude physical microphone capture, operating-system audio driver latency, acoustic propagation, ADC latency, network transport, and frontend/browser buffering. They therefore must not be presented as full acoustic end-to-end latency.

## Lifecycle finding

An earlier implementation started the producer before Matchmaker completed reference-score preprocessing. The bounded queue correctly filled while no consumer existed. SF-02 now exposes an `on_ready` lifecycle hook: live producers start only after backend construction/preprocessing and immediately before stream consumption. A unit regression test protects the order `constructed -> ready -> run`.

## Exit conclusion

The SF-02 repository exit criterion is met by reproducible synthetic streaming evidence: bounded realtime-paced PCM and MIDI byte streams both drive score-position progress, queue pressure remains bounded and observable, overflow/cancellation behavior is explicit, and mean/P95/max latency is instrumented. Physical microphone/device validation remains a later environment-specific validation item rather than a CI requirement.
