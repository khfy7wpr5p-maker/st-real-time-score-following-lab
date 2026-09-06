# SF-04 Solo Violin — STRAdi Preflight

Date: 2026-09-06

## External candidate

STRAdi is the official code/model release for the 2026 work "Real-time Violin Transcription for Score Following". Its online model is described as fully causal. The repository documents CSV note output with `onset`, `offset`, and `midi_number`, mono/16 kHz preprocessing, and paper experiments using Python 3.7.12 with PyTorch 1.13.1.

The source repository license is Apache-2.0. Its README separately states that the included example audio/annotations are subject to KRAISLER dataset terms. The README does not separately state license terms for the downloadable checkpoint assets, so ST does not materialize those assets without explicit confirmation.

## Integration decision

Do not install STRAdi directly into the ST core environment. Its historical Python/PyTorch dependency stack is isolated from the main Python 3.11/3.12 package.

Instead, the first adapter boundary consumes STRAdi-style CSV output and maps it to `PerformanceEventV1`. This keeps model execution replaceable and avoids importing a legacy deep-learning stack into core score-following code.

STRAdi CSV output does not expose a confidence column. ST therefore records `confidence=None`; it does not invent 0.0 or 1.0. The symbolic follower accepts unavailable confidence only when no positive confidence threshold is requested. With a positive threshold, unavailable-confidence events abstain/reject explicitly.

## Repository-owned synthetic evidence

`tests/fixtures/stradi_synthetic_violin_output.csv` is authored by ST and contains no third-party audio/data. Tests prove:

- onset/offset/MIDI mapping;
- unavailable confidence preservation;
- causal symbolic following from STRAdi-style note events;
- explicit abstention under a positive confidence gate;
- preservation of irregular/tempo-varying onset timestamps.

This is adapter-contract evidence only. It is not violin transcription accuracy evidence.

## Narrow human/data gate

Actual STRAdi checkpoint inference and KRAISLER/example-audio evaluation remain gated until asset/audio terms are confirmed. The rest of the repository is not blocked.

SF-04 cannot satisfy its final exit criterion — a violin research report with reproducible instrument evidence — from the synthetic CSV adapter alone.
