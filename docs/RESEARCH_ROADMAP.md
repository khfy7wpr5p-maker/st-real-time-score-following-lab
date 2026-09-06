# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Next / autonomous |
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

ST-owned bounded ingestion now drives Matchmaker through both raw MIDI bytes and realtime-paced float32 PCM bytes. The final evidence run `34057173502` passed all core and Matchmaker integration jobs. PCM reached beat 15.0 at nominal 30 frames/s while bounded ingress remained at depth <= 1/4 with no rejected or dropped chunks; measured ST-ingress-to-follower-update P95 was 2.969 ms for the synthetic runner. The MIDI path also reached beat 15.0 and reports explicit queue-pressure and P95 latency metrics.

Exact numbers, lifecycle findings and latency boundaries are recorded in `benchmarks/reports/SF02_REALTIME_STREAMING.md`. Physical microphone/ADC/driver latency is outside this evidence and is not claimed.

## SF-03 next slice

1. Define a backend-neutral transcription observation contract including timestamp, pitch/note evidence and confidence provenance.
2. Add a causal transcription adapter boundary; do not hard-wire a specific AMT model.
3. Implement a symbolic follower baseline behind the shared follower interface.
4. Run audio-only and symbolic-observation paths on the same repository-owned synthetic material with comparable metrics.
5. Treat oracle/synthetic transcription as an architecture upper-bound only; it is not transcription-model performance evidence.
6. Record conditions where either path is better or worse rather than assuming symbolic is superior.

A stage is not complete merely because code exists. Completion requires the evidence defined by its exit criteria and benchmark protocol.
