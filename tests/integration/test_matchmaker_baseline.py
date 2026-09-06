from pathlib import Path

import pytest

pytest.importorskip("matchmaker")

from st_score_following.evaluation import (  # noqa: E402
    SYNTHETIC_NOTES,
    evaluate_expected_onsets,
    write_quarter_note_midi,
)
from st_score_following.followers import MatchmakerAdapter  # noqa: E402


def test_matchmaker_midi_baseline_runs(tmp_path) -> None:
    score = Path(__file__).parents[1] / "fixtures" / "synthetic_piano.musicxml"
    midi = tmp_path / "performance.mid"
    write_quarter_note_midi(midi)

    result = MatchmakerAdapter().run_files(
        score_file=str(score),
        performance_file=str(midi),
        input_type="midi",
        method="pthmm",
    )

    expected = tuple((float(i), i * 0.5) for i in range(len(SYNTHETIC_NOTES)))
    metrics = evaluate_expected_onsets(result.alignment_path, expected)

    assert len(result.updates) > 0
    assert len(result.alignment_path) > 0
    assert metrics.evaluated_events > 0
    assert metrics.failure_rate < 1.0
