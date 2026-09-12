# Current Status

Date: 2026-09-12

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete**.
- SF-01 Matchmaker Baseline Reproduction: **complete; CI + permanent evidence**.
- SF-02 Realtime Microphone and Streaming Pipeline: **complete for repository-owned synthetic realtime evidence**.
- SF-03 Symbolic Following Path: **complete; audio-vs-oracle-symbolic comparison + permanent evidence**.
- SF-04 Solo Violin: **active external-evidence gate; autonomous STRAdi interface/preflight implemented, real model/data evidence gated by asset/audio usage confirmation**.
- SF-05 Classical Guitar: **complete for repository-owned structural synthetic evidence; real-corpus validation remains rights-gated**.
- SF-06 Robustness and Recovery: **complete for repository-owned deterministic symbolic recovery evidence**.
- SF-07 Performance Alignment: **complete for repository-owned deterministic post-performance analysis/export evidence**.
- SF-08 Performance Error Intelligence Foundation: **complete for repository-owned deterministic evidence-first error/deviation intelligence**.
- SF-09 Duet Research: **complete for repository-owned deterministic independent two-performer/part evidence**.
- SF-10 Quartet / Multi-Channel Ensemble: **complete for repository-owned deterministic independent four-channel evidence**.
- SF-11 Mixed Ensemble: **complete for repository-owned deterministic channel-separated heterogeneous provenance evidence**.
- SF-12 Orchestra Global Score Following: **complete for repository-owned deterministic global measure/beat structural evidence; real orchestral-audio validation remains dataset/license-gated**.
- SF-13 Orchestra Section Research: **next active autonomous research stage**.

## SF-04 narrow gate

- STRAdi-style CSV output is adapted into ST contracts without importing the legacy PyTorch stack into core.
- Missing external confidence remains explicitly unavailable rather than fabricated.
- No checkpoint or KRAISLER audio is materialized while applicable asset/audio terms remain unconfirmed.

SF-04 is not globally blocking the roadmap; only its real violin evidence exit is gated.

## SF-05 evidence

The repository-owned classical-guitar fixture exercises 16 onset positions with 4 chord onsets, 12 arpeggio onsets under sustained whole-measure bass, and explicit voice overlap.

Final SF-05 CI `34088140925` passed Python 3.11/3.12 Ruff + pytest, Matchmaker integrations, and all benchmark steps.

On the deterministic synthetic fixture:
- Matchmaker Arzt/chroma: 16/16 expected events, 0 ms mean/P95 onset error.
- Matchmaker Arzt/CQT: 16/16 expected events, 0 ms mean/P95 onset error.
- ST synthetic-oracle symbolic path: 16/16 expected events, 0 ms mean/P95 onset error.

These results establish structural pipeline behavior only. They do not establish real nylon-string timbre robustness, real performer generalization, or AMT accuracy.

## SF-06 evidence

`RecoveryAwareSymbolicFollower` is a separate recovery backend with bounded forward/backward search and explicit global re-lock only for initial acquisition, long gaps, or configured mismatch recovery.

The repository-owned suite contains clean control plus wrong note, missing note, extra note, pause, restart, repeat, skip, backward jump, tempo change, and rubato.

Evidence:
- 11/11 scenarios passed.
- 188/188 valid event-to-score mappings correct.
- 2/2 injected noise observations rejected.
- one explicit global restart re-lock.
- maximum declared re-lock: 2.0 s / 2 observations across aggregate dimensions; the 2.0 s is injected pause silence, not CPU latency.
- every accepted match exposes an audit record; confidence is propagated only when available and never fabricated.

See `benchmarks/reports/SF06_ROBUSTNESS_RECOVERY.md` and `docs/SF06_ROBUSTNESS_RECOVERY.md`.

## SF-07 evidence

SF-07 adds ST-owned post-performance alignment records with explicit provenance and optional confidence, plus stable JSON/CSV export.

Final implementation CI `34103541246` passed Python 3.11/3.12 Ruff + full pytest, the independent performance-alignment benchmark, SF-06 recovery regression, and the full Matchmaker/SF-01/SF-02/SF-03/SF-05 regression chain.

Repository-owned benchmark evidence at 120 BPM / 40 ms timing tolerance:
- clean: 8 points, 1 segment, 8/8 on-time, 7 local-tempo samples at 120 BPM;
- expressive: 6 points, 1 early / 3 on-time / 2 late, mean absolute segment deviation 36.667 ms, P95 90 ms, local-tempo range about 98.361–146.341 BPM;
- pause: 5 points, 2 segments, one explicit performance-gap boundary, no tempo estimate across the pause;
- backward jump: 6 points, 2 segments, one explicit score-discontinuity boundary, no negative/cross-boundary tempo.

Missing confidence remains null/blank in exports rather than being fabricated. These are deterministic post-processing fixtures and are not real musician performance-quality claims.

See `benchmarks/reports/SF07_PERFORMANCE_ALIGNMENT.md` and `docs/SF07_PERFORMANCE_ALIGNMENT.md`.

## SF-08 evidence

SF-08 adds an evidence-first performance error/deviation layer over SF-06 recovery and SF-07 alignment records. It explicitly separates measured/derived evidence from unsupported musical or pedagogical interpretation.

Implementation CI `34105618113` passed all 6 jobs: Python 3.11/3.12 Ruff + full pytest, recovery, performance alignment, error intelligence and the complete Matchmaker regression chain.

Repository-owned deterministic evidence:
- 6 observations -> 5 accepted alignment points;
- 5 evidence events: one timing-late (~80 ms), one performance gap, one score discontinuity, one unmatched observation and one one-event skipped score region;
- unmatched event identity is safely reconciled to `event-unmatched` at 0.25 s when the original observation stream makes that identity provable;
- 2 evidence events retain source confidence provenance and 3 keep confidence unavailable;
- 6 explicit abstentions cover unsupported pitch-error identity, unmatched semantics, articulation, dynamics, musical intent and pedagogical grading;
- no grade or severity score is produced.

See `benchmarks/reports/SF08_ERROR_INTELLIGENCE.md` and `docs/SF08_ERROR_INTELLIGENCE.md`.

## SF-09 evidence

SF-09 preserves two independent `RecoveryAwareSymbolicFollower` paths and derives a shared duet snapshot without replacing either part's alignment authority. Stale/unavailable/divergent states remain explicit, and shared confidence stays unavailable.

Implementation head CI `34394175788` passed all 7 jobs: Python 3.11/3.12 Ruff + full pytest, duet research, recovery, performance alignment, error intelligence and the complete Matchmaker/SF-01/SF-02/SF-03/SF-05 regression chain.

Repository-owned deterministic duet evidence:
- clean: both parts matched 8/8 score events and ended at beat 7; 8 common asynchrony points with ~20 ms mean/max absolute offset; 15 consensus snapshots, 0 divergent;
- one dropped part-B event: part A remained 8/8, part B matched 7 events and exposed one forward-skipped score event; both still ended at beat 7; 7 common asynchrony points with ~20 ms mean/max offset; 0 divergent snapshots;
- one performer pause: both parts still matched 8 events and ended at beat 7; part B exposed one pause gap; shared state produced 6 single-part and 4 divergent snapshots rather than blocking part A; max spread 4 beats and max absolute asynchrony 1520 ms;
- one performer advance: part A remained 8/8; part B matched 6 observations while exposing 2 forward-skipped score events; shared state exposed 3 divergent snapshots, max spread 2 beats, and max absolute asynchrony 980 ms.

The clean 1-beat maximum snapshot spread is a transient event-arrival ordering effect and stayed inside the configured consensus semantics; it is not reported as duet divergence. Asynchrony is evidence, not a quality grade. `authority_boundary` remains `duet_research_not_ensemble_authority`.

See `benchmarks/reports/SF09_DUET_RESEARCH.md` and `docs/SF09_DUET_RESEARCH.md`.

## SF-10 evidence

SF-10 preserves four independent recovery paths with stable part/performer/channel identity and introduces an explicit default 3-of-4 quorum for a derived quartet shared-position view. Below quorum, the global position is unavailable rather than inferred from too few channels.

Implementation CI `34395555183` passed all 8 jobs: Python 3.11/3.12 Ruff + full pytest, quartet research, duet regression, recovery, performance alignment, error intelligence and the complete Matchmaker/SF-01/SF-02/SF-03/SF-05 regression chain.

Repository-owned deterministic quartet evidence:
- clean: all four parts 8/8 to beat 7; 48 pairwise timing points; 29 full-consensus snapshots, no divergence; maximum pairwise offset 50 ms;
- one dropped part-D event: A/B/C remain 8/8, D=7 with one forward skip; all reach beat 7; no divergence;
- one paused part C: all four still 8/8; C exposes one pause gap; 2 divergent and 2 true post-bootstrap below-quorum snapshots; maximum spread 3 beats;
- one advancing part D: A/B/C remain 8/8; D=6 with two forward skips; 12 divergent snapshots; maximum spread 2 beats;
- two-channel loss: A/B continue to beat 7 while C/D stop at beat 2; 8 true post-bootstrap insufficient-quorum snapshots publish no shared beat or spread.

Shared confidence remains unavailable. Pairwise asynchrony and quorum loss are evidence, not performance grades. `authority_boundary` remains `quartet_multichannel_research_not_mixed_ensemble_authority`.

See `benchmarks/reports/SF10_QUARTET_MULTICHANNEL.md` and `docs/SF10_QUARTET_MULTICHANNEL.md`.

## SF-11 evidence

SF-11 preserves independent four-part following while making heterogeneous instrument-family, observation-path, and timing-basis provenance explicit. It does not reinterpret source event onset timestamps as model inference latency.

Implementation CI `34529350858` passed all 9 jobs on head `a694a4ff088ed7ef45192fca77032a283dc0410a`: Python 3.11/3.12 Ruff + full pytest, mixed-ensemble, quartet, duet, recovery, performance-alignment, error-intelligence, and the complete Matchmaker regression chain.

Repository-owned deterministic mixed-ensemble evidence:
- clean: piano/direct-MIDI, guitar/transcription-symbolic, violin/external adapter, and voice/synthetic-oracle each matched 8/8 and ended at beat 7; all 6 timing pairs were eligible and produced 48 timing points; 29 full-consensus snapshots and no divergence;
- unverified voice timing: all four followers still reached beat 7, but voice was excluded from shared timing; only 3 pairs remained comparable and the 3 voice-related pairs produced explicit abstentions;
- unverified voice plus guitar pause: all four followers remained 8/8; guitar exposed one pause gap; shared evidence produced 8 true degraded insufficient-quorum snapshots and 2 divergent snapshots while voice remained timing-ineligible;
- dropped guitar event: guitar exposed one forward skip while the other three remained 8/8; all reached beat 7 and no divergence was fabricated;
- advancing voice: voice exposed two forward skips, the other three remained 8/8, and 12 divergent snapshots exposed the disagreement instead of forcing consensus.

Shared confidence remains unavailable. `synthetic_oracle` is architecture evidence only. `authority_boundary` remains `mixed_ensemble_channel_separated_research_not_acoustic_mixture_authority`; no acoustic source separation, real-room ensemble generalization, inferred model latency, orchestra authority, or pedagogy is claimed.

See `benchmarks/reports/SF11_MIXED_ENSEMBLE.md` and `docs/SF11_MIXED_ENSEMBLE.md`.

## SF-12 evidence

SF-12 introduces a separate aggregate-texture follower whose authority is only the global orchestral measure/beat position. It does not scale the four-part follower by assumption and it deliberately carries no instrument/section transcription authority.

Implementation CI `34678255101` passed all 10 jobs on head `7f023613697a3ae999bb0f2ebc6fd86d5adbde72`: Python 3.11/3.12 Ruff + full pytest, orchestra-global, mixed-ensemble, quartet, duet, recovery, performance-alignment, error-intelligence, and the complete Matchmaker regression chain.

Repository-owned deterministic global evidence on a 32-point / 8-measure proxy:
- clean, controlled dense-texture, and tempo/rubato cases each mapped 32/32 received observations to the declared global point with zero position error;
- two omitted observations left 30/30 received observations correctly mapped while exposing two forward-skipped score points;
- a six-point forward skip was exposed and the first post-skip observation mapped correctly;
- a backward jump was exposed and the first post-jump observation mapped correctly;
- pause/restart exposed one pause, one restart re-lock, and one global re-lock; the first post-pause observation mapped to the restart target;
- benchmark confidence remained unavailable rather than being synthesized from texture similarity.

The clean CI sample measured ~0.0207 ms median / ~0.0258 ms P95 local Python matching work. This is **not** microphone/model/end-to-end realtime latency. Real dense-orchestral-audio accuracy, within-50/100/250/500-ms acoustic alignment, calibrated global confidence, and large repeated-score robustness remain unproven and require appropriately licensed real evidence.

`authority_boundary` is `global_measure_beat_research_not_per_instrument_transcription_authority`.

See `benchmarks/reports/SF12_ORCHESTRA_GLOBAL.md` and `docs/SF12_ORCHESTRA_GLOBAL.md`.

## Current autonomous direction

Proceed to SF-13 Orchestra Section Research. Research strings/winds/brass/section grouping and section-level observation/fusion feasibility without widening SF-12 global authority or making product promises. Preserve explicit provenance, abstention, confidence-unavailable behavior, and dataset/license gates.
