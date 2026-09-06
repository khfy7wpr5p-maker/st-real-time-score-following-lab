# SF-03 Symbolic Following Comparison Evidence

Date: 2026-09-06

## Validation source

- GitHub Actions run: `34058190673`
- Python core matrix: 3.11 and 3.12 — green
- Matchmaker integration job: green
- Matchmaker version: `0.3.0`
- Comparison schema: `st.score_following.symbolic_comparison.v1`
- Fixture: `synthetic_piano_same_material_v1`
- Expected events: 16

The comparison uses the same repository-owned 16-note score material for both paths.

## Path A — direct audio-only following

Backend: Matchmaker 0.3.0, `arzt`.

- online/alignment updates: 226
- evaluated expected events: 16
- failed events: 0
- failure rate: 0.0
- mean absolute onset error: 20.833333333333343 ms
- median absolute onset error: 0.0 ms
- P95 absolute onset error: 333.3333333333335 ms
- within 50 ms: 0.9375
- within 100 ms: 0.9375
- within 250 ms: 0.9375
- within 500 ms: 1.0
- calibrated confidence exposed by backend: no

The audio is deterministically synthesized from the score. It is not a microphone or musician recording.

## Path B — transcription to symbolic following

Transcription source: `synthetic_oracle_ground_truth`.

Follower: `st-symbolic-causal` 0.1.0, method `forward_pitch_lookahead`.

- alignment updates: 16
- matched events: 16
- unmatched observations: 0
- skipped score events: 0
- low-confidence rejections: 0
- lookahead events: 2
- evaluated expected events: 16
- failed events: 0
- failure rate: 0.0
- mean absolute onset error: 0.0 ms
- median absolute onset error: 0.0 ms
- P95 absolute onset error: 0.0 ms
- within 50/100/250/500 ms: 1.0
- confidence semantics: propagated from transcription event

The oracle confidence value describes benchmark construction certainty only. It is explicitly uncalibrated and is not an AMT probability.

## Interpretation

This result validates the architecture and the shared evaluation boundary: a transcription backend can emit `PerformanceEventV1` events into an ST-owned causal symbolic follower and be evaluated against the direct audio path with the same onset metrics.

The 0 ms oracle symbolic result is an upper bound created from perfect note events. It does **not** show that a real transcription model is more accurate or lower-latency than direct audio following. No AMT model accuracy or AMT inference latency is measured in SF-03.

Wall-clock implementation timings are intentionally not used as a path-to-path latency comparison because the oracle path performs no audio transcription work.

## Known warnings

CI continued to surface known Partitura MusicXML warnings and the HiddenMarkov transition-log warning. They were not hidden or converted into false success signals.

## Exit decision

SF-03 exit criteria are satisfied for the repository-owned synthetic comparison scope:

1. backend-neutral transcription contract exists;
2. causal symbolic follower exists with explicit failure counters;
3. both paths run on the same material;
4. both paths use common expected-onset metrics;
5. core and Matchmaker CI are green;
6. exact evidence and limitations are preserved here.

Real violin/guitar/polyphonic transcription quality remains outside SF-03 and requires instrument-specific evidence in later stages.
