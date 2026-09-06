# ST Real-Time Score Following Lab

Research infrastructure for low-latency alignment of live audio/MIDI performances to a validated symbolic score.

## Near-term target

Produce benchmarkable `score position + tempo + confidence` from simulated or live streams while keeping follower algorithms replaceable.

## Design rules

- Canonical score truth and live observations are separate.
- Every position estimate is uncertain; unavailable backend confidence is reported as unavailable, never fabricated.
- Audio-only and transcription→symbolic following are parallel research paths.
- Latency, recovery and robustness are first-class metrics alongside alignment accuracy.
- Python is the research language; C++ extraction starts only after reproducible benchmark evidence.
- Experimental evidence is not production or pedagogical authority.

## Current stage

**SF-02 — Realtime Streaming Foundation is next.**

SF-00 is complete and CI-validated. SF-01 is also complete: the ST-owned adapter runs a pinned
`pymatchmaker==0.3.0` synthetic MusicXML/MIDI baseline in CI and records reproducible evidence.
The clean 16-event fixture aligned 16/16 events with zero failures; this is deliberately only a
smoke/reproducibility result, not a real-performance accuracy claim.

See `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md` for the exact evidence and limitations.

## Roadmap

SF-00 foundation → SF-01 Matchmaker baseline → SF-02 realtime streaming → symbolic following → instrument research → robustness/recovery → performance alignment → ensemble/orchestra research → production candidate extraction.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

To reproduce the optional SF-01 Matchmaker baseline on a compatible environment:

```bash
python -m pip install -e ".[dev,matchmaker]"
python benchmarks/run_matchmaker_baseline.py
```

Matchmaker 0.3.0 is evaluated only through an adapter and is not the ST runtime authority.

## Data policy

Do not commit private/student audio, secrets, downloaded third-party corpora, large raw datasets or model checkpoints by default. Dataset use must record source, version, license and integrity metadata.
