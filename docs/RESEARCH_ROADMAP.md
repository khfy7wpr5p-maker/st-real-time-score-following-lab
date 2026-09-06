# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Next / active preparation |
| SF-03 | Symbolic following path | Planned |
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

### SF-00

Core contracts, stream-relative clock/latency primitives, deterministic tests, architecture/benchmark/data-governance documentation and Python 3.11/3.12 CI are complete.

### SF-01

A real `pymatchmaker==0.3.0` integration runs in CI using a repository-owned synthetic 16-note MusicXML/MIDI fixture. The clean deterministic baseline produced 16/16 aligned events with zero failures. Exact metrics, timing, backend observations and limitations are recorded in `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md`.

This result proves baseline reproducibility and adapter functionality only; it is not a representative performance-accuracy claim.

## SF-02 immediate research slice

1. ST-owned bounded stream ingress with explicit overflow policy.
2. Monotonic ST arrival timestamps independent of backend wall clocks.
3. Synthetic MIDI/byte producer-consumer tests.
4. Matchmaker byte-stream bridge behind the follower adapter.
5. Realtime score-position smoke benchmark without requiring physical microphone hardware.
6. Latency instrumentation that clearly distinguishes ST ingress timing, backend processing timing and end-to-end evidence.

A stage is not "complete" merely because code exists. Completion requires the evidence defined by its exit criteria and benchmark protocol.
