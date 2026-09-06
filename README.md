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

**SF-03 — Symbolic Following Path is active.**

SF-00, SF-01 and SF-02 are complete and CI-validated. SF-02 established bounded realtime MIDI and PCM streaming with explicit queue-pressure, lifecycle and ST-ingress-to-follower latency evidence. SF-03 now adds a backend-neutral transcription boundary and a causal symbolic follower, then compares direct audio-only alignment against a benchmark-only oracle transcription path on the same repository-owned score material.

Oracle transcription is an architecture upper bound only; it is not AMT model evidence.

See `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md` and `benchmarks/reports/SF02_REALTIME_STREAMING.md` for completed evidence. SF-03 evidence will be added only after its comparison benchmark passes CI.

## Roadmap

SF-00 foundation -> SF-01 Matchmaker baseline -> SF-02 realtime streaming -> SF-03 symbolic following -> instrument research -> robustness/recovery -> performance alignment -> ensemble/orchestra research -> production candidate extraction.

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
