import pytest

from st_score_following.followers import MatchmakerAdapter


class FakeMatchmaker:
    def __init__(self, **kwargs):
        self.method = kwargs.get("method") or "pthmm"
        self.alignment_duration = None

    def run(self, verbose=False):
        del verbose
        yield 0.0
        yield 1.0
        self.alignment_duration = 0.01
        return [(0.0, 0.0), (1.0, 0.5)]


def test_adapter_normalizes_generator_return_path() -> None:
    adapter = MatchmakerAdapter(
        factory=FakeMatchmaker,
        backend_version="0.3.0",
    )
    result = adapter.run_files(
        score_file="score.musicxml",
        performance_file="performance.mid",
        input_type="midi",
        method="pthmm",
    )

    assert [update.score_beat for update in result.updates] == [0.0, 1.0]
    assert [point.performance_time_s for point in result.alignment_path] == [0.0, 0.5]
    assert result.backend_alignment_duration_s == pytest.approx(0.01)
    assert result.confidence_available is False


def test_stream_ready_hook_runs_after_backend_construction_before_consumption() -> None:
    order: list[str] = []

    class OrderedFakeMatchmaker(FakeMatchmaker):
        def __init__(self, **kwargs):
            order.append("constructed")
            super().__init__(**kwargs)

        def run(self, verbose=False):
            order.append("run")
            yield from super().run(verbose=verbose)

    adapter = MatchmakerAdapter(
        factory=OrderedFakeMatchmaker,
        backend_version="0.3.0",
    )
    adapter.run_stream(
        score_file="score.musicxml",
        stream=object(),
        input_type="midi",
        method="pthmm",
        on_ready=lambda: order.append("ready"),
    )

    assert order[:3] == ["constructed", "ready", "run"]


def test_adapter_rejects_unknown_backend_version() -> None:
    with pytest.raises(RuntimeError):
        MatchmakerAdapter(
            factory=FakeMatchmaker,
            backend_version="9.9.9",
        )
