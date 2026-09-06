# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Active — implementation + same-material comparison pending CI |
| SF-04 | Solo violin | Planned; license gates apply |
| SF-05 | Classical guitar | Planned; high priority; dataset license gates apply |
| SF-06 | Robustness and recovery | Planned |
| SF-07 | Performance alignment | Planned |
| SF-08 | Performance error intelligence foundation | Planned |
| SF-09 | Duet research | Planned |
| SF-10 | Quartet / multi-channel ensemble | Planned |
| SF-11 | Mixed ensemble | Planned |
| SF-12 | Orchestra global score following | Planned |
| SF-13 | Orchestra section research | Planned |
| SF-14 | Production candidate extraction | Planned |

## Completed evidence

### SF-01

A real `pymatchmaker==0.3.0` integration runs in CI using a repository-owned synthetic 16-note MusicXML/MIDI fixture. The clean deterministic baseline produced 16/16 aligned events with zero failures. Exact metrics, timing, backend observations and limitations are recorded in `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md`.

### SF-02

ST-owned bounded ingestion drives Matchmaker through both raw MIDI bytes and realtime-paced float32 PCM bytes. Exact numbers, lifecycle findings and latency boundaries are recorded in `benchmarks/reports/SF02_REALTIME_STREAMING.md`. Physical microphone/ADC/driver latency is outside this evidence and is not claimed.

## SF-03 active slice

1. Reuse `PerformanceEventV1` as the backend-neutral note observation, preserving timestamp, pitch evidence and confidence provenance.
2. Keep `TranscriptionAdapter` model-independent; do not hard-wire an AMT backend.
3. Establish a causal forward-only symbolic follower with bounded lookahead and explicit failure counters.
4. Compare audio-only and symbolic-observation paths on the same repository-owned synthetic material with the same onset-alignment metrics.
5. Treat oracle transcription as an architecture upper bound only.
6. Record conditions and limitations instead of assuming symbolic following is automatically superior.

A stage is not complete merely because code exists. Completion requires green CI and permanent benchmark evidence.
