#!/usr/bin/env python3
"""Build a fail-closed Japan-38 capitulum-trait bridge from the NMNS thistle index.

Only short categorical states are derived from the authority index catchphrases.
The source prose is not redistributed: rows retain a SHA-256 of the catchphrase,
source URL and taxon labels. Exact infraspecific matches are required when the
paper concept is infraspecific; otherwise a unique species-binomial candidate is
reported as sensitivity-only rather than silently accepted.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
from pathlib import Path

import pandas as pd
import requests


DEFAULT_URL = "https://www.kahaku.go.jp/research/db/botany/azami/list.html?word=all"
INFRA_MARKERS = {"var.", "subsp.", "ssp.", "f."}


def clean(value: object) -> str:
    text = "" if value is None or pd.isna(value) else str(value)
    text = text.replace("\u3000", " ").replace("（", "(").replace("）", ")")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_taxon(value: object) -> str:
    text = clean(value)
    text = re.sub(r"^C\.\s+", "Cirsium ", text)
    tokens = text.split()
    if len(tokens) < 2:
        return text
    result = [tokens[0], tokens[1].strip(",;()")]
    for i, token in enumerate(tokens[2:], start=2):
        if token in INFRA_MARKERS and i + 1 < len(tokens):
            result += [token, tokens[i + 1].strip(",;()")]
            break
    return " ".join(result)


def binomial(value: object) -> str:
    tokens = normalize_taxon(value).split()
    return " ".join(tokens[:2]) if len(tokens) >= 2 else " ".join(tokens)


def has_infra(value: object) -> bool:
    return any(token in normalize_taxon(value).split() for token in INFRA_MARKERS)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def classify_orientation(text: str) -> str:
    t = clean(text)
    states = []
    if any(key in t for key in ("下向き", "点頭", "懸垂")):
        states.append("downward_or_nodding")
    if "横向き" in t:
        states.append("lateral")
    if any(key in t for key in ("上向き", "直立")):
        states.append("upward_or_erect")
    if any(key in t for key in ("斜め上向き", "斜上")):
        states.append("ascending")
    return "|".join(dict.fromkeys(states)) if states else "unknown_from_index_catchphrase"


def classify_phyllary(text: str) -> str:
    t = clean(text)
    states = []
    if "圧着" in t:
        states.append("appressed")
    if "斜上" in t:
        states.append("ascending")
    if "開出" in t or "張り出" in t:
        states.append("spreading")
    if "反曲" in t or "反り返" in t:
        states.append("recurved")
    return "|".join(dict.fromkeys(states)) if states else "unknown_from_index_catchphrase"


def classify_stickiness(text: str) -> str:
    t = clean(text)
    if any(key in t for key in ("粘らない", "粘らず")):
        return "nonsticky_or_nearly_nonsticky"
    if "ほとんど粘らない" in t:
        return "nonsticky_or_nearly_nonsticky"
    if any(key in t for key in ("著しく粘る", "良く粘る", "よく粘る", "粘る", "粘着")):
        return "sticky"
    return "unknown_from_index_catchphrase"


def find_nmns_table(html: str) -> pd.DataFrame:
    tables = pd.read_html(io.StringIO(html))
    for table in tables:
        cols = {clean(col) for col in table.columns}
        if "種名" in cols and "キャッチフレーズ" in cols:
            table = table.copy()
            table.columns = [clean(col) for col in table.columns]
            return table
    raise ValueError("Could not locate NMNS thistle index table")


def build_bridge(membership: pd.DataFrame, nmns: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    required = {"paper_japan_member_id", "paper_taxon_concept"}
    if required.difference(membership.columns):
        raise ValueError("Japan-38 membership is incomplete")
    for column in ("種名", "変種名", "キャッチフレーズ"):
        if column not in nmns.columns:
            raise ValueError(f"NMNS table lacks {column}")

    source = nmns.copy()
    source["nmns_species"] = source["種名"].map(clean)
    source["nmns_infra"] = source["変種名"].map(clean)
    source["nmns_concept_raw"] = (
        source["nmns_species"] + " " + source["nmns_infra"]
    ).str.strip()
    source["nmns_concept"] = source["nmns_concept_raw"].map(normalize_taxon)
    source["nmns_binomial"] = source["nmns_species"].map(binomial)
    source["catchphrase"] = source["キャッチフレーズ"].map(clean)

    rows = []
    for _, paper in membership.iterrows():
        paper_raw = clean(paper["paper_taxon_concept"])
        paper_norm = normalize_taxon(paper_raw)
        paper_bin = binomial(paper_norm)
        exact = source.loc[source["nmns_concept"].eq(paper_norm)].copy()
        candidates = source.loc[source["nmns_binomial"].eq(paper_bin)].copy()

        if len(exact) == 1:
            chosen = exact.iloc[0]
            match_status = "exact_authority_concept_match"
        elif not has_infra(paper_norm) and len(candidates) == 1:
            chosen = candidates.iloc[0]
            match_status = "unique_binomial_authority_match"
        else:
            chosen = None
            match_status = (
                "no_exact_match_infraspecific_or_taxonomy_review_required"
                if has_infra(paper_norm)
                else "ambiguous_or_missing_authority_match"
            )

        row = {
            "paper_japan_member_id": paper["paper_japan_member_id"],
            "paper_taxon_concept": paper_raw,
            "paper_normalized_concept": paper_norm,
            "paper_species_binomial": paper_bin,
            "authority_match_status": match_status,
            "nmns_taxon_concept": "",
            "orientation_state_from_index": "unknown",
            "phyllary_posture_from_index": "unknown",
            "stickiness_from_index": "unknown",
            "source_catchphrase_sha256": "",
            "source_url": DEFAULT_URL,
            "claim_boundary": (
                "authority index categorical screening only; no continuous image value, genotype linkage, "
                "ancestral state, evolutionary rate or adaptation inferred"
            ),
        }
        if chosen is not None:
            phrase = clean(chosen["catchphrase"])
            row.update({
                "nmns_taxon_concept": clean(chosen["nmns_concept_raw"]),
                "orientation_state_from_index": classify_orientation(phrase),
                "phyllary_posture_from_index": classify_phyllary(phrase),
                "stickiness_from_index": classify_stickiness(phrase),
                "source_catchphrase_sha256": sha256_text(phrase),
            })
        rows.append(row)

    result = pd.DataFrame(rows)
    matched = result["nmns_taxon_concept"].ne("")
    orientation = ~result["orientation_state_from_index"].isin(["unknown", "unknown_from_index_catchphrase"])
    phyllary = ~result["phyllary_posture_from_index"].isin(["unknown", "unknown_from_index_catchphrase"])
    sticky = ~result["stickiness_from_index"].isin(["unknown", "unknown_from_index_catchphrase"])
    summary = {
        "contract_version": "japan38_nmns_capitulum_trait_bridge_v1",
        "n_paper_concepts": int(len(result)),
        "n_authority_matched_concepts": int(matched.sum()),
        "n_orientation_states_recovered": int(orientation.sum()),
        "n_phyllary_posture_states_recovered": int(phyllary.sum()),
        "n_stickiness_states_recovered": int(sticky.sum()),
        "n_exact_authority_concept_matches": int(result["authority_match_status"].eq("exact_authority_concept_match").sum()),
        "n_unique_binomial_matches": int(result["authority_match_status"].eq("unique_binomial_authority_match").sum()),
        "n_taxonomy_review_required": int((~matched).sum()),
        "claim_boundary": (
            "The NMNS index provides authority-backed categorical morphology useful for coverage and later "
            "ASR sensitivity. It is not a substitute for individual measurements or a resolved phylogeny."
        ),
    }
    return result, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--japan38", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--url", default=DEFAULT_URL)
    args = parser.parse_args()

    response = requests.get(args.url, timeout=60)
    response.raise_for_status()
    nmns = find_nmns_table(response.text)
    membership = pd.read_csv(args.japan38, dtype=str, keep_default_na=False)
    bridge, summary = build_bridge(membership, nmns)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bridge.to_csv(out / "japan38_nmns_capitulum_trait_bridge_v1.csv", index=False, encoding="utf-8")
    (out / "japan38_nmns_capitulum_trait_bridge_v1.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (out / "nmns_source_metadata.json").write_text(
        json.dumps({
            "url": args.url,
            "html_sha256": hashlib.sha256(response.content).hexdigest(),
            "n_source_rows": int(len(nmns)),
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
