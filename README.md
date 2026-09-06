# ST Real-Time Score Following Lab

Research infrastructure for low-latency alignment of live audio/MIDI performances to a validated symbolic score.

## Near-term target

Produce benchmarkable `score position + tempo + confidence` from simulated or live streams while keeping follower algorithms replaceable.

## Design rules

- Canonical score truth and live observations are separate.
- Every position estimate is uncertain and must carry confidence.
- Audio-only and transcription→symbolic following are parallel research paths.
- Latency, recovery and robustness are first-class metrics alongside alignment accuracy.
- Python is the research language; C++ extraction starts only after reproducible benchmark evidence.
- Experimental evidence is not production or pedagogical authority.

## Current stage

**SF-00 — Foundation, Architecture and Contracts.**

Implemented on the foundation branch: typed v1 contracts, stream-relative clock/latency primitives, tests, CI, benchmark/data governance docs, and repository boundaries.

## Roadmap

SF-00 foundation → SF-01 Matchmaker baseline → SF-02 realtime streaming → symbolic following → instrument research → robustness/recovery → performance alignment → ensemble/orchestra research → production candidate extraction.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

## Data policy

Do not commit private/student audio, secrets, downloaded third-party corpora, large raw datasets or model checkpoints by default. Dataset use must record source, version, license and integrity metadata.
