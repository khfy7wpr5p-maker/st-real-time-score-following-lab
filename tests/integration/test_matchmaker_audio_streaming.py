from pathlib import Path
from threading import Event, Thread
from time import sleep

import pytest

pytest.importorskip("matchmaker")
np = pytest.importorskip("numpy")
partitura = pytest.importorskip("partitura")

from matchmaker.features.audio import (  # noqa: E402
    FRAME_RATE,
    SAMPLE_RATE,
    ChromagramProcessor,
)
from matchmaker.io.audio import BytesAudioStream  # noqa: E402
from matchmaker.utils.misc import generate_score_audio  # noqa: E402
from partitura.score import merge_parts  # noqa: E402

from st_score_following.followers import MatchmakerAdapter  # noqa: E402
from st_score_following.streaming import (  # noqa: E402
    BoundedStreamIngress,
    ByteQueueBridge,
    ObservedByteQueue,
)


def _accepted_put(
    ingress: BoundedStreamIngress[bytes],
    payload: bytes,
    stop_event: Event,
) -> bool:
    while not stop_event.is_set():
        if ingress.put(payload) is not None:
            return True
        sleep(0.0005)
    return False


def _render_fixture_audio(score_path: Path):
    score = partitura.load_musicxml(str(score_path), ignore_invisible_objects=True)
    score_part = merge_parts(score.parts)
    return np.asarray(
        generate_score_audio(score_part, bpm=120.0, samplerate=SAMPLE_RATE),
        dtype=np.float32,
    )


def test_bounded_pcm_bytes_drive_matchmaker_audio_score_position() -> None:
    score_path = Path(__file__).parents[1] / "fixtures" / "synthetic_piano.musicxml"
    audio = _render_fixture_audio(score_path)
    hop_length = SAMPLE_RATE // FRAME_RATE
    frame_duration_s = hop_length / SAMPLE_RATE

    stop_event = Event()
    ingress = BoundedStreamIngress[bytes](maxsize=4)
    backend_queue = ObservedByteQueue(maxsize=4)
    bridge = ByteQueueBridge(
        ingress=ingress,
        target_queue=backend_queue,
        stop_event=stop_event,
    )
    bridge_result = {}
    errors: list[BaseException] = []

    def pump_bridge() -> None:
        try:
            bridge_result["stats"] = bridge.pump()
        except BaseException as exc:  # pragma: no cover - surfaced below
            errors.append(exc)

    def produce() -> None:
        try:
            for start in range(0, len(audio), hop_length):
                if stop_event.is_set():
                    break
                chunk = audio[start : start + hop_length]
                if len(chunk) < hop_length:
                    chunk = np.pad(chunk, (0, hop_length - len(chunk)))
                payload = np.asarray(chunk, dtype=np.float32).tobytes()
                if not _accepted_put(ingress, payload, stop_event):
                    break
                stop_event.wait(frame_duration_s)
        finally:
            ingress.close()

    bridge_thread = Thread(target=pump_bridge, daemon=True)
    producer_thread = Thread(target=produce, daemon=True)
    bridge_thread.start()
    producer_thread.start()

    stream = BytesAudioStream(
        processor=ChromagramProcessor(
            sample_rate=SAMPLE_RATE,
            hop_length=hop_length,
        ),
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
    stop_event.set()

    producer_thread.join(timeout=2)
    bridge_thread.join(timeout=2)

    assert not errors
    assert not producer_thread.is_alive()
    assert not bridge_thread.is_alive()
    assert len(result.updates) > 0
    assert max(update.score_beat for update in result.updates) >= 1.0
    assert ingress.stats().dropped_oldest == 0

    bridge_stats = bridge_result["stats"]
    assert bridge_stats.forwarded > 0
    assert bridge_stats.p95_transport_latency_s >= 0
    assert bridge_stats.max_transport_latency_s >= bridge_stats.p95_transport_latency_s

    pipeline = result.backend_metrics["pipeline_latency"]
    assert pipeline["samples"] > 0
    assert pipeline["mean_s"] >= 0
    assert pipeline["p95_s"] >= 0
    assert pipeline["max_s"] >= pipeline["p95_s"]
