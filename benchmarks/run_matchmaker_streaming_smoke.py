from __future__ import annotations

import json
from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep

from matchmaker.io.midi import BytesMidiStream

from st_score_following.evaluation import SYNTHETIC_NOTES
from st_score_following.followers import MatchmakerAdapter
from st_score_following.streaming import BoundedStreamIngress, ByteQueueBridge


def _accepted_put(ingress: BoundedStreamIngress[bytes], payload: bytes) -> None:
    while ingress.put(payload) is None:
        sleep(0.0005)


def run() -> dict[str, object]:
    score = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic_piano.musicxml"
    ingress = BoundedStreamIngress[bytes](maxsize=8)
    backend_queue: Queue[bytes | None] = Queue(maxsize=8)
    bridge = ByteQueueBridge(ingress=ingress, target_queue=backend_queue)
    bridge_result = {}
    errors: list[str] = []

    def pump_bridge() -> None:
        try:
            bridge_result["stats"] = bridge.pump()
        except BaseException as exc:  # pragma: no cover - CLI evidence
            errors.append(repr(exc))

    def produce() -> None:
        try:
            for pitch in SYNTHETIC_NOTES:
                _accepted_put(ingress, bytes((0x90, pitch, 80)))
                sleep(0.001)
                _accepted_put(ingress, bytes((0x80, pitch, 0)))
        finally:
            ingress.close()

    bridge_thread = Thread(target=pump_bridge, daemon=True)
    producer_thread = Thread(target=produce, daemon=True)
    bridge_thread.start()
    producer_thread.start()

    stream = BytesMidiStream(data_queue=backend_queue, polling_period=None)
    result = MatchmakerAdapter().run_stream(
        score_file=str(score),
        stream=stream,
        input_type="midi",
        method="pthmm",
        emitted_clock=ingress.now_s,
    )

    producer_thread.join(timeout=2)
    bridge_thread.join(timeout=2)
    if errors or producer_thread.is_alive() or bridge_thread.is_alive():
        raise RuntimeError(f"streaming workers failed: {errors}")

    bridge_stats = bridge_result["stats"]
    ingress_stats = ingress.stats()
    update_times = [update.emitted_at_s for update in result.updates]

    return {
        "schema": "st.score_following.streaming_benchmark.v1",
        "fixture": "synthetic_piano_midi_bytes_v1",
        "backend": result.backend,
        "backend_version": result.backend_version,
        "method": result.method,
        "input_type": result.input_type,
        "score_position_updates": len(result.updates),
        "max_score_beat": max((update.score_beat for update in result.updates), default=None),
        "first_update_at_s": min(update_times) if update_times else None,
        "last_update_at_s": max(update_times) if update_times else None,
        "wall_duration_s": result.wall_duration_s,
        "confidence_available": result.confidence_available,
        "ingress": {
            "maxsize": ingress.maxsize,
            "accepted": ingress_stats.accepted,
            "rejected_newest": ingress_stats.rejected_newest,
            "dropped_oldest": ingress_stats.dropped_oldest,
            "max_depth": ingress_stats.max_depth,
        },
        "bridge": {
            "forwarded": bridge_stats.forwarded,
            "target_timeouts": bridge_stats.target_timeouts,
            "mean_transport_latency_ms": bridge_stats.mean_transport_latency_s * 1000,
            "max_transport_latency_ms": bridge_stats.max_transport_latency_s * 1000,
        },
        "limitations": [
            "Synthetic Web-MIDI-style bytes, not physical MIDI hardware or microphone audio.",
            "Bridge latency measures ST ingress-to-backend-queue transport, not full acoustic end-to-end latency.",
            "Backend stream timing remains Matchmaker-owned internally; ST canonical arrival/emission timestamps use StreamClock.",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
