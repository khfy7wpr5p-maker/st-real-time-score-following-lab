from __future__ import annotations

import json

from st_score_following import (
    OrchestraGlobalObservationV1,
    OrchestraGlobalScorePointV1,
    OrchestraSectionAnalyzer,
    OrchestraSectionFamily,
    OrchestraSectionInputV1,
)

BASE = (
    (0, 4, 5, 7, 8),
    (0, 2, 5, 8, 11),
    (1, 2, 3, 5, 6),
    (1, 3, 6, 8, 9),
    (2, 3, 5, 9, 10),
    (3, 5, 7, 8, 10),
    (1, 3, 4, 8, 11),
    (2, 3, 7, 8, 10),
    (1, 4, 6, 9, 11),
    (1, 2, 4, 7, 9),
    (0, 1, 4, 6, 8),
    (4, 5, 7, 10, 11),
    (0, 3, 5, 6, 11),
    (0, 1, 4, 7, 9),
    (3, 4, 5, 9, 10),
    (0, 4, 7, 8, 9),
)
CONFIG = {
    "violins": (OrchestraSectionFamily.VIOLINS, 0, 0.000),
    "strings": (OrchestraSectionFamily.STRINGS, 2, 0.015),
    "winds": (OrchestraSectionFamily.WINDS, 5, 0.030),
    "brass": (OrchestraSectionFamily.BRASS, 7, 0.045),
}


def _texture(index: int, shift: int) -> tuple[int, ...]:
    return tuple(sorted({(value + shift) % 12 for value in BASE[index]}))


def _dense_texture(index: int, shift: int) -> tuple[int, ...]:
    values = set(_texture(index, shift))
    expected = sorted(values)
    values.remove(expected[index % len(expected)])
    extra = (index * 5 + shift + 3) % 12
    while extra in values:
        extra = (extra + 1) % 12
    values.add(extra)
    return tuple(sorted(values))


def _section(
    name: str,
    *,
    indices: tuple[int, ...] = tuple(range(16)),
    dense: bool = False,
) -> OrchestraSectionInputV1:
    family, shift, offset = CONFIG[name]
    score = tuple(
        OrchestraGlobalScorePointV1(
            score_index=index,
            measure_index=index // 4 + 1,
            beat_in_measure=float(index % 4 + 1),
            score_beat=float(index),
            texture_pitch_classes=_texture(index, shift),
        )
        for index in range(16)
    )
    observations = tuple(
        OrchestraGlobalObservationV1(
            event_id=f"{name}-{ordinal}-{score_index}",
            observed_at_s=ordinal * 0.5 + offset,
            texture_pitch_classes=(
                _dense_texture(score_index, shift)
                if dense
                else _texture(score_index, shift)
            ),
            confidence=None,
        )
        for ordinal, score_index in enumerate(indices)
    )
    return OrchestraSectionInputV1(
        section_id=f"section-{name}",
        family=family,
        source_provenance=f"repository_fixture:{name}",
        score_points=score,
        observations=observations,
    )


def _case(
    name: str,
    *,
    overrides: dict[str, tuple[int, ...]] | None = None,
    dense_sections: frozenset[str] = frozenset(),
) -> dict[str, object]:
    overrides = overrides or {}
    sections = tuple(
        _section(
            section_name,
            indices=overrides.get(section_name, tuple(range(16))),
            dense=section_name in dense_sections,
        )
        for section_name in CONFIG
    )
    report = OrchestraSectionAnalyzer(sections).run()
    final = report.snapshots[-1]
    return {
        "name": name,
        "authority_boundary": report.authority_boundary,
        "sections": [
            {
                "section_id": section.section_id,
                "family": section.family.value,
                "matched_observations": section.report.summary.matched_observations,
                "unmatched_observations": section.report.summary.unmatched_observations,
                "forward_skipped_score_points": section.report.summary.forward_skipped_score_points,
                "backward_jumps": section.report.summary.backward_jumps,
                "confidence_available_matches": section.report.summary.confidence_available_matches,
            }
            for section in report.sections
        ],
        "fusion_summary": report.summary.to_dict(),
        "final_snapshot": {
            "status": final.status.value,
            "fused_score_index": final.fused_score_index,
            "fused_measure_index": final.fused_measure_index,
            "fused_beat_in_measure": final.fused_beat_in_measure,
            "contributing_section_ids": final.contributing_section_ids,
            "disagreeing_section_ids": final.disagreeing_section_ids,
            "stale_section_ids": final.stale_section_ids,
            "unavailable_section_ids": final.unavailable_section_ids,
            "confidence": final.confidence,
        },
    }


def main() -> None:
    stopped = tuple(range(6))
    advanced_winds = tuple(range(6)) + tuple(range(8, 16))
    output = {
        "schema": "st.score_following.orchestra_section_benchmark.v1",
        "authority_boundary": (
            "orchestra_section_fusion_research_not_acoustic_source_separation_authority"
        ),
        "productization_decision": "research_only_no_productization_yet",
        "decision_basis": [
            "deterministic section identity/fusion behavior is structurally testable",
            "independent section followers remain auditable under dropout and disagreement",
            "real acoustic section extraction and source separation are not established",
            "real section-level confidence calibration is unavailable",
            "therefore section intelligence remains a research candidate rather than a production feature",
        ],
        "boundaries": [
            "section labels are repository-owned synthetic research groups",
            "no mono-room acoustic source separation is performed",
            "3-of-4 fusion publishes a position only when three recent sections agree exactly",
            "divergent or below-quorum evidence publishes no fused position",
            "fused confidence remains unavailable",
        ],
        "cases": {
            "clean": _case("clean"),
            "dense_strings_proxy": _case(
                "dense_strings_proxy",
                dense_sections=frozenset({"strings"}),
            ),
            "strings_dropout": _case(
                "strings_dropout",
                overrides={"strings": tuple(range(8))},
            ),
            "advancing_winds": _case(
                "advancing_winds",
                overrides={"winds": advanced_winds},
            ),
            "two_section_loss": _case(
                "two_section_loss",
                overrides={"violins": stopped, "strings": stopped},
            ),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
