# Research Roadmap

| Stage | Focus | State |
|---|---|---|
| SF-00 | Foundation, architecture, contracts | Complete |
| SF-01 | Matchmaker baseline reproduction | Complete — CI + evidence report |
| SF-02 | Realtime microphone/streaming | Complete — bounded MIDI + realtime-paced PCM CI evidence |
| SF-03 | Symbolic following path | Complete — same-material comparison + evidence report |
| SF-04 | Solo violin | Active external-evidence gate — STRAdi interface/preflight autonomous; real asset/audio evidence rights-gated |
| SF-05 | Classical guitar | Complete — repository-owned structural synthetic baseline + evidence; real corpus validation rights-gated |
| SF-06 | Robustness and recovery | Complete — 11-scenario deterministic recovery suite + evidence |
| SF-07 | Performance alignment | Complete — post-performance analysis/export contracts + CI evidence |
| SF-08 | Performance error intelligence foundation | Active — next autonomous stage |
| SF-09 | Duet research | Planned |
| SF-10 | Quartet / multi-channel ensemble | Planned |
| SF-11 | Mixed ensemble | Planned |
| SF-12 | Orchestra global score following | Planned |
| SF-13 | Orchestra section research | Planned |
| SF-14 | Production candidate extraction | Planned |

## Completed evidence

SF-01, SF-02, SF-03, SF-05, SF-06, and SF-07 have permanent reports under `benchmarks/reports/`.

## SF-04 narrow external-evidence gate

1. Keep STRAdi execution isolated from the Python 3.11/3.12 ST core because the paper environment uses an older PyTorch/Python stack.
2. Adapt external `onset,offset,midi_number` output into `PerformanceEventV1` without fabricating confidence.
3. Do not download or copy checkpoint/example-audio assets while their applicable terms remain unconfirmed.
4. After the narrow rights gate is cleared, run causal violin transcription, measure pitch/onset/inference latency, feed observations into symbolic following, and add real violin recovery/tempo evidence.

SF-04 remains incomplete until real violin research evidence is reproducible, but this does not block independent roadmap stages.

## SF-05 completed structural baseline

1. Repository-owned MusicXML covers chord onsets, arpeggiation, sustained bass, and voice overlap.
2. Generic onset clustering converts note-level symbolic observations into polyphonic onset observations without fabricating confidence.
3. Matchmaker Arzt/chroma, Arzt/CQT, and ST synthetic-oracle symbolic paths are evaluated against the same 16 expected onset positions.
4. Final SF-05 CI reports 0 failures and 0 ms mean/P95 onset error for all three paths on deterministic synthetic material.
5. CQT is substantially slower than chroma in the captured offline CI sample, but this is not interpreted as an end-to-end real-time latency result.
6. No GuitarSet/GAPS media are materialized while the primary rights evidence trail is incomplete.

## SF-06 completed recovery baseline

1. Separate recovery backend preserves the simpler SF-03/SF-05 causal follower semantics.
2. Repository-owned scenarios cover wrong/missing/extra note, pause, restart, repeat, skip, backward jump, tempo change, and rubato plus clean control.
3. 188/188 valid mappings were correct and 2/2 injected noise observations were rejected across 11/11 passing scenarios.
4. Long-gap restart uses an explicit global re-lock; repeat and backward-jump cases use bounded backward search; missing/skip cases expose forward skips.
5. Re-lock metrics are defined on the synthetic performance timeline and are not mislabeled as CPU latency.
6. Failure taxonomy, fail-soft policy, and per-match audit records are retained in benchmark output.

## SF-07 completed performance-alignment baseline

1. ST-owned post-performance records preserve backend/method/input provenance and optional confidence.
2. Alignment paths are converted to score-time/performance-time, absolute offset, segment-relative deviation and timing classes.
3. Local tempo is computed only within valid forward-moving segments.
4. Pause gaps and non-forward score movement start explicit new segments, preventing bogus cross-boundary BPM.
5. Stable JSON and CSV exports retain missing confidence as missing.
6. Repository-owned clean, expressive, pause and backward-jump cases passed the independent benchmark.
7. CI `34103541246` passed Python 3.11/3.12, recovery, performance-alignment and the Matchmaker regression chain.
8. Permanent evidence is recorded in `benchmarks/reports/SF07_PERFORMANCE_ALIGNMENT.md`.

## SF-08 active plan

1. Define ST-owned performance error/deviation event contracts that distinguish measured facts from pedagogical interpretation.
2. Start with evidence available from current symbolic/alignment paths: timing deviation, unmatched/extra observations, skipped score regions, discontinuities and confidence provenance.
3. Preserve abstention when the system lacks sufficient evidence; do not transform unavailable confidence into certainty.
4. Add aggregation suitable for rehearsal review without turning research heuristics into grading authority.
5. Build deterministic repository-owned fixtures and failure taxonomy before considering model-based error intelligence.
6. Keep future pitch/articulation/dynamics intelligence modular so SF-08 does not hardwire one transcription model.
7. Publish permanent evidence before advancing to SF-09 duet research.
