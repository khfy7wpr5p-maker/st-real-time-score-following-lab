import pytest

from st_score_following import LatencySample, StreamClock


def test_stream_clock_is_relative() -> None:
    samples = iter([100.0, 100.25, 100.5])
    clock = StreamClock(lambda: next(samples))
    assert clock.now_s() == pytest.approx(0.25)
    assert clock.now_s() == pytest.approx(0.5)


def test_stream_clock_detects_backwards_time() -> None:
    samples = iter([10.0, 9.0])
    clock = StreamClock(lambda: next(samples))
    with pytest.raises(RuntimeError):
        clock.now_s()


def test_latency_sample() -> None:
    sample = LatencySample(input_timestamp_s=1.0, output_timestamp_s=1.075)
    assert sample.latency_s == pytest.approx(0.075)
