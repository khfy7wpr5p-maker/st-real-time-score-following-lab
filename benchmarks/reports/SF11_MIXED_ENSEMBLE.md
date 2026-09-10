# SF-11 Mixed Ensemble — Permanent Evidence

Date: 2026-09-10

## Scope

SF-11 establishes a repository-owned, deterministic, channel-separated mixed-ensemble research layer over the existing independent recovery followers. It adds explicit instrument-family, observation-path, and timing-basis provenance without turning heterogeneous observations into a new score authority.

Authority boundary: `mixed_ensemble_channel_separated_research_not_acoustic_mixture_authority`.

This evidence does **not** establish acoustic mono-mixture source separation, real-room mixed-instrument generalization, calibrated cross-model latency correction, orchestra-scale following, or pedagogical grading.

## Validation

Implementation head: `a694a4ff088ed7ef45192fca77032a283dc0410a`.

CI run `34529350858` passed all 9 jobs on that head:
- Python 3.11 Ruff + full pytest;
- Python 3.12 Ruff + full pytest;
- mixed-ensemble benchmark;
- quartet regression;
- duet regression;
- robustness/recovery regression;
- performance-alignment regression;
- error-intelligence regression;
- Matchmaker integrations plus SF-01/SF-02/SF-03/SF-05 benchmark chain.

The initial implementation run exposed four Ruff-only style violations. They were fixed without changing mixed-ensemble behavior; the evidence below is from the passing benchmark semantics retained on the validated head.

## Provenance model

The deterministic fixture represents four independent paths:
- piano: `direct_midi`;
- guitar: `transcription_symbolic`;
- violin: `external_event_adapter`;
- voice: `synthetic_oracle`.

All four retain stable part, performer, channel, and instrument-family identities. `PerformanceEventV1.observed_at_s` is not reinterpreted as model inference latency. Timing eligibility is represented separately by `ObservationTimingBasis`.

A path marked `unverified` can continue independent score following, but it is excluded from shared-position timing quorum and from pairwise timing evidence. Pairwise comparisons that cannot be justified produce explicit timing abstentions instead of fabricated values.

## Deterministic evidence

### Clean heterogeneous case

- 4 instrument families and 4 observation paths.
- All four parts matched 8/8 events and ended at score beat 7.
- 4 timing-comparable parts; all 6 part pairs comparable.
- 48 pairwise timing points.
- 32 shared snapshots: 29 full-consensus, 1 quorum-consensus, 0 divergent, 2 bootstrap insufficient-quorum.
- Mean absolute pairwise asynchrony: about 27.5 ms.
- Maximum absolute pairwise asynchrony: about 50 ms.
- Maximum shared-position spread: 1 beat.
- Shared confidence unavailable.

### Unverified voice timing

- Piano, guitar, violin, and voice each still matched 8/8 and ended at beat 7.
- Voice timing remains `unverified` and is not silently normalized or corrected.
- Timing-comparable parts: 3; timing-ineligible parts: 1.
- Comparable pairs: 3; abstained pairs: 3, exactly the voice-involving comparisons.
- 24 pairwise timing points from eligible pairs only.
- 24 shared snapshots: 22 quorum-consensus, 0 divergent, 2 bootstrap insufficient-quorum, 0 full-consensus because one of four parts is timing-ineligible.
- Maximum eligible-pair asynchrony: about 35 ms.
- The voice follower remains independently usable despite timing abstention.

### Unverified voice plus guitar pause

- All four independent followers still matched 8/8 and ended at beat 7.
- Guitar exposed one pause gap.
- Voice remained timing-ineligible.
- 3 comparable pairs and 3 explicit abstained pairs.
- 24 pairwise timing points.
- 24 shared snapshots: 12 quorum-consensus, 2 divergent, 10 insufficient-quorum; 8 of those are true post-bootstrap degraded insufficient-quorum snapshots.
- Maximum position spread: 3 beats.
- Maximum eligible-pair asynchrony: 1620 ms.
- The system degrades shared evidence without blocking independently valid parts.

### Dropped guitar event

- Piano 8/8, violin 8/8, voice 8/8.
- Guitar matched 7 observations and exposed one forward-skipped score event.
- All parts still ended at beat 7.
- No divergent shared snapshots.
- 45 pairwise timing points; maximum pairwise asynchrony about 50 ms.

### Advanced voice

- Piano, guitar, and violin remained 8/8.
- Voice matched 6 observations and exposed two forward-skipped score events.
- All parts ended at beat 7.
- 12 divergent shared snapshots.
- Maximum shared-position spread: 2 beats.
- 42 pairwise timing points.
- Mean absolute asynchrony about 294.524 ms; maximum about 985 ms.
- Divergence is exposed rather than forced into consensus.

## Safety and interpretation

The benchmark is synthetic, repository-owned, and channel-separated. `synthetic_oracle` is architecture evidence only and must not be interpreted as automatic-transcription accuracy. No inference latency is inferred from onset timestamps. No shared confidence is synthesized from unrelated path-level values. Asynchrony, divergence, quorum loss, and abstention are evidence states rather than quality grades.

## Exit

SF-11 is complete for deterministic channel-separated mixed-ensemble provenance and fail-soft timing semantics. SF-12 Orchestra Global Score Following is the next autonomous research stage. SF-04 real violin evidence remains a separate narrow rights gate.
