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

**SF-03 — Symbolic Following Path is next.**

SF-00, SF-01 and SF-02 have reproducible CI evidence. SF-02 adds bounded realtime ingestion, explicit overflow/cancellation behavior, monotonic ST timing, raw MIDI streaming and realtime-paced float32 PCM streaming through `pymatchmaker==0.3.0`.

The SF-02 synthetic PCM evidence reached score beat 15.0 at nominal 30 frames/s while ingress remained bounded at depth <= 1/4 with no rejected or dropped PCM chunks. The measured ST-ingress-to-follower-update latency on that runner was mean 2.852 ms, P95 2.969 ms and max 7.038 ms. These values exclude physical microphone/ADC/driver/network latency.

See `benchmarks/reports/SF02_REALTIME_STREAMING.md` for exact evidence and limitations, and `benchmarks/reports/SF01_MATCHMAKER_SYNTHETIC_MIDI.md` for the baseline report.

## Roadmap

SF-00 foundation -> SF-01 Matchmaker baseline -> SF-02 realtime streaming -> SF-03 symbolic following -> instrument research -> robustness/recovery -> performance alignment -> ensemble/orchestra research -> production candidate extraction.

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
pytest
```

To reproduce Matchmaker research paths on a compatible environment:

```bash
python -m pip install -e ".[dev,matchmaker]"
python benchmarks/run_matchmaker_baseline.py
python benchmarks/run_matchmaker_streaming_smoke.py
python benchmarks/run_matchmaker_audio_streaming_smoke.py
```

Matchmaker 0.3.0 is evaluated only through an adapter and is not the ST runtime authority. Live producers must start through the adapter's ready lifecycle after backend score preprocessing.

## Data policy

Do not commit private/student audio, secrets, downloaded third-party corpora, large raw datasets or model checkpoints by default. Dataset use must record source, version, license and integrity metadata.
