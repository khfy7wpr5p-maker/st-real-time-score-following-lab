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
    SYNTHETIC_NOTES,
    evaluate_expected_onsets,
    oracle_performance_events,
    synthetic_score_events,
)
from st_score_following.followers import MatchmakerAdapter
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


def run() -> dict[str, object]:
    score_path = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic_piano.musicxml"
    expected = tuple((float(index), index * 0.5) for index in range(len(SYNTHETIC_NOTES)))
    audio = _render_fixture_audio(score_path)

    with TemporaryDirectory() as tmp_dir:
        audio_path = Path(tmp_dir) / "synthetic.wav"
        _write_pcm16_wav(audio_path, audio)
        audio_result = MatchmakerAdapter().run_files(
            score_file=str(score_path),
            performance_file=str(audio_path),
            input_type="audio",
            method="arzt",
        )

    symbolic_result = CausalSymbolicFollower(synthetic_score_events()).run_events(
        oracle_performance_events()
    )
    audio_metrics = evaluate_expected_onsets(audio_result.alignment_path, expected)
    symbolic_metrics = evaluate_expected_onsets(symbolic_result.alignment_path, expected)

    return {
        "schema": "st.score_following.symbolic_comparison.v1",
        "fixture": "synthetic_piano_same_material_v1",
        "expected_events": len(expected),
        "audio_only": {
            "backend": audio_result.backend,
            "backend_version": audio_result.backend_version,
            "method": audio_result.method,
            "updates": len(audio_result.updates),
            "alignment_points": len(audio_result.alignment_path),
            "wall_duration_s": audio_result.wall_duration_s,
            "confidence_available": audio_result.confidence_available,
            "metrics": audio_metrics.to_dict(),
        },
        "transcription_to_symbolic": {
            "transcription_source": "synthetic_oracle_ground_truth",
            "backend": symbolic_result.backend,
            "backend_version": symbolic_result.backend_version,
            "method": symbolic_result.method,
            "updates": len(symbolic_result.updates),
            "alignment_points": len(symbolic_result.alignment_path),
            "wall_duration_s": symbolic_result.wall_duration_s,
            "confidence_available": symbolic_result.confidence_available,
            "backend_metrics": symbolic_result.backend_metrics,
            "metrics": symbolic_metrics.to_dict(),
        },
        "limitations": [
            "Both paths use the same repository-owned 16-note score material.",
            (
                "The symbolic path receives perfect oracle note events; "
                "it is an architecture upper bound."
            ),
            "No AMT/transcription model accuracy or latency is measured by the oracle path.",
            "Audio is deterministically synthesized from the score and is not a live performance.",
            (
                "Wall durations are implementation timings and are not comparable "
                "end-to-end latency claims."
            ),
            "A lower oracle symbolic error does not establish superiority on real instruments.",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
