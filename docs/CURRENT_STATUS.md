# Current Status

Date: 2026-09-06

## Stage state

- SF-00 Foundation, Architecture and Contracts: **complete; CI green on Python 3.11/3.12**.
- SF-01 Matchmaker Baseline Reproduction: **active; adapter + synthetic baseline implemented, CI evidence pending**.
- SF-02 Realtime Microphone and Streaming Pipeline: **not started**.

## Implemented

- Python package bootstrap and canonical v1 score/observation/tempo/confidence/alignment contracts.
- Stream-relative monotonic clock and latency primitive.
- Ruff + pytest CI on Python 3.11 and 3.12.
- ST-owned follower adapter boundary.
- Version-pinned `pymatchmaker==0.3.0` adapter with lazy optional dependency loading.
- Matchmaker generator-return normalization: online score-beat updates plus final `(score beat, performance time)` path.
- Synthetic 16-quarter-note MusicXML/MIDI baseline fixture generated without private or third-party data.
- Baseline alignment metrics and dedicated Matchmaker CI job.

## Evidence level

SF-00 is validated infrastructure. SF-01 code exists but is not declared complete until the
real `pymatchmaker==0.3.0` CI job runs the synthetic baseline and records reproducible evidence.

Matchmaker's high-level API does not expose calibrated confidence with each yielded score-beat
update. The adapter therefore reports confidence as unavailable rather than inventing a value.

## Next safe action

Run the SF-01 Matchmaker integration job. If successful, record its benchmark output, close SF-01,
and proceed to SF-02 bounded streaming/queue foundations using synthetic byte/MIDI streams before
requiring local microphone hardware.
