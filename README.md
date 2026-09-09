# ST Real-Time Score Following Lab

Research infrastructure for low-latency alignment of live audio/MIDI performances to a validated symbolic score.

## Near-term target

Produce benchmarkable `score position + tempo + confidence` from simulated or live streams while keeping follower algorithms replaceable, then turn validated alignment evidence into auditable post-performance analysis, evidence-first performance intelligence, and explicitly bounded multi-performer research.

## Design rules

- Canonical score truth and live observations are separate.
- Every position estimate is uncertain; unavailable backend confidence is reported as unavailable, never fabricated.
- Audio-only and transcription->symbolic following are parallel research paths.
- Latency, recovery and robustness are first-class metrics alongside alignment accuracy.
- Multi-performer streams retain independent part/performer identity; shared position is derived evidence rather than new score authority.
- Multi-channel shared positions require explicit quorum; insufficient evidence stays unavailable.
- Python is the research language; C++ extraction starts only after reproducible benchmark evidence.
- Experimental evidence is not production or pedagogical authority.

## Current stage

**SF-10 Quartet / Multi-Channel Ensemble is complete for repository-owned deterministic four-channel evidence. SF-11 Mixed Ensemble is the next autonomous stage.**

Completed permanent evidence currently covers:
- SF-01 Matchmaker synthetic MIDI baseline;
- SF-02 bounded realtime MIDI/PCM streaming;
- SF-03 direct-audio vs synthetic-oracle symbolic following;
- SF-05 classical-guitar structural synthetic comparison;
- SF-06 robustness/recovery perturbation suite;
- SF-07 post-performance alignment, segmentation, timing/tempo summaries and JSON/CSV export;
- SF-08 evidence-first performance deviation events, abstention contracts and JSON/CSV export;
- SF-09 independent duet part-following, derived shared-position states, inter-part asynchrony and fail-soft divergence evidence;
- SF-10 independent quartet channels, 3-of-4 quorum semantics, six-pair timing evidence and partial-channel fail-soft behavior.

SF-04 Solo Violin remains a narrow real-evidence rights gate and does not block independent stages.

Evidence reports:

- `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md`
- `benchmarks/reports/SF02_REALTIME_STREAMING.md`
- `benchmarks/reports/SF03_SYMBOLIC_COMPARISON.md`
- `benchmarks/reports/SF05_CLASSICAL_GUITAR.md`
- `benchmarks/reports/SF06_ROBUSTNESS_RECOVERY.md`
- `benchmarks/reports/SF07_PERFORMANCE_ALIGNMENT.md`
- `benchmarks/reports/SF08_ERROR_INTELLIGENCE.md`
- `benchmarks/reports/SF09_DUET_RESEARCH.md`
- `benchmarks/reports/SF10_QUARTET_MULTICHANNEL.md`

## Roadmap

SF-00 foundation -> SF-01 Matchmaker baseline -> SF-02 realtime streaming -> SF-03 symbolic following -> SF-04 solo violin -> SF-05 classical guitar -> SF-06 robustness/recovery -> SF-07 performance alignment -> SF-08 performance error intelligence -> SF-09 duet -> SF-10 quartet/multi-channel ensemble -> SF-11 mixed ensemble -> SF-12 orchestra global following -> production candidate extraction.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

To reproduce optional Matchmaker research on a compatible environment:

```bash
python -m pip install -e ".[dev,matchmaker]"
python benchmarks/run_matchmaker_baseline.py
python benchmarks/run_matchmaker_streaming_smoke.py
python benchmarks/run_matchmaker_audio_streaming_smoke.py
python benchmarks/run_symbolic_comparison.py
python benchmarks/run_guitar_baseline.py
```

To reproduce repository-owned autonomous research benchmarks without Matchmaker:

```bash
python benchmarks/run_recovery_suite.py
python benchmarks/run_performance_alignment.py
python benchmarks/run_error_intelligence.py
python benchmarks/run_duet_research.py
python benchmarks/run_quartet_research.py
```

Matchmaker 0.3.0 is evaluated only through an adapter and is not the ST runtime authority.

## Data policy

Do not commit private/student audio, secrets, downloaded third-party corpora, large raw datasets or model checkpoints by default. Dataset use must record source, version, license and integrity metadata.
