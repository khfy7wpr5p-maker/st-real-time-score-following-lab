from st_score_following.clock import StreamClock
from st_score_following.streaming import BoundedStreamIngress, OverflowPolicy


def test_ingress_assigns_sequence_and_monotonic_arrival_time() -> None:
    samples = iter([10.0, 10.1, 10.2])
    ingress = BoundedStreamIngress[str](
        maxsize=2,
        clock=StreamClock(lambda: next(samples)),
    )

    first = ingress.put("a")
    second = ingress.put("b")

    assert first is not None and first.sequence_id == 0
    assert second is not None and second.sequence_id == 1
    assert first.arrived_at_s == 0.1
    assert second.arrived_at_s == 0.2


def test_reject_newest_is_explicit_and_counted() -> None:
    ingress = BoundedStreamIngress[str](maxsize=1)
    assert ingress.put("a") is not None
    assert ingress.put("b") is None

    stats = ingress.stats()
    assert stats.accepted == 1
    assert stats.rejected_newest == 1
    assert stats.dropped_oldest == 0


def test_drop_oldest_keeps_latest_packet() -> None:
    ingress = BoundedStreamIngress[str](
        maxsize=1,
        overflow_policy=OverflowPolicy.DROP_OLDEST,
    )
    ingress.put("a")
    ingress.put("b")

    packet = ingress.get(timeout_s=0)
    assert packet is not None and packet.payload == "b"
    assert ingress.stats().dropped_oldest == 1


def test_close_drains_then_signals_end_of_stream() -> None:
    ingress = BoundedStreamIngress[str](maxsize=2)
    ingress.put("a")
    ingress.close()

    packet = ingress.get(timeout_s=0)
    assert packet is not None and packet.payload == "a"
    assert ingress.get(timeout_s=0) is None
