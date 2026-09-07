# SF-05 Classical Guitar Synthetic Baseline

Date: 2026-09-07

## Scope

This report records the repository-owned SF-05 structural baseline. It does not claim real classical-guitar transcription or acoustic generalization.

Fixture: `synthetic_classical_guitar_polyphonic_v1`

Coverage:
- 16 expected onset positions.
- 4 multi-pitch chord onsets.
- 12 upper-voice arpeggio onsets while a whole-measure bass voice remains sustained.
- explicit voice overlap across all four measures.

Compared paths:
1. Matchmaker 0.3.0 / Arzt / chroma.
2. Matchmaker 0.3.0 / Arzt / CQT.
3. ST causal symbolic follower fed by repository-owned synthetic note-level oracle events grouped into polyphonic onset observations.

## Evidence

Clean CI run: `34087889237`.

Python 3.11 and 3.12 both passed Ruff and the full pytest suite. The Matchmaker job passed the existing integration suite and every SF-01 through SF-05 benchmark step.

### Audio / chroma

- updates: 226
- alignment points: 226
- evaluated onset events: 16
- failed events: 0
- mean absolute onset error: 0 ms
- median absolute onset error: 0 ms
- P95 absolute onset error: 0 ms
- within 50/100/250/500 ms: 100%
- chord-onset subset: 4/4, 0 ms error
- arpeggio-under-sustain subset: 12/12, 0 ms error
- wall duration in this CI sample: 0.647763 s
- calibrated confidence: unavailable

### Audio / CQT

- updates: 226
- alignment points: 226
- evaluated onset events: 16
- failed events: 0
- mean absolute onset error: 0 ms
- median absolute onset error: 0 ms
- P95 absolute onset error: 0 ms
- within 50/100/250/500 ms: 100%
- chord-onset subset: 4/4, 0 ms error
- arpeggio-under-sustain subset: 12/12, 0 ms error
- wall duration in this CI sample: 14.144695 s
- calibrated confidence: unavailable

### Synthetic oracle -> symbolic

- clustered observations: 16
- updates: 16
- alignment points: 16
- failed events: 0
- mean/median/P95 onset error: 0 ms
- chord-onset subset: 4/4, 0 ms error
- arpeggio-under-sustain subset: 12/12, 0 ms error
- wall duration in this CI sample: 0.000082184 s
- event confidence is synthetic-oracle provenance and explicitly uncalibrated

## Interpretation

All three paths align perfectly on this deterministic score-synthesized fixture. That establishes structural compatibility with chord onsets, arpeggiation, sustained bass and voice overlap under controlled conditions. It does not establish one feature path as more accurate on real guitar.

The CQT path took substantially longer than chroma in this particular offline CI execution. That is implementation timing evidence only; it is not a complete real-time acoustic latency measurement and is not sufficient by itself to reject CQT for later research.

## Visible warnings

The benchmark intentionally retains third-party warnings instead of hiding them:
- Partitura `ignore_invisible_objects` caution.
- Partitura metronome-direction parsing warning.
- Scipy/Librosa complex-to-real warnings on the CQT path.
- Librosa warnings where `n_fft` exceeds the local 1470-sample frame length.

These warnings are not currently benchmark failures, but the CQT frame-size behavior should be revisited before production extraction.

## Data boundary

No GuitarSet or GAPS media were downloaded, committed or redistributed. GuitarSet remains a candidate for real-corpus external validation. The repository records that candidate separately and does not infer primary dataset rights from an unverified secondary mirror.

## Exit statement

SF-05 is complete for the repository-owned structural synthetic baseline. Real nylon-string timbre, performer variability and real-corpus generalization remain external-validation work and must not be inferred from this report.
