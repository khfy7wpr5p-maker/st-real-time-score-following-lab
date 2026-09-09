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
| SF-08 | Performance error intelligence foundation | Complete — evidence taxonomy, abstention contracts + CI evidence |
| SF-09 | Duet research | Complete — independent part following, derived shared position, asynchrony/fail-soft CI evidence |
| SF-10 | Quartet / multi-channel ensemble | Complete — 4-channel identity, 3-of-4 quorum, pairwise timing/fail-soft CI evidence |
| SF-11 | Mixed ensemble | Active — next autonomous stage |
| SF-12 | Orchestra global score following | Planned |
| SF-13 | Orchestra section research | Planned |
| SF-14 | Production candidate extraction | Planned |

## Completed evidence

SF-01, SF-02, SF-03, SF-05, SF-06, SF-07, SF-08, SF-09, and SF-10 have permanent reports under `benchmarks/reports/`.

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

## SF-08 completed evidence-first error-intelligence baseline

1. ST-owned evidence contracts separate measured/derived performance facts from unsupported pedagogical interpretation.
2. Initial evidence kinds cover timing early/late, unmatched observations, skipped score regions, score discontinuities and performance gaps.
3. Unsupported pitch-error identity, unmatched semantics, articulation, dynamics, musical intent and grading remain explicit abstentions.
4. Original `ConfidenceV1` provenance is retained when available; missing confidence remains missing and naked scalar recovery confidence is not promoted into calibrated provenance.
5. When source observations safely reconcile with recovery match IDs, unmatched evidence retains exact event ID and performance timestamp; otherwise the layer falls back to aggregate evidence rather than guessing.
6. Repository-owned benchmark emits 5 evidence events and 6 abstentions from a deterministic 6-observation fixture, including one ~80 ms timing-late event, one unmatched event, one skipped score event and two boundary events.
7. No severity score, student grade or pedagogical authority is emitted.
8. CI `34105618113` passed all 6 jobs including Python 3.11/3.12, recovery, performance alignment, SF-08 benchmark and the Matchmaker regression chain.
9. Permanent evidence is recorded in `benchmarks/reports/SF08_ERROR_INTELLIGENCE.md`.

## SF-09 completed duet baseline

1. `DuetPartInputV1` keeps stable part and performer identity and requires exactly two unique parts/performers.
2. Each part runs through its own recovery follower; no shared follower overwrites per-part alignment truth.
3. Shared snapshots use only recent non-stale part positions, derive their score beat by median, and expose `consensus`, `single_part`, or `divergent` state plus spread.
4. Shared confidence remains unavailable; per-part scalar confidence is not combined into a fabricated duet confidence.
5. Common aligned score beats produce signed/absolute inter-part onset asynchrony evidence.
6. Repository-owned cases cover clean 20 ms offset, one dropped observation, one-performer pause and one-performer advance/skip.
7. A dropped event preserves the unaffected part's 8/8 mapping while the affected part exposes one forward skip; pause and advance cases expose stale/single-part/divergent shared states rather than globally blocking.
8. Implementation CI `34394175788` passed all 7 jobs, including Python 3.11/3.12, duet/recovery/performance/error-intelligence benchmarks and the full Matchmaker regression chain.
9. Authority remains `duet_research_not_ensemble_authority`; mono-mixture source separation, quartet/orchestra behavior, conductor intent and pedagogy remain unproven.
10. Permanent evidence is recorded in `benchmarks/reports/SF09_DUET_RESEARCH.md`.

## SF-10 completed quartet / multi-channel baseline

1. `QuartetPartInputV1` requires exactly four unique part, performer and channel identities.
2. Every part runs through its own recovery follower; no shared state overwrites a part alignment.
3. The default global-position quorum is 3 of 4 recent parts.
4. Below quorum, `shared_score_beat` and spread remain null instead of being inferred from too few channels.
5. Shared snapshots distinguish `full_consensus`, `quorum_consensus`, `divergent`, and `insufficient_quorum` while retaining stale/unavailable IDs and coverage.
6. All six part pairs contribute signed/absolute timing-asynchrony evidence on common aligned score beats.
7. Clean evidence produced 48 pairwise points and no divergence; dropped-event evidence localized one forward skip to part D; pause and advance cases exposed degraded/divergent states without corrupting unaffected part results.
8. Two-channel-loss evidence produced 8 true post-bootstrap below-quorum snapshots with no shared position while the remaining A/B part followers continued independently.
9. Shared confidence stays unavailable and is never synthesized from per-part recovery scalars.
10. Implementation CI `34395555183` passed all 8 jobs, including Python 3.11/3.12, quartet/duet/recovery/performance/error-intelligence benchmarks and the full Matchmaker regression chain.
11. Authority remains `quartet_multichannel_research_not_mixed_ensemble_authority`; mono-mixture source separation, arbitrary ensemble scaling, real-room generalization, conductor intent and pedagogy remain unproven.
12. Permanent evidence is recorded in `benchmarks/reports/SF10_QUARTET_MULTICHANNEL.md`.

## SF-11 active plan

1. Add explicit heterogeneous instrument/observation-path identity without weakening independent part authority.
2. Keep repository-owned evidence synthetic and channel-separated initially; do not imply source separation from a mono room recording.
3. Compare mixed instrument-family timing/position evidence under a shared score while preserving source-specific provenance.
4. Reuse quorum only after defining what constitutes eligible/recent evidence across heterogeneous observation paths.
5. Keep shared confidence unavailable unless a calibrated combination method is independently validated.
6. Add fail-soft cases where one instrument path pauses, drops events, or diverges while other paths continue.
7. Preserve SF-09/SF-10 as regressions and isolate SF-11 claims from SF-12 orchestra authority.
8. Publish permanent mixed-ensemble evidence before advancing.
