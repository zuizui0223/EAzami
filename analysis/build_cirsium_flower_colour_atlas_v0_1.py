#!/usr/bin/env python3
"""Build the source-backed v0.1 Cirsium flower-colour atlas.

The builder intentionally starts small and high-confidence.  It combines three
existing EAzami evidence streams without silently promoting weak evidence:

1. six taxon-level Arenicola/Nipponocirsium states that are directly supported
   by Chang et al. 2025/2026 text and are already used in the topology screen;
2. six morph-linked var. takaoense public RNA-seq samples whose W/BP labels are
   directly tied to voucher/run/BioSample evidence;
3. the Japan colour-evidence seed, retained as pending until exact page-level
   provenance and phylogenetic tip mapping are frozen.

Rate fitting is a *separate* eligibility field.  Direct sample-level takaoense
records are biologically real observations but are not independent species-tree
tips, so they are excluded from cross-species transition-rate fitting until an
empirical within-variety topology is available.  Polymorphic or unresolved
species records are never silently collapsed to W or C.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_ARENICOLA = Path("data/evidence/arenicola_flower_colour_history_evidence_v1.csv")
DEFAULT_TAKAOENSE = Path("data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv")
DEFAULT_JAPAN = Path("data/japan_colour_evidence_seed.csv")
DEFAULT_OUTPUT = Path("data/evidence/cirsium_flower_colour_atlas_v0_1.csv")

FIELDS = (
    "record_id", "accepted_taxon", "source_taxon_name", "country", "region",
    "locality", "latitude", "longitude", "population_id", "observation_unit",
    "observation_id", "evidence_type", "evidence_source", "evidence_id",
    "source_url", "source_locator", "observation_date", "life_stage",
    "assessable", "colour_state", "binary_colour_code", "binary_collapse_rule",
    "anthocyanin_visible", "polymorphic_context", "phylogeny_context",
    "phylogeny_tip_candidate", "rate_fit_eligible", "rate_fit_exclusion_reason",
    "evidence_status", "lab_l", "lab_a", "lab_b", "chroma", "hue_deg",
    "notes", "review_status",
)

FINE_TO_BINARY = {
    "white": "W",
    "near_white": "W",
    "pale_pink": "C",
    "pink": "C",
    "purple": "C",
    "blue_purple": "C",
    "polymorphic": "P",
    "unknown": "U",
}


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            {key: clean(value) for key, value in row.items()}
            for row in csv.DictReader(handle)
            if any(clean(value) for value in row.values())
        ]


def blank_row() -> dict[str, str]:
    return {field: "" for field in FIELDS}


def normalized_colour_from_binary(binary: str, source_text: str = "") -> str:
    binary = clean(binary).upper()
    text = clean(source_text).casefold()
    if binary == "W":
        return "white"
    if binary == "C":
        if "bluish" in text or "blue" in text or text == "bp":
            return "blue_purple"
        if "pink" in text:
            return "pink"
        return "purple"
    raise ValueError(f"Cannot normalize binary colour {binary!r}")


def build_arenicola_rows(path: Path) -> list[dict[str, str]]:
    source = read_csv(path)
    rows: list[dict[str, str]] = []
    tips = [row for row in source if row.get("evidence_type") == "tip_flower_colour"]
    if len(tips) != 6:
        raise ValueError(f"Expected six source-backed Arenicola/Nipponocirsium tips, observed {len(tips)}")
    cluster = {
        "Cirsium brevicaule": "Arenicola",
        "Cirsium irumtiense": "Arenicola",
        "Cirsium morii": "Nipponocirsium",
        "Cirsium pengii": "Nipponocirsium",
        "Cirsium kawakamii": "Nipponocirsium",
        "Cirsium tatakaense": "Nipponocirsium",
    }
    for index, item in enumerate(tips, start=1):
        state = clean(item.get("state_or_fact")).upper()
        if state not in {"C", "W"}:
            raise ValueError(f"Unexpected Arenicola evidence state: {item}")
        taxon = clean(item.get("taxon_or_node"))
        if taxon not in cluster:
            raise ValueError(f"Unexpected source-backed tip taxon {taxon!r}")
        row = blank_row()
        row.update(
            {
                "record_id": f"ATL-A{index:02d}",
                "accepted_taxon": taxon,
                "source_taxon_name": taxon,
                "country": "Taiwan" if cluster[taxon] == "Nipponocirsium" else "Japan",
                "observation_unit": "taxon",
                "observation_id": taxon,
                "evidence_type": "published_taxon_description",
                "evidence_source": clean(item.get("source")),
                "evidence_id": clean(item.get("record_id")),
                "source_url": clean(item.get("source_url")),
                "source_locator": clean(item.get("source_locator")),
                "life_stage": "flower",
                "assessable": "yes",
                "colour_state": "white" if state == "W" else "purple",
                "binary_colour_code": state,
                "binary_collapse_rule": "white/near_white->W; visible pink/purple/blue-purple->C",
                "anthocyanin_visible": "no" if state == "W" else "yes",
                "phylogeny_context": cluster[taxon],
                "phylogeny_tip_candidate": "yes",
                "rate_fit_eligible": "yes",
                "rate_fit_exclusion_reason": "",
                "evidence_status": "direct_taxon_text",
                "notes": clean(item.get("notes")),
                "review_status": "reviewed",
            }
        )
        rows.append(row)
    return rows


def build_takaoense_rows(path: Path) -> list[dict[str, str]]:
    source = read_csv(path)
    if len(source) != 6:
        raise ValueError(f"Expected six morph-linked takaoense samples, observed {len(source)}")
    rows: list[dict[str, str]] = []
    for index, item in enumerate(sorted(source, key=lambda r: clean(r.get("code"))), start=1):
        binary = clean(item.get("binary_colour_code")).upper()
        if binary not in {"C", "W"}:
            raise ValueError(f"Unexpected takaoense colour code: {item}")
        code = clean(item.get("code"))
        voucher = clean(item.get("voucher"))
        run = clean(item.get("run"))
        biosample = clean(item.get("biosample"))
        if not all((code, voucher, run, biosample)):
            raise ValueError(f"Incomplete takaoense direct-evidence row: {item}")
        location = clean(item.get("location"))
        region = location.split(":", 1)[0].replace("TAIWAN.", "").strip() if location else ""
        locality = location.split(":", 1)[1].strip() if ":" in location else location
        row = blank_row()
        row.update(
            {
                "record_id": f"ATL-T{index:02d}",
                "accepted_taxon": "Cirsium japonicum var. takaoense",
                "source_taxon_name": clean(item.get("accepted_taxon")),
                "country": "Taiwan",
                "region": region,
                "locality": locality,
                "latitude": clean(item.get("latitude_decimal")),
                "longitude": clean(item.get("longitude_decimal")),
                "population_id": code,
                "observation_unit": "sample",
                "observation_id": f"{code}_{voucher}",
                "evidence_type": "published_morph_linked_sample",
                "evidence_source": "Chang et al. 2026 Figure 1 + public SRA/BioSample linkage",
                "evidence_id": f"{run}|{biosample}|{voucher}",
                "source_url": "https://doi.org/10.1186/s12870-026-08097-6",
                "source_locator": f"Figure 1 labels {code}-{voucher} ({clean(item.get('published_figure_label'))}); SRA {run}; BioSample {biosample}",
                "life_stage": "flower phenotype linked to young-leaf RNA sample",
                "assessable": "yes",
                "colour_state": normalized_colour_from_binary(binary, clean(item.get("flower_colour_state"))),
                "binary_colour_code": binary,
                "binary_collapse_rule": "published W->W; published BP/bluish-purple->C",
                "anthocyanin_visible": "no" if binary == "W" else "yes",
                "polymorphic_context": "same accepted variety contains directly linked W and BP samples",
                "phylogeny_context": "Sinocirsium/takaoense_within_variety",
                "phylogeny_tip_candidate": "yes",
                "rate_fit_eligible": "no",
                "rate_fit_exclusion_reason": "sample-level morph record; not an independent species-tree tip and empirical within-variety topology is still being tested",
                "evidence_status": clean(item.get("evidence_status")),
                "notes": clean(item.get("limitations")),
                "review_status": "reviewed",
            }
        )
        rows.append(row)
    return rows


def build_japan_seed_rows(path: Path) -> list[dict[str, str]]:
    source = read_csv(path)
    rows: list[dict[str, str]] = []
    mapping = {
        "polymorphic_purple_white": ("polymorphic", "P"),
        "coloured_red_purple": ("purple", "C"),
        "colour_not_textually_coded": ("unknown", "U"),
    }
    for index, item in enumerate(source, start=1):
        raw = clean(item.get("colour_state"))
        if raw not in mapping:
            raise ValueError(f"Unsupported Japan seed colour_state {raw!r}")
        fine, binary = mapping[raw]
        taxon = clean(item.get("accepted_taxon"))
        row = blank_row()
        row.update(
            {
                "record_id": f"ATL-J{index:02d}",
                "accepted_taxon": taxon,
                "source_taxon_name": taxon,
                "country": "Japan",
                "observation_unit": "taxon",
                "observation_id": taxon,
                "evidence_type": clean(item.get("evidence_type")),
                "evidence_source": clean(item.get("evidence_source")),
                "evidence_id": clean(item.get("japanese_name")),
                "source_locator": clean(item.get("source_detail")),
                "life_stage": "flower",
                "assessable": "no" if binary == "U" else "yes",
                "colour_state": fine,
                "binary_colour_code": binary,
                "binary_collapse_rule": "candidate seed only; polymorphic is retained as P and unknown as U",
                "anthocyanin_visible": "unknown" if binary in {"P", "U"} else "yes",
                "polymorphic_context": clean(item.get("source_detail")) if binary == "P" else "",
                "phylogeny_context": "Japan_seed_unmapped",
                "phylogeny_tip_candidate": "no",
                "rate_fit_eligible": "no",
                "rate_fit_exclusion_reason": "exact source URL/locator and nuclear-tree tip mapping have not yet been frozen" if binary != "U" else "flower colour not textually coded; image/spectral review still required",
                "evidence_status": "official_database_seed_pending_exact_provenance",
                "notes": clean(item.get("priority_implication")),
                "review_status": "pending",
            }
        )
        rows.append(row)
    return rows


def build(arenicola: Path, takaoense: Path, japan: Path) -> list[dict[str, str]]:
    rows = build_arenicola_rows(arenicola) + build_takaoense_rows(takaoense) + build_japan_seed_rows(japan)
    ids = [row["record_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Generated atlas record IDs are not unique")
    return rows


def write_csv(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arenicola", type=Path, default=DEFAULT_ARENICOLA)
    parser.add_argument("--takaoense", type=Path, default=DEFAULT_TAKAOENSE)
    parser.add_argument("--japan-seed", type=Path, default=DEFAULT_JAPAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build(args.arenicola, args.takaoense, args.japan_seed)
    write_csv(args.output, rows)
    print(f"atlas_records={len(rows)}")
    print(f"taxon_level_records={sum(row['observation_unit']=='taxon' for row in rows)}")
    print(f"sample_level_records={sum(row['observation_unit']=='sample' for row in rows)}")
    print(f"rate_fit_eligible={sum(row['rate_fit_eligible']=='yes' for row in rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
