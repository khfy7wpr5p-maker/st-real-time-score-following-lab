from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep

import pytest

pytest.importorskip("matchmaker")

from matchmaker.features.midi import PitchProcessor  # noqa: E402
from matchmaker.io.midi import BytesMidiStream  # noqa: E402

from st_score_following.evaluation import SYNTHETIC_NOTES  # noqa: E402
from st_score_following.followers import MatchmakerAdapter  # noqa: E402
from st_score_following.streaming import (  # noqa: E402
    BoundedStreamIngress,
    ByteQueueBridge,
)


def _accepted_put(ingress: BoundedStreamIngress[bytes], payload: bytes) -> None:
    while ingress.put(payload) is None:
        sleep(0.0005)


def test_bounded_midi_bytes_drive_matchmaker_score_position() -> None:
    score = Path(__file__).parents[1] / "fixtures" / "synthetic_piano.musicxml"
    ingress = BoundedStreamIngress[bytes](maxsize=8)
    backend_queue: Queue[bytes | None] = Queue(maxsize=8)
    bridge = ByteQueueBridge(ingress=ingress, target_queue=backend_queue)
    bridge_result = {}
    bridge_errors: list[BaseException] = []

    def pump_bridge() -> None:
        try:
            bridge_result["stats"] = bridge.pump()
        except BaseException as exc:  # pragma: no cover - surfaced below
            bridge_errors.append(exc)

    def produce() -> None:
        for pitch in SYNTHETIC_NOTES:
            _accepted_put(ingress, bytes((0x90, pitch, 80)))
            sleep(0.001)
            _accepted_put(ingress, bytes((0x80, pitch, 0)))
        ingress.close()

    bridge_thread = Thread(target=pump_bridge, daemon=True)
    producer_thread = Thread(target=produce, daemon=True)
    bridge_thread.start()
    producer_thread.start()

    stream = BytesMidiStream(
        processor=PitchProcessor(piano_range=True),
        data_queue=backend_queue,
        polling_period=None,
    )
    result = MatchmakerAdapter().run_stream(
        score_file=str(score),
        stream=stream,
        input_type="midi",
        method="pthmm",
        emitted_clock=ingress.now_s,
    )

    producer_thread.join(timeout=2)
    bridge_thread.join(timeout=2)

    assert not bridge_errors
    assert not producer_thread.is_alive()
    assert not bridge_thread.is_alive()
    assert len(result.updates) > 0
    assert max(update.score_beat for update in result.updates) >= 1.0
    assert all(update.emitted_at_s >= 0 for update in result.updates)
    assert bridge_result["stats"].forwarded == len(SYNTHETIC_NOTES) * 2
    assert ingress.stats().dropped_oldest == 0
