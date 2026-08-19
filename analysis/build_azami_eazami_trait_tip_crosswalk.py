#!/usr/bin/env python3
"""Build a fail-closed Azami→EAzami trait-tip crosswalk.

Automatic matches require exact normalized taxon concepts. Broad species names are
not silently assigned to infraspecific Chang lineages. The crosswalk describes
available evidence; it does not graft missing taxa or infer ancestral states.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


INFRA_MARKERS = {"var.", "subsp.", "ssp.", "f."}


def normalize_name(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    text = re.sub(r"^C\.\s+", "Cirsium ", text)
    text = re.sub(r"\s+", " ", text)
    tokens = text.split()
    if len(tokens) < 2:
        return text
    result = [tokens[0], tokens[1].strip(",;()")]
    for index, token in enumerate(tokens[2:], start=2):
        if token in INFRA_MARKERS and index + 1 < len(tokens):
            result.extend([token, tokens[index + 1].strip(",;()")])
            break
    return " ".join(result)


def species_binomial(value: object) -> str:
    normalized = normalize_name(value)
    tokens = normalized.split()
    return " ".join(tokens[:2]) if len(tokens) >= 2 else normalized


def grouped_index(frame: pd.DataFrame, columns: list[str], payload_columns: list[str]) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, set[str]]] = {}
    for _, row in frame.iterrows():
        names = {normalize_name(row[column]) for column in columns if column in frame.columns}
        names.discard("")
        for name in names:
            bucket = records.setdefault(name, {column: set() for column in payload_columns})
            for column in payload_columns:
                if column in frame.columns and pd.notna(row[column]) and str(row[column]).strip():
                    bucket[column].add(str(row[column]).strip())
    output: dict[str, dict[str, str]] = {}
    for name, payload in records.items():
        output[name] = {key: "|".join(sorted(values)) for key, values in payload.items()}
    return output


def build_crosswalk(
    handoff: pd.DataFrame,
    moreyra: pd.DataFrame,
    japan38: pd.DataFrame,
    chang2025: pd.DataFrame | None = None,
    chang2026: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, dict]:
    if handoff["taxon_name"].duplicated().any():
        raise ValueError("Azami handoff must be unique by taxon_name")

    moreyra_index = grouped_index(
        moreyra,
        ["tree_code", "published_species", "sra_scientific_name"],
        ["tree_code", "run", "biosample"],
    )
    chang_frames = [frame for frame in (chang2025, chang2026) if frame is not None]
    chang_index: dict[str, dict[str, str]] = {}
    for frame in chang_frames:
        index = grouped_index(
            frame,
            [column for column in ("taxon", "accepted_taxon", "published_taxon") if column in frame.columns],
            [column for column in ("code", "run", "embedded_public_accession", "voucher") if column in frame.columns],
        )
        for name, payload in index.items():
            bucket = chang_index.setdefault(name, {})
            for key, value in payload.items():
                if not value:
                    continue
                existing = set(filter(None, bucket.get(key, "").split("|")))
                existing.update(filter(None, value.split("|")))
                bucket[key] = "|".join(sorted(existing))

    japan38_bins: dict[str, list[dict]] = {}
    for _, row in japan38.iterrows():
        concept = species_binomial(row.get("paper_taxon_concept", ""))
        if concept:
            japan38_bins.setdefault(concept, []).append(row.to_dict())

    rows = []
    for _, source in handoff.iterrows():
        name = normalize_name(source["taxon_name"])
        binomial = species_binomial(name)
        m = moreyra_index.get(name)
        c = chang_index.get(name)
        jrecords = japan38_bins.get(binomial, [])

        sources = []
        if m:
            sources.append("Moreyra2025")
        if c:
            sources.append("Chang2025_2026")

        if m or c:
            match_status = "direct_exact_nuclear_match"
        else:
            match_status = "no_exact_nuclear_match"

        japan38_ids = sorted({str(record.get("paper_japan_member_id", "")) for record in jrecords if record.get("paper_japan_member_id")})
        japan38_concepts = sorted({str(record.get("paper_taxon_concept", "")) for record in jrecords if record.get("paper_taxon_concept")})

        row = source.to_dict()
        row.update({
            "accepted_analysis_taxon": name,
            "nuclear_match_status": match_status,
            "nuclear_match_sources": "|".join(sources),
            "moreyra_tree_codes": (m or {}).get("tree_code", ""),
            "moreyra_runs": (m or {}).get("run", ""),
            "moreyra_biosamples": (m or {}).get("biosample", ""),
            "chang_codes": (c or {}).get("code", ""),
            "chang_runs_or_accessions": "|".join(filter(None, [(c or {}).get("run", ""), (c or {}).get("embedded_public_accession", "")])),
            "japan38_binomial_match": "yes" if jrecords else "no",
            "japan38_member_ids": "|".join(japan38_ids),
            "japan38_paper_concepts": "|".join(japan38_concepts),
            "crosswalk_claim_boundary": (
                "exact normalized nuclear-name match only; Japan38 uses binomial membership for coverage accounting; "
                "no infraspecific assignment, grafting, ancestry or ancestral-state inference"
            ),
        })
        rows.append(row)

    result = pd.DataFrame(rows).sort_values("taxon_name").reset_index(drop=True)
    japan_rows = result.loc[result["japan38_binomial_match"].eq("yes")]
    direct = result.loc[result["nuclear_match_status"].eq("direct_exact_nuclear_match")]
    direct_japan = japan_rows.loc[japan_rows["nuclear_match_status"].eq("direct_exact_nuclear_match")]
    unique_japan_ids = set()
    for value in japan_rows["japan38_member_ids"]:
        unique_japan_ids.update(filter(None, str(value).split("|")))

    summary = {
        "contract_version": "azami_eazami_trait_tip_crosswalk_v1",
        "n_azami_taxa": int(len(result)),
        "n_exact_nuclear_matched_azami_taxa": int(len(direct)),
        "exact_nuclear_match_fraction": float(len(direct) / len(result)) if len(result) else 0.0,
        "n_azami_taxa_matching_japan38_binomial": int(len(japan_rows)),
        "n_japan38_paper_concepts_represented_by_azami_traits": int(len(unique_japan_ids)),
        "n_direct_nuclear_matched_japan38_trait_taxa": int(len(direct_japan)),
        "n_direct_nuclear_matched_taxa_with_auxiliary_proxy": int(direct["n_usable_heads_species"].fillna(0).gt(0).sum()),
        "interpretation": (
            "Coverage audit only. A taxon may have a direct nuclear match while its population/morph state remains unresolved; "
            "Japan38 coverage does not imply adequate trait replication or direct wild-voucher equivalence."
        ),
    }
    return result, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--azami-handoff", required=True)
    parser.add_argument("--moreyra-reconciliation", required=True)
    parser.add_argument("--japan38", required=True)
    parser.add_argument("--chang2025")
    parser.add_argument("--chang2026")
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    handoff = pd.read_csv(args.azami_handoff)
    moreyra = pd.read_csv(args.moreyra_reconciliation)
    japan38 = pd.read_csv(args.japan38)
    chang2025 = pd.read_csv(args.chang2025) if args.chang2025 else None
    chang2026 = pd.read_csv(args.chang2026) if args.chang2026 else None

    result, summary = build_crosswalk(handoff, moreyra, japan38, chang2025, chang2026)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.to_csv(out / "azami_eazami_trait_tip_crosswalk_v1.csv", index=False, encoding="utf-8")
    (out / "azami_eazami_trait_tip_crosswalk_v1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
