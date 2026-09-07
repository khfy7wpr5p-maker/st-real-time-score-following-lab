# SF-05 Classical Guitar Score Following

## Goal

Establish a reproducible polyphonic classical-guitar score-following baseline without making a third-party dataset or transcription model project authority.

## Repository-owned benchmark

`tests/fixtures/synthetic_classical_guitar.musicxml` contains four 4/4 measures at 120 BPM. Each measure begins with a multi-pitch guitar-range harmony and a whole-measure bass voice. Upper-voice quarter-note arpeggios continue while the bass sustains, creating explicit chord onset, sustain and voice-overlap conditions.

The benchmark compares:

1. Matchmaker Arzt with chroma audio features.
2. Matchmaker Arzt with CQT audio features.
3. ST causal symbolic following fed by note-level synthetic oracle events grouped with `cluster_simultaneous_note_events`.

All paths share the same score structure and expected onset positions.

## Data boundary

No GuitarSet or GAPS media are required for the repository-owned baseline. GuitarSet remains a candidate for external validation. Its current official Zenodo record and repository are recorded in `datasets/manifests/guitarset_research_candidate.json`; data are not materialized while primary-source dataset rights are not independently captured in the ST evidence trail.

## Interpretation boundary

The synthetic score represents guitar range, polyphonic chord onsets, arpeggiation and sustained-bass overlap, but the rendered audio is deterministic score synthesis rather than a real nylon-string performance. The symbolic observations are oracle events. Therefore this benchmark can establish architecture and structural robustness, but it cannot establish real-world guitar transcription accuracy or acoustic-timbre generalization.
