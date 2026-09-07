from st_score_following.evaluation import (
    GUITAR_EVENT_CLASSES,
    guitar_category_indices,
    guitar_expected_onsets,
    guitar_note_level_events,
    guitar_score_events,
)
from st_score_following.polyphony import cluster_simultaneous_note_events
from st_score_following.symbolic import CausalSymbolicFollower


def test_guitar_fixture_has_chords_arpeggios_and_sustain_overlap() -> None:
    score_events = guitar_score_events()
    categories = guitar_category_indices()

    assert len(score_events) == 16
    assert len(categories["chord_onsets"]) == 4
    assert len(categories["arpeggio_under_sustain"]) == 12
    assert GUITAR_EVENT_CLASSES[0] == "chord_onset"
    assert len(score_events[0].midi_pitches) == 5


def test_polyphonic_oracle_follows_complete_guitar_score() -> None:
    clustered = cluster_simultaneous_note_events(guitar_note_level_events())
    result = CausalSymbolicFollower(guitar_score_events()).run_events(clustered)

    assert len(clustered) == 16
    assert len(result.updates) == 16
    assert result.updates[-1].score_beat == 15.0
    assert result.backend_metrics["matched_events"] == 16
    assert guitar_expected_onsets()[-1] == (15.0, 7.5)
