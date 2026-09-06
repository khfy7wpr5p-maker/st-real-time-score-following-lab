# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Active — bounded byte-stream foundation, CI pending |
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

## SF-02 active slice

1. Bounded ST-owned ingestion with explicit overflow behavior.
2. Monotonic arrival and follower-emission timestamps independent of backend wall clocks.
3. Synthetic MIDI-byte producer/consumer coverage.
4. Real Matchmaker byte-stream bridge and score-position smoke benchmark.
5. PCM/audio byte path after the MIDI streaming baseline is green.
6. Optional physical microphone validation after architecture works without hardware.

A stage is not "complete" merely because code exists. Completion requires the evidence defined by its exit criteria and benchmark protocol.
