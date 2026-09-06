# Dependencies

## Core runtime

The ST-owned core package intentionally uses only the Python standard library.

## Development

- `pytest>=8.3,<9`: deterministic tests.
- `ruff>=0.8,<1`: lint/static hygiene.

## SF-01 optional research backend

- `pymatchmaker==0.3.0`: Apache-2.0 score-following research backend, loaded only through
  `MatchmakerAdapter`.
- Matchmaker 0.3.0 declares Python `>=3.10,<3.13`; the integration CI therefore runs on Python 3.12.
- Ubuntu CI installs `libfluidsynth3` because Matchmaker includes FluidSynth-backed audio utilities.
- Device extras are not installed for the offline synthetic MIDI baseline.

The optional dependency is version-pinned because Matchmaker 0.3 introduced API changes and ST
normalizes its high-level generator/final alignment path behind an adapter.

## Future research dependencies

Audio device support, causal transcription models and additional followers remain optional and are
introduced only behind ST-owned contracts after license/API/benchmark verification.
