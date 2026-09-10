# SF-11 Mixed Ensemble

## Goal

Add heterogeneous instrument-family and observation-path provenance without treating every symbolic channel as timing-equivalent or claiming source separation from an acoustic mixture.

## Provenance boundary

`MixedEnsemblePartInputV1` extends stable part/performer/channel identity with:

- `instrument_family`;
- `observation_path`;
- `timing_basis`;
- `path_source`.

The initial repository-owned fixture deliberately uses four different families and four different paths: piano/direct MIDI, guitar/transcription-symbolic, violin/external-event-adapter, and voice/synthetic-oracle.

`SYNTHETIC_ORACLE` is architecture-only evidence. It is not transcription-model accuracy evidence.

## Timing eligibility

`PerformanceEventV1.observed_at_s` is not redefined by SF-11. In particular, model inference latency is not silently inserted into or subtracted from event onset time.

A path with `timing_basis = performance_onset` can participate in shared stale/quorum timing and pairwise onset-asynchrony evidence. A path with `timing_basis = unverified`:

- keeps its own independent recovery/score-following result;
- remains visible with full path provenance;
- is excluded from timing-based shared-position aggregation;
- causes pairwise timing comparisons involving that part to become explicit abstentions rather than zero-latency assumptions.

## Quorum

The default mixed-ensemble shared-position quorum remains 3 of 4 timing-comparable recent parts. Below quorum, shared score beat and spread stay unavailable.

## Authority boundary

`mixed_ensemble_channel_separated_research_not_acoustic_mixture_authority`

SF-11 does not establish real-room mixed-ensemble tracking, mono microphone source separation, calibrated cross-path timing correction, conductor intent, orchestra behavior, or pedagogy.
