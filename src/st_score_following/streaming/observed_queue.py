from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from queue import Queue
from threading import Lock


@dataclass(frozen=True, slots=True)
class _ObservedByteItem:
    payload: bytes | None
    source_arrival_s: float | None


class ObservedByteQueue:
    """Byte queue that exposes the ST arrival time of the last consumed packet.

    Matchmaker still receives plain ``bytes``/``None`` from ``get``. The side-channel
    timestamp is used only for ST latency instrumentation and never changes backend data.
    """

    def __init__(self, maxsize: int = 0) -> None:
        if maxsize < 0:
            raise ValueError("maxsize must be >= 0")
        self.maxsize = maxsize
        self._queue: Queue[_ObservedByteItem] = Queue(maxsize=maxsize)
        self._lock = Lock()
        self._last_source_arrival_s: float | None = None

    def put(
        self,
        payload: bytes | None,
        block: bool = True,
        timeout: float | None = None,
    ) -> None:
        self._queue.put(
            _ObservedByteItem(payload=payload, source_arrival_s=None),
            block=block,
            timeout=timeout,
        )

    def put_packet(
        self,
        payload: bytes | None,
        *,
        source_arrival_s: float | None,
        timeout: float | None = None,
    ) -> None:
        if source_arrival_s is not None:
            if not isfinite(source_arrival_s) or source_arrival_s < 0:
                raise ValueError("source_arrival_s must be finite and >= 0")
        self._queue.put(
            _ObservedByteItem(payload=payload, source_arrival_s=source_arrival_s),
            timeout=timeout,
        )

    def put_nowait(self, payload: bytes | None) -> None:
        self.put(payload, block=False)

    def get(
        self,
        block: bool = True,
        timeout: float | None = None,
    ) -> bytes | None:
        item = self._queue.get(block=block, timeout=timeout)
        if item.source_arrival_s is not None:
            with self._lock:
                self._last_source_arrival_s = item.source_arrival_s
        return item.payload

    def last_source_arrival_s(self) -> float | None:
        with self._lock:
            return self._last_source_arrival_s
