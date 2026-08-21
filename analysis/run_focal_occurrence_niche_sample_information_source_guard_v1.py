#!/usr/bin/env python3
"""Run the focal niche audit with a source-name guard against GBIF synonym collapse.

GBIF currently resolves some focal taxa (notably Cirsium irumtiense) as synonyms of
other focal taxa (notably C. brevicaule). A taxon-key query can therefore return
records whose accepted name is C. brevicaule but whose source scientificName is
C. irumtiense. That collapse is unacceptable for EAzami's colour-history and
population-sampling questions.

This wrapper preserves v1's niche calculations but filters every downloaded taxon
packet by the record-level source `scientificName` before coordinate cleaning.
It also appends source-name inclusion/exclusion counts to the frozen summary.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_focal_occurrence_niche_sample_information_v1 as v1  # noqa: E402

SOURCE_FILTER_COUNTS: dict[str, dict[str, int]] = {}
_BASE_CLEAN = v1.clean_and_thin


def normalize_name(value: object) -> str:
    return " ".join(str(value or "").strip().split())


def source_name_matches_query(source_name: object, query_name: object) -> bool:
    """Accept the query species itself and its infraspecific/source-author variants.

    Examples accepted for query ``Cirsium brevicaule``:
    - ``Cirsium brevicaule``
    - ``Cirsium brevicaule A.Gray``
    - ``Cirsium brevicaule var. ...``

    A record explicitly source-labelled ``Cirsium irumtiense ...`` is rejected even
    when GBIF's acceptedScientificName is C. brevicaule.
    """
    source = normalize_name(source_name).casefold()
    query = normalize_name(query_name).casefold()
    return bool(source and query and (source == query or source.startswith(query + " ")))


def guarded_clean_and_thin(raw: pd.DataFrame, cfg: dict):
    if raw.empty:
        return _BASE_CLEAN(raw, cfg)
    queries = [normalize_name(x) for x in raw["scientific_name_query"].dropna().unique()]
    if len(queries) != 1:
        raise ValueError(f"Expected one query taxon per GBIF packet, found {queries}")
    query = queries[0]
    mask = raw["scientificName"].map(lambda x: source_name_matches_query(x, query))
    kept = raw.loc[mask].copy()
    SOURCE_FILTER_COUNTS[query] = {
        "n_pre_source_filter": int(len(raw)),
        "n_source_taxon_match": int(mask.sum()),
        "n_source_taxon_excluded": int((~mask).sum()),
    }
    primary, meta = _BASE_CLEAN(kept, cfg)
    meta.update(SOURCE_FILTER_COUNTS[query])
    return primary, meta


def append_source_filter_counts(out_dir: Path) -> None:
    summary_path = out_dir / "focal_niche_sampling_summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError(summary_path)
    summary = pd.read_csv(summary_path)
    for column in ["n_pre_source_filter", "n_source_taxon_match", "n_source_taxon_excluded"]:
        summary[column] = summary["taxon"].map(
            lambda taxon: SOURCE_FILTER_COUNTS.get(str(taxon), {}).get(column, 0)
        )
    summary.to_csv(summary_path, index=False)

    matches_path = out_dir / "gbif_taxon_matches.csv"
    if matches_path.exists():
        matches = pd.read_csv(matches_path)
        for column in ["n_pre_source_filter", "n_source_taxon_match", "n_source_taxon_excluded"]:
            matches[column] = matches["query_name"].map(
                lambda taxon: SOURCE_FILTER_COUNTS.get(str(taxon), {}).get(column, 0)
            )
        matches.to_csv(matches_path, index=False)


if __name__ == "__main__":
    # v1.main() parses the same CLI arguments and calls the monkeypatched cleaner.
    v1.clean_and_thin = guarded_clean_and_thin
    argv = sys.argv[1:]
    out_dir = None
    for i, arg in enumerate(argv):
        if arg == "--out-dir" and i + 1 < len(argv):
            out_dir = Path(argv[i + 1])
            break
        if arg.startswith("--out-dir="):
            out_dir = Path(arg.split("=", 1)[1])
            break
    if out_dir is None:
        raise SystemExit("--out-dir is required")
    v1.main()
    append_source_filter_counts(out_dir)
