# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Complete — same-material comparison + evidence report |
| SF-04 | Solo violin | Active — STRAdi interface/preflight autonomous; real asset/audio evidence license-gated |
| SF-05 | Classical guitar | Complete — repository-owned structural synthetic baseline + evidence; real corpus validation rights-gated |
| SF-06 | Robustness and recovery | Active — autonomous next stage |
| SF-07 | Performance alignment | Planned |
| SF-08 | Performance error intelligence foundation | Planned |
| SF-09 | Duet research | Planned |
| SF-10 | Quartet / multi-channel ensemble | Planned |
| SF-11 | Mixed ensemble | Planned |
| SF-12 | Orchestra global score following | Planned |
| SF-13 | Orchestra section research | Planned |
| SF-14 | Production candidate extraction | Planned |

## Completed evidence

SF-01, SF-02, SF-03 and SF-05 have permanent reports under `benchmarks/reports/`.

## SF-04 narrow external-evidence gate

1. Keep STRAdi execution isolated from the Python 3.11/3.12 ST core because the paper environment uses an older PyTorch/Python stack.
2. Adapt external `onset,offset,midi_number` output into `PerformanceEventV1` without fabricating confidence.
3. Do not download or copy checkpoint/example-audio assets while their applicable terms remain unconfirmed.
4. After the narrow license gate is cleared, run causal violin transcription, measure pitch/onset/inference latency, feed observations into symbolic following, and add real violin recovery/tempo evidence.

SF-04 remains incomplete until real violin research evidence is reproducible, but this does not block independent roadmap stages.

## SF-05 completed structural baseline

1. Repository-owned MusicXML covers chord onsets, arpeggiation, sustained bass and voice overlap.
2. Generic onset clustering converts note-level symbolic observations into polyphonic onset observations without fabricating confidence.
3. Matchmaker Arzt/chroma, Arzt/CQT and ST synthetic-oracle symbolic paths are evaluated against the same 16 expected onset positions.
4. Clean CI `34087889237` reports 0 failures and 0 ms mean/P95 onset error for all three paths on the deterministic synthetic material.
5. CQT is substantially slower than chroma in the captured offline CI sample, but this is not interpreted as an end-to-end real-time latency result.
6. No GuitarSet/GAPS media are materialized while the primary rights evidence trail is incomplete.

SF-05 synthetic structural exit is complete. Real-corpus guitar validation remains a separate external-evidence extension.

## SF-06 active plan

1. Build a recovery-aware symbolic follower without changing the SF-03/SF-05 causal baseline semantics.
2. Add repository-owned scenarios for wrong note, missing note, extra note, pause, restart, repeat, skip, backward jump, tempo change and rubato.
3. Record auditable event-to-score mappings, relock behavior, recovery time and fail-soft outcomes.
4. Publish a permanent robustness report and keep any unresolved failure modes visible.
