from queue import Queue

from st_score_following.streaming import BoundedStreamIngress, ByteQueueBridge


def test_bridge_forwards_bytes_and_end_sentinel() -> None:
    ingress = BoundedStreamIngress[bytes](maxsize=4)
    target: Queue[bytes | None] = Queue(maxsize=4)
    ingress.put(b"one")
    ingress.put(b"two")
    ingress.close()

    stats = ByteQueueBridge(ingress=ingress, target_queue=target).pump()

    assert target.get_nowait() == b"one"
    assert target.get_nowait() == b"two"
    assert target.get_nowait() is None
    assert stats.forwarded == 2
    assert stats.mean_transport_latency_s >= 0
    assert stats.max_transport_latency_s >= 0
