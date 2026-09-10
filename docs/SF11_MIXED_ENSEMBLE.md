# SF-11 Mixed Ensemble

SF-11 extends the SF-10 four-channel research boundary to heterogeneous instrument and observation paths while preserving independent per-part authority.

## Contracts

Each `MixedEnsemblePartInputV1` retains:
- stable `part_id`, `performer_id`, and `channel_id`;
- `InstrumentFamily`;
- `ObservationPathKind`;
- `ObservationTimingBasis`;
- explicit `path_source` provenance;
- independent score and observation streams.

The current research boundary requires exactly four parts and at least two instrument families and two observation paths. It is intentionally not an arbitrary-N or orchestra contract.

## Timing eligibility

`PerformanceEventV1.observed_at_s` remains the event timestamp supplied by its source. SF-11 does not repurpose this field as model inference latency and does not silently compensate heterogeneous paths.

Only `ObservationTimingBasis.PERFORMANCE_ONSET` paths participate in shared timing/quorum and pairwise asynchrony evidence. `UNVERIFIED` paths still run their independent score follower but are excluded from comparisons whose timing basis cannot be justified.

Pairs involving an ineligible path create `MixedTimingAbstentionV1`. This makes missing comparability explicit rather than fabricating timing evidence.

## Shared position

The default shared-position quorum remains 3 of 4 timing-eligible, recent parts. Below quorum, `shared_score_beat` and spread remain unavailable. At or above quorum the layer reports full consensus, quorum consensus, or divergence while retaining contributing, stale, unavailable, and timing-ineligible part IDs.

Shared confidence remains unavailable because no calibrated heterogeneous confidence-combination method has been validated.

## Evidence boundary

The SF-11 benchmark is deterministic and channel-separated. It covers piano/direct MIDI, guitar/transcription-symbolic, violin/external-event-adapter, and voice/synthetic-oracle paths plus timing-ineligible, pause, dropped-event, and advance cases.

This does not prove acoustic mixture source separation, physical microphone behavior, real musician/room generalization, AMT model quality, cross-model latency correction, orchestra behavior, conductor intent, or pedagogy.

Permanent numeric evidence is in `benchmarks/reports/SF11_MIXED_ENSEMBLE.md`.
