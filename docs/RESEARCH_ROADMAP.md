# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Complete — same-material comparison + evidence report |
| SF-04 | Solo violin | Next — dataset/license audit required before real-instrument evidence |
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

A real `pymatchmaker==0.3.0` integration runs in CI using a repository-owned synthetic 16-note MusicXML/MIDI fixture. The deterministic baseline produced 16/16 aligned events with zero failures. Exact evidence is in `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md`.

### SF-02

ST-owned bounded ingestion drives Matchmaker through raw MIDI bytes and realtime-paced float32 PCM bytes. Exact lifecycle and latency-boundary evidence is in `benchmarks/reports/SF02_REALTIME_STREAMING.md`. Physical microphone/ADC/driver latency is outside this evidence.

### SF-03

A model-independent transcription contract and an ST-owned causal symbolic follower were evaluated beside direct Matchmaker audio following on the same repository-owned 16-note material. Final CI run `34058190673` passed Python 3.11/3.12 and all Matchmaker integration/benchmark steps. Audio-only mean absolute onset error was 20.833 ms with P95 333.333 ms; the perfect oracle symbolic path was 0 ms across 16/16 events. The oracle result is an architecture upper bound, not real AMT evidence. Exact results are in `benchmarks/reports/SF03_SYMBOLIC_COMPARISON.md`.

## SF-04 entry rule

Before real violin data is downloaded, copied or committed, record source, version, license, permitted use and integrity metadata according to `DATASET_GOVERNANCE.md`. Repository-owned or procedurally synthetic scaffolding may proceed autonomously, but it cannot satisfy real-instrument robustness claims.

A stage is complete only when its stated evidence exists; code presence alone is insufficient.
