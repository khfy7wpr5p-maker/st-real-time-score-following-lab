from __future__ import annotations

from dataclasses import dataclass
from queue import Full
from threading import Event
from typing import Any

from st_score_following.clock import summarize_latency_s

from .ingress import BoundedStreamIngress


@dataclass(frozen=True, slots=True)
class BridgeStats:
    forwarded: int
    target_timeouts: int
    cancelled: bool
    mean_transport_latency_s: float
    p95_transport_latency_s: float
    max_transport_latency_s: float


class ByteQueueBridge:
    """Forward ST-timestamped byte packets into a bounded backend byte queue."""

    def __init__(
        self,
        *,
        ingress: BoundedStreamIngress[bytes],
        target_queue: Any,
        stop_event: Event | None = None,
        target_put_timeout_s: float = 0.05,
        max_consecutive_target_timeouts: int = 200,
    ) -> None:
        if target_put_timeout_s <= 0:
            raise ValueError("target_put_timeout_s must be > 0")
        if max_consecutive_target_timeouts <= 0:
            raise ValueError("max_consecutive_target_timeouts must be > 0")
        self._ingress = ingress
        self._target_queue = target_queue
        self._stop_event = stop_event
        self._target_put_timeout_s = target_put_timeout_s
        self._max_consecutive_target_timeouts = max_consecutive_target_timeouts

    def _stopped(self) -> bool:
        return self._stop_event is not None and self._stop_event.is_set()

    def _put_target(
        self,
        payload: bytes | None,
        *,
        source_arrival_s: float | None,
    ) -> tuple[int, bool]:
        consecutive_timeouts = 0
        total_timeouts = 0
        while True:
            if self._stopped():
                return total_timeouts, False
            try:
                put_packet = getattr(self._target_queue, "put_packet", None)
                if callable(put_packet):
                    put_packet(
                        payload,
                        source_arrival_s=source_arrival_s,
                        timeout=self._target_put_timeout_s,
                    )
                else:
                    self._target_queue.put(payload, timeout=self._target_put_timeout_s)
                return total_timeouts, True
            except Full as exc:
                consecutive_timeouts += 1
                total_timeouts += 1
                if self._stopped():
                    return total_timeouts, False
                if consecutive_timeouts >= self._max_consecutive_target_timeouts:
                    raise TimeoutError("backend stream queue remained full") from exc

    def pump(self) -> BridgeStats:
        forwarded = 0
        target_timeouts = 0
        transport_latencies_s: list[float] = []
        cancelled = False

        while True:
            if self._stopped():
                cancelled = True
                break
            try:
                packet = self._ingress.get(timeout_s=0.1)
            except TimeoutError:
                continue

            if packet is None:
                timeouts, delivered = self._put_target(None, source_arrival_s=None)
                target_timeouts += timeouts
                cancelled = not delivered
                break

            timeouts, delivered = self._put_target(
                packet.payload,
                source_arrival_s=packet.arrived_at_s,
            )
            target_timeouts += timeouts
            if not delivered:
                cancelled = True
                break
            transport_latencies_s.append(self._ingress.now_s() - packet.arrived_at_s)
            forwarded += 1

        latency = summarize_latency_s(transport_latencies_s)
        return BridgeStats(
            forwarded=forwarded,
            target_timeouts=target_timeouts,
            cancelled=cancelled,
            mean_transport_latency_s=latency.mean_s,
            p95_transport_latency_s=latency.p95_s,
            max_transport_latency_s=latency.max_s,
        )
