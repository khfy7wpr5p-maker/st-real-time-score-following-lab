# ST Real-Time Score Following Lab

Research infrastructure for low-latency alignment of live audio/MIDI performances to a validated symbolic score.

## Near-term target

Produce benchmarkable `score position + tempo + confidence` from simulated or live streams while keeping follower algorithms replaceable.

## Design rules

- Canonical score truth and live observations are separate.
- Every position estimate is uncertain; unavailable backend confidence is reported as unavailable, never fabricated.
- Audio-only and transcription->symbolic following are parallel research paths.
- Latency, recovery and robustness are first-class metrics alongside alignment accuracy.
- Python is the research language; C++ extraction starts only after reproducible benchmark evidence.
- Experimental evidence is not production or pedagogical authority.

## Current stage

**SF-03 — Symbolic Following Path is complete for the repository-owned synthetic comparison scope. SF-04 Solo Violin is next.**

SF-00 through SF-03 are CI-validated. SF-03 adds a backend-neutral transcription boundary and ST-owned causal symbolic follower, then compares direct audio-only alignment against a benchmark-only oracle transcription path on the same 16-note score material.

Final SF-03 run `34058190673` passed Python 3.11/3.12 plus all Matchmaker integration and benchmark steps. Audio-only mean absolute onset error was 20.833 ms with P95 333.333 ms; the perfect oracle symbolic path was 0 ms across all 16 expected events. The oracle result is an architecture upper bound only and is not AMT-model evidence.

Evidence reports:

- `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md`
- `benchmarks/reports/SF02_REALTIME_STREAMING.md`
- `benchmarks/reports/SF03_SYMBOLIC_COMPARISON.md`

## Roadmap

SF-00 foundation -> SF-01 Matchmaker baseline -> SF-02 realtime streaming -> SF-03 symbolic following -> SF-04 solo violin -> SF-05 classical guitar -> robustness/recovery -> performance alignment -> ensemble/orchestra research -> production candidate extraction.

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
```

Matchmaker 0.3.0 is evaluated only through an adapter and is not the ST runtime authority.

## Data policy

Do not commit private/student audio, secrets, downloaded third-party corpora, large raw datasets or model checkpoints by default. Dataset use must record source, version, license and integrity metadata.
