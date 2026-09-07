from __future__ import annotations

import json
import wave
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import partitura
from matchmaker.features.audio import SAMPLE_RATE
from matchmaker.utils.misc import generate_score_audio
from partitura.score import merge_parts

from st_score_following.evaluation import (
    evaluate_expected_onsets,
    guitar_category_indices,
    guitar_expected_onsets,
    guitar_note_level_events,
    guitar_score_events,
)
from st_score_following.followers import MatchmakerAdapter
from st_score_following.polyphony import cluster_simultaneous_note_events
from st_score_following.symbolic import CausalSymbolicFollower


def _render_fixture_audio(score_path: Path) -> np.ndarray:
    score = partitura.load_musicxml(str(score_path), ignore_invisible_objects=True)
    score_part = merge_parts(score.parts)
    return np.asarray(
        generate_score_audio(score_part, bpm=120.0, samplerate=SAMPLE_RATE),
        dtype=np.float32,
    )


def _write_pcm16_wav(path: Path, samples: np.ndarray) -> None:
    pcm = np.asarray(np.clip(samples, -1.0, 1.0) * 32767.0, dtype=np.int16)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm.tobytes())


def _category_metrics(path: object) -> dict[str, object]:
    expected = guitar_expected_onsets()
    return {
        name: evaluate_expected_onsets(
            path,
            tuple(expected[index] for index in indices),
        ).to_dict()
        for name, indices in guitar_category_indices().items()
    }


def _audio_result(score_path: Path, audio_path: Path, processor: str) -> dict[str, object]:
    result = MatchmakerAdapter().run_files(
        score_file=str(score_path),
        performance_file=str(audio_path),
        input_type="audio",
        method="arzt",
        kwargs={"processor": processor},
    )
    return {
        "backend": result.backend,
        "backend_version": result.backend_version,
        "method": result.method,
        "processor": processor,
        "updates": len(result.updates),
        "alignment_points": len(result.alignment_path),
        "wall_duration_s": result.wall_duration_s,
        "confidence_available": result.confidence_available,
        "metrics": evaluate_expected_onsets(
            result.alignment_path,
            guitar_expected_onsets(),
        ).to_dict(),
        "category_metrics": _category_metrics(result.alignment_path),
    }


def run() -> dict[str, object]:
    score_path = (
        Path(__file__).parents[1]
        / "tests"
        / "fixtures"
        / "synthetic_classical_guitar.musicxml"
    )
    audio = _render_fixture_audio(score_path)

    with TemporaryDirectory() as tmp_dir:
        audio_path = Path(tmp_dir) / "synthetic_classical_guitar.wav"
        _write_pcm16_wav(audio_path, audio)
        chroma = _audio_result(score_path, audio_path, "chroma")
        cqt = _audio_result(score_path, audio_path, "cqt")

    clustered = cluster_simultaneous_note_events(guitar_note_level_events())
    symbolic_result = CausalSymbolicFollower(guitar_score_events()).run_events(clustered)
    symbolic = {
        "transcription_source": "synthetic_polyphonic_oracle_ground_truth",
        "clustered_observations": len(clustered),
        "backend": symbolic_result.backend,
        "backend_version": symbolic_result.backend_version,
        "method": symbolic_result.method,
        "updates": len(symbolic_result.updates),
        "alignment_points": len(symbolic_result.alignment_path),
        "wall_duration_s": symbolic_result.wall_duration_s,
        "confidence_available": symbolic_result.confidence_available,
        "metrics": evaluate_expected_onsets(
            symbolic_result.alignment_path,
            guitar_expected_onsets(),
        ).to_dict(),
        "category_metrics": _category_metrics(symbolic_result.alignment_path),
    }

    return {
        "schema": "st.score_following.classical_guitar_baseline.v1",
        "fixture": "synthetic_classical_guitar_polyphonic_v1",
        "expected_onsets": len(guitar_expected_onsets()),
        "audio_chroma": chroma,
        "audio_cqt": cqt,
        "transcription_to_symbolic": symbolic,
        "coverage": {
            "chord_onsets": len(guitar_category_indices()["chord_onsets"]),
            "arpeggio_onsets_under_sustained_bass": len(
                guitar_category_indices()["arpeggio_under_sustain"]
            ),
            "voice_overlap": "whole-measure bass overlaps upper-voice onsets",
        },
        "limitations": [
            (
                "The MusicXML encodes classical-guitar-range voicings and "
                "sustained bass overlap."
            ),
            (
                "Audio is deterministic score synthesis, not a recorded "
                "nylon-string guitar performance."
            ),
            "The symbolic path receives perfect note-level oracle events before onset clustering.",
            "Oracle symbolic results are an architecture upper bound, not AMT accuracy evidence.",
            "No GuitarSet/GAPS media were downloaded or redistributed for this benchmark.",
            (
                "Real classical-guitar timbre and performer variability remain "
                "external-validation work."
            ),
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
