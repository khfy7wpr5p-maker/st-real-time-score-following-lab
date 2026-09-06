from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import StrEnum
from threading import Condition
from typing import Generic, TypeVar

from st_score_following.clock import StreamClock

T = TypeVar("T")


class OverflowPolicy(StrEnum):
    REJECT_NEWEST = "reject_newest"
    DROP_OLDEST = "drop_oldest"


@dataclass(frozen=True, slots=True)
class StreamPacket(Generic[T]):
    sequence_id: int
    arrived_at_s: float
    payload: T


@dataclass(frozen=True, slots=True)
class IngressStats:
    accepted: int
    rejected_newest: int
    dropped_oldest: int
    max_depth: int
    current_depth: int
    closed: bool


class BoundedStreamIngress(Generic[T]):
    """Thread-safe bounded ingress with explicit overflow and monotonic arrival time."""

    def __init__(
        self,
        *,
        maxsize: int,
        overflow_policy: OverflowPolicy = OverflowPolicy.REJECT_NEWEST,
        clock: StreamClock | None = None,
    ) -> None:
        if maxsize <= 0:
            raise ValueError("maxsize must be > 0")
        self._maxsize = maxsize
        self._overflow_policy = overflow_policy
        self._clock = clock or StreamClock()
        self._items: deque[StreamPacket[T]] = deque()
        self._condition = Condition()
        self._closed = False
        self._next_sequence_id = 0
        self._accepted = 0
        self._rejected_newest = 0
        self._dropped_oldest = 0
        self._max_depth = 0

    def now_s(self) -> float:
        return self._clock.now_s()

    def put(self, payload: T) -> StreamPacket[T] | None:
        with self._condition:
            if self._closed:
                raise RuntimeError("cannot put into closed stream ingress")

            if len(self._items) >= self._maxsize:
                if self._overflow_policy is OverflowPolicy.REJECT_NEWEST:
                    self._rejected_newest += 1
                    return None
                self._items.popleft()
                self._dropped_oldest += 1

            packet = StreamPacket(
                sequence_id=self._next_sequence_id,
                arrived_at_s=self._clock.now_s(),
                payload=payload,
            )
            self._next_sequence_id += 1
            self._items.append(packet)
            self._accepted += 1
            self._max_depth = max(self._max_depth, len(self._items))
            self._condition.notify()
            return packet

    def get(self, *, timeout_s: float | None = None) -> StreamPacket[T] | None:
        if timeout_s is not None and timeout_s < 0:
            raise ValueError("timeout_s must be >= 0 or None")

        with self._condition:
            if not self._items and not self._closed:
                ready = self._condition.wait_for(
                    lambda: bool(self._items) or self._closed,
                    timeout=timeout_s,
                )
                if not ready:
                    raise TimeoutError("stream ingress read timed out")

            if self._items:
                return self._items.popleft()
            return None

    def close(self) -> None:
        with self._condition:
            self._closed = True
            self._condition.notify_all()

    @property
    def closed(self) -> bool:
        with self._condition:
            return self._closed

    @property
    def maxsize(self) -> int:
        return self._maxsize

    def stats(self) -> IngressStats:
        with self._condition:
            return IngressStats(
                accepted=self._accepted,
                rejected_newest=self._rejected_newest,
                dropped_oldest=self._dropped_oldest,
                max_depth=self._max_depth,
                current_depth=len(self._items),
                closed=self._closed,
            )
