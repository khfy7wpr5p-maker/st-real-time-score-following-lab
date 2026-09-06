import pytest

from st_score_following import LatencySample, StreamClock, summarize_latency_s


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


def test_latency_summary_reports_mean_p95_and_max() -> None:
    summary = summarize_latency_s([0.001, 0.002, 0.003, 0.010])
    assert summary.count == 4
    assert summary.mean_s == pytest.approx(0.004)
    assert summary.p95_s == pytest.approx(0.00895)
    assert summary.max_s == pytest.approx(0.010)


def test_latency_summary_rejects_negative_samples() -> None:
    with pytest.raises(ValueError):
        summarize_latency_s([0.001, -0.001])
