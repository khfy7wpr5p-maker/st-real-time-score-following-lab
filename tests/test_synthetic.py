from st_score_following.evaluation.synthetic import SYNTHETIC_NOTES, write_quarter_note_midi


def test_synthetic_midi_has_valid_smf_header(tmp_path) -> None:
    target = tmp_path / "fixture.mid"
    write_quarter_note_midi(target)
    data = target.read_bytes()

    assert data.startswith(b"MThd")
    assert b"MTrk" in data
    assert len(SYNTHETIC_NOTES) == 16
