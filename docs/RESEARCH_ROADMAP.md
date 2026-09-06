# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Complete — same-material comparison + evidence report |
| SF-04 | Solo violin | Active — STRAdi interface/preflight autonomous; real asset/audio evidence license-gated |
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

SF-01, SF-02 and SF-03 have permanent reports under `benchmarks/reports/`.

## SF-04 active slice

1. Keep STRAdi execution isolated from the Python 3.11/3.12 ST core because the paper environment uses an older PyTorch/Python stack.
2. Adapt external `onset,offset,midi_number` output into `PerformanceEventV1` without fabricating confidence.
3. Validate adapter and follower semantics with repository-owned synthetic CSV data.
4. Do not download or copy checkpoint/example-audio assets while their applicable terms remain unconfirmed.
5. After the narrow license gate is cleared, run causal violin transcription, measure pitch/onset/inference latency, feed observations into symbolic following, and add recovery/tempo-variation evidence.

SF-04 remains incomplete until real violin research evidence is reproducible.
