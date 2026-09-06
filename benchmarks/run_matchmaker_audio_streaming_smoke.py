from __future__ import annotations

import json
from pathlib import Path
from threading import Thread
from time import sleep

import numpy as np
import partitura
from matchmaker.features.audio import FRAME_RATE, SAMPLE_RATE, ChromagramProcessor
from matchmaker.io.audio import BytesAudioStream
from matchmaker.utils.misc import generate_score_audio
from partitura.score import merge_parts

from st_score_following.followers import MatchmakerAdapter
from st_score_following.streaming import (
    BoundedStreamIngress,
    ByteQueueBridge,
    ObservedByteQueue,
)


def _accepted_put(ingress: BoundedStreamIngress[bytes], payload: bytes) -> None:
    while ingress.put(payload) is None:
        sleep(0.0005)


def _render_fixture_audio(score_path: Path) -> np.ndarray:
    score = partitura.load_musicxml(str(score_path), ignore_invisible_objects=True)
    score_part = merge_parts(score.parts)
    return np.asarray(
        generate_score_audio(score_part, bpm=120.0, samplerate=SAMPLE_RATE),
        dtype=np.float32,
    )


def run() -> dict[str, object]:
    score_path = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic_piano.musicxml"
    audio = _render_fixture_audio(score_path)
    hop_length = SAMPLE_RATE // FRAME_RATE
    frame_duration_s = hop_length / SAMPLE_RATE

    ingress = BoundedStreamIngress[bytes](maxsize=4)
    backend_queue = ObservedByteQueue(maxsize=4)
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
            for start in range(0, len(audio), hop_length):
                chunk = audio[start : start + hop_length]
                if len(chunk) < hop_length:
                    chunk = np.pad(chunk, (0, hop_length - len(chunk)))
                _accepted_put(ingress, np.asarray(chunk, dtype=np.float32).tobytes())
                sleep(frame_duration_s)
        finally:
            ingress.close()

    bridge_thread = Thread(target=pump_bridge, daemon=True)
    producer_thread = Thread(target=produce, daemon=True)
    bridge_thread.start()
    producer_thread.start()

    stream = BytesAudioStream(
        processor=ChromagramProcessor(sample_rate=SAMPLE_RATE, hop_length=hop_length),
        sample_rate=SAMPLE_RATE,
        hop_length=hop_length,
        data_queue=backend_queue,
    )
    result = MatchmakerAdapter().run_stream(
        score_file=str(score_path),
        stream=stream,
        input_type="audio",
        method="arzt",
        emitted_clock=ingress.now_s,
        source_arrival_clock=backend_queue.last_source_arrival_s,
    )

    producer_thread.join(timeout=12)
    bridge_thread.join(timeout=12)
    if errors or producer_thread.is_alive() or bridge_thread.is_alive():
        raise RuntimeError(f"audio streaming workers failed: {errors}")

    ingress_stats = ingress.stats()
    bridge_stats = bridge_result["stats"]
    pipeline = result.backend_metrics.get("pipeline_latency")

    return {
        "schema": "st.score_following.audio_streaming_benchmark.v1",
        "fixture": "synthetic_rendered_score_pcm_v1",
        "backend": result.backend,
        "backend_version": result.backend_version,
        "method": result.method,
        "sample_rate": SAMPLE_RATE,
        "hop_length": hop_length,
        "nominal_frame_rate": FRAME_RATE,
        "audio_duration_s": len(audio) / SAMPLE_RATE,
        "score_position_updates": len(result.updates),
        "max_score_beat": max((update.score_beat for update in result.updates), default=None),
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
            "p95_transport_latency_ms": bridge_stats.p95_transport_latency_s * 1000,
            "max_transport_latency_ms": bridge_stats.max_transport_latency_s * 1000,
        },
        "pipeline_latency": None
        if pipeline is None
        else {
            "boundary": pipeline["boundary"],
            "samples": pipeline["samples"],
            "mean_ms": pipeline["mean_s"] * 1000,
            "p95_ms": pipeline["p95_s"] * 1000,
            "max_ms": pipeline["max_s"] * 1000,
        },
        "limitations": [
            "PCM is deterministically rendered from the synthetic score, not microphone capture.",
            (
                "The fixture is a transport/realtime architecture smoke test, "
                "not musical robustness evidence."
            ),
            "Matchmaker does not expose calibrated confidence for these score-position updates.",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
