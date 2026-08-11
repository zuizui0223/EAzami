#!/usr/bin/env python3
"""Compare normalized OMA Read2Tree marker packs by actual reference sequences.

Marker filenames are profile-specific and therefore not a valid overlap key.
This comparator uses the sorted three-OMA-ID signature in each normalized AA
marker FASTA. It reports exact group overlap and individual reference-sequence
overlap between the automated static400 and Browser-export400 profiles.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Iterable, Mapping, Sequence

EXPECTED_CODES = ("CYNCS", "HELAN", "DAUCS")
SIGNATURE_FIELDS = (
    "marker_signature",
    "profile_a_marker_file",
    "profile_b_marker_file",
    "present_in_profile_a",
    "present_in_profile_b",
)
OMA_ID_RE = re.compile(r"^([A-Z0-9]{5}\d{5})$")


def clean(value: object) -> str:
    return str(value or "").strip()


def load_contract(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("contract_version") != "eazami_read2tree_oma_marker_pack_v1":
        raise ValueError(f"{path}: unsupported marker-pack contract")
    if payload.get("execution_allowed") is not True:
        raise ValueError(f"{path}: marker pack is not execution-allowed")
    if payload.get("oma_release") != "May2026":
        raise ValueError(f"{path}: expected May2026 marker pack")
    codes = tuple(payload.get("reference_codes", []))
    if codes != EXPECTED_CODES:
        raise ValueError(f"{path}: unexpected reference codes {codes}")
    return payload


def fasta_ids(path: Path) -> tuple[str, ...]:
    ids: list[str] = []
    with path.open(encoding="utf-8") as handle:
        for raw in handle:
            if not raw.startswith(">"):
                continue
            seq_id = raw[1:].strip().split()[0]
            if not OMA_ID_RE.fullmatch(seq_id):
                raise ValueError(f"{path}: invalid OMA sequence ID {seq_id!r}")
            ids.append(seq_id)
    if not ids:
        raise ValueError(f"{path}: no FASTA sequence IDs")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path}: duplicate OMA sequence IDs")
    return tuple(ids)


def marker_signatures(
    contract_path: Path,
    *,
    expected_count: int = 400,
) -> tuple[dict[str, str], set[str], dict[str, object]]:
    contract = load_contract(contract_path)
    marker_dir = contract_path.parent / clean(contract.get("normalized_marker_dir"))
    if not marker_dir.is_dir():
        raise ValueError(f"{contract_path}: marker directory missing: {marker_dir}")
    files = sorted(marker_dir.glob("*.fa"))
    if len(files) != expected_count:
        raise ValueError(
            f"{contract_path}: expected {expected_count} AA markers, observed {len(files)}"
        )
    signatures: dict[str, str] = {}
    all_ids: set[str] = set()
    for path in files:
        ids = fasta_ids(path)
        codes = tuple(seq_id[:5] for seq_id in ids)
        if len(ids) != 3 or set(codes) != set(EXPECTED_CODES):
            raise ValueError(
                f"{path}: expected exactly one sequence for {EXPECTED_CODES}, observed {ids}"
            )
        signature = "|".join(sorted(ids))
        if signature in signatures:
            raise ValueError(
                f"{contract_path}: duplicate marker signature in {path.name} and {signatures[signature]}"
            )
        signatures[signature] = path.name
        all_ids.update(ids)
    return signatures, all_ids, contract


def overlap_class(intersection: int, marker_count: int) -> str:
    if intersection == marker_count:
        return "identical_marker_sets"
    fraction = intersection / marker_count if marker_count else 0.0
    if fraction >= 0.75:
        return "high_overlap"
    if fraction >= 0.25:
        return "moderate_overlap"
    return "low_overlap"


def compare_packs(
    profile_a_contract: Path,
    profile_b_contract: Path,
    *,
    expected_count: int = 400,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    a_groups, a_ids, a_contract = marker_signatures(
        profile_a_contract, expected_count=expected_count
    )
    b_groups, b_ids, b_contract = marker_signatures(
        profile_b_contract, expected_count=expected_count
    )
    a_set = set(a_groups)
    b_set = set(b_groups)
    intersection = a_set & b_set
    union = a_set | b_set
    id_intersection = a_ids & b_ids
    id_union = a_ids | b_ids

    rows = []
    for signature in sorted(union):
        rows.append(
            {
                "marker_signature": signature,
                "profile_a_marker_file": a_groups.get(signature, ""),
                "profile_b_marker_file": b_groups.get(signature, ""),
                "present_in_profile_a": str(signature in a_set).lower(),
                "present_in_profile_b": str(signature in b_set).lower(),
            }
        )

    marker_jaccard = len(intersection) / len(union) if union else 1.0
    sequence_jaccard = len(id_intersection) / len(id_union) if id_union else 1.0
    summary = {
        "analysis": "OMA Read2Tree normalized marker-pack overlap",
        "oma_release": "May2026",
        "reference_codes": list(EXPECTED_CODES),
        "profile_a_contract": str(profile_a_contract),
        "profile_b_contract": str(profile_b_contract),
        "profile_a_pack_sha256": clean(a_contract.get("normalized_pack_sha256")),
        "profile_b_pack_sha256": clean(b_contract.get("normalized_pack_sha256")),
        "marker_count_each": expected_count,
        "exact_marker_group_intersection": len(intersection),
        "exact_marker_group_union": len(union),
        "marker_group_jaccard": marker_jaccard,
        "profile_a_group_overlap_fraction": len(intersection) / len(a_set),
        "profile_b_group_overlap_fraction": len(intersection) / len(b_set),
        "reference_sequence_ids_profile_a": len(a_ids),
        "reference_sequence_ids_profile_b": len(b_ids),
        "reference_sequence_id_intersection": len(id_intersection),
        "reference_sequence_id_union": len(id_union),
        "reference_sequence_id_jaccard": sequence_jaccard,
        "overlap_classification": overlap_class(len(intersection), expected_count),
        "interpretation": (
            "Marker-group identity is defined by the exact sorted CYNCS/HELAN/DAUCS OMA-ID triplet, not by profile-specific filenames."
        ),
        "claim_limit": (
            "Marker overlap quantifies one design dimension only. High overlap does not make two profile trees independent, and low overlap does not by itself validate either topology."
        ),
    }
    return rows, summary


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SIGNATURE_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-a-contract", type=Path, required=True)
    parser.add_argument("--profile-b-contract", type=Path, required=True)
    parser.add_argument("--expected-marker-count", type=int, default=400)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows, summary = compare_packs(
        args.profile_a_contract,
        args.profile_b_contract,
        expected_count=args.expected_marker_count,
    )
    write_csv(args.output, rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"marker_group_intersection={summary['exact_marker_group_intersection']}")
    print(f"marker_group_jaccard={summary['marker_group_jaccard']:.6f}")
    print(f"reference_sequence_id_jaccard={summary['reference_sequence_id_jaccard']:.6f}")
    print(f"overlap_classification={summary['overlap_classification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
