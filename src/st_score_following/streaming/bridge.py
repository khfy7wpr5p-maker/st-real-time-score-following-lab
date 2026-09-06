from __future__ import annotations

from dataclasses import dataclass
from queue import Full, Queue

from .ingress import BoundedStreamIngress


@dataclass(frozen=True, slots=True)
class BridgeStats:
    forwarded: int
    target_timeouts: int
    mean_transport_latency_s: float
    max_transport_latency_s: float


class ByteQueueBridge:
    """Forward ST-timestamped byte packets into a bounded backend byte queue."""

    def __init__(
        self,
        *,
        ingress: BoundedStreamIngress[bytes],
        target_queue: Queue[bytes | None],
        target_put_timeout_s: float = 0.05,
        max_consecutive_target_timeouts: int = 200,
    ) -> None:
        if target_put_timeout_s <= 0:
            raise ValueError("target_put_timeout_s must be > 0")
        if max_consecutive_target_timeouts <= 0:
            raise ValueError("max_consecutive_target_timeouts must be > 0")
        self._ingress = ingress
        self._target_queue = target_queue
        self._target_put_timeout_s = target_put_timeout_s
        self._max_consecutive_target_timeouts = max_consecutive_target_timeouts

    def _put_target(self, payload: bytes | None) -> int:
        consecutive_timeouts = 0
        total_timeouts = 0
        while True:
            try:
                self._target_queue.put(payload, timeout=self._target_put_timeout_s)
                return total_timeouts
            except Full as exc:
                consecutive_timeouts += 1
                total_timeouts += 1
                if consecutive_timeouts >= self._max_consecutive_target_timeouts:
                    raise TimeoutError("backend stream queue remained full") from exc

    def pump(self) -> BridgeStats:
        forwarded = 0
        target_timeouts = 0
        total_transport_latency_s = 0.0
        max_transport_latency_s = 0.0

        while True:
            try:
                packet = self._ingress.get(timeout_s=0.1)
            except TimeoutError:
                continue

            if packet is None:
                target_timeouts += self._put_target(None)
                break

            target_timeouts += self._put_target(packet.payload)
            latency_s = self._ingress.now_s() - packet.arrived_at_s
            total_transport_latency_s += latency_s
            max_transport_latency_s = max(max_transport_latency_s, latency_s)
            forwarded += 1

        mean_latency_s = total_transport_latency_s / forwarded if forwarded else 0.0
        return BridgeStats(
            forwarded=forwarded,
            target_timeouts=target_timeouts,
            mean_transport_latency_s=mean_latency_s,
            max_transport_latency_s=max_transport_latency_s,
        )
