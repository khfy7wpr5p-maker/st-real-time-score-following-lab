# SF-12 Orchestra Global Score Following

SF-12 introduces a deliberately narrow orchestra-level research path. Its output authority is global score location: measure and beat. It is not a per-instrument transcription system.

## Architecture

```text
aggregate orchestral observation
        |
        v
OrchestraGlobalObservationV1
        |
        v
aggregate pitch-class texture similarity
        |
        +--> bounded local forward/backward search
        |
        +--> global initial / long-gap re-lock
        |
        v
OrchestraGlobalMatchV1
        |
        +--> measure_index
        +--> beat_in_measure
        +--> score_beat
        +--> transition / search scope
        +--> optional propagated source confidence
        +--> local CPU processing latency
```

`OrchestraGlobalScorePointV1` contains only score-global identity plus an aggregate texture fingerprint. It deliberately has no instrument or section field.

## Recovery policy

Normal observations are matched in a bounded local window. A forward skip records how many score points were skipped; a bounded backward match records a backward jump. Initial acquisition and a long performance gap use global search before the local window. This ordering matters for restart behavior: a nearby similar texture must not silently override an explicit post-pause restart candidate.

After a configured mismatch streak the follower may also use global search. Every accepted match records its transition and search scope so the recovery path is auditable.

## Confidence semantics

Texture Jaccard similarity is a matching score, not calibrated probability and not `ConfidenceV1`. If the observation source provides no confidence, the result remains unavailable. If the caller requests a positive minimum observation confidence, unavailable-confidence observations are rejected rather than guessed.

## Latency semantics

`processing_latency_ms` measures the Python matching work from one already-materialized aggregate observation to its score-point decision. It excludes capture, microphone/ADC, feature extraction, transcription/model inference, buffering, transport, browser/network, and presentation latency. It must not be presented as end-to-end realtime latency.

## Repository-owned evidence

Run:

```bash
python benchmarks/run_orchestra_global.py
```

CI `34678255101` passed the orchestra-global benchmark and the full existing regression suite on implementation head `7f023613697a3ae999bb0f2ebc6fd86d5adbde72`.

The benchmark covers clean tracking, a controlled dense-texture proxy, tempo/rubato timestamp variation, missing observations, forward skip, backward jump, and pause/restart. Every received observation in these deterministic fixtures mapped to the declared global score point; discontinuity scenarios re-acquired the target on the first post-boundary observation.

See `benchmarks/reports/SF12_ORCHESTRA_GLOBAL.md` for exact CI numbers and limitations.

## Research boundary

Authority remains:

`global_measure_beat_research_not_per_instrument_transcription_authority`

Real dense-orchestra audio, large repeated score structures, calibrated global confidence, acoustic source separation, and section-level intelligence are not established here. SF-13 may research section grouping separately without retroactively widening SF-12 authority.
