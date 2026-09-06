from __future__ import annotations

from pathlib import Path

SYNTHETIC_NOTES = (
    60,
    62,
    64,
    65,
    67,
    69,
    71,
    72,
    72,
    71,
    69,
    67,
    65,
    64,
    62,
    60,
)


def _vlq(value: int) -> bytes:
    if value < 0:
        raise ValueError("variable-length quantity must be non-negative")
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buffer))


def write_quarter_note_midi(
    path: str | Path,
    *,
    notes: tuple[int, ...] = SYNTHETIC_NOTES,
    bpm: int = 120,
    ticks_per_beat: int = 480,
) -> None:
    if bpm <= 0:
        raise ValueError("bpm must be positive")
    if ticks_per_beat <= 0 or ticks_per_beat > 0x7FFF:
        raise ValueError("ticks_per_beat must be within MIDI header range")
    if any(note < 0 or note > 127 for note in notes):
        raise ValueError("notes must be valid MIDI pitches")

    microseconds_per_beat = round(60_000_000 / bpm)
    tempo = microseconds_per_beat.to_bytes(3, byteorder="big")

    track = bytearray()
    track.extend(b"\x00\xff\x51\x03")
    track.extend(tempo)
    track.extend(b"\x00\xc0\x00")

    for note in notes:
        track.extend(_vlq(0))
        track.extend(bytes((0x90, note, 80)))
        track.extend(_vlq(ticks_per_beat))
        track.extend(bytes((0x80, note, 0)))

    track.extend(b"\x00\xff\x2f\x00")

    header = b"MThd" + (6).to_bytes(4, "big")
    header += (0).to_bytes(2, "big")
    header += (1).to_bytes(2, "big")
    header += ticks_per_beat.to_bytes(2, "big")
    body = b"MTrk" + len(track).to_bytes(4, "big") + bytes(track)
    Path(path).write_bytes(header + body)
