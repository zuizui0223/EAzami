#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

TAXA = [
    "Cirsium brevicaule",
    "Cirsium irumtiense",
    "Cirsium kawakamii",
    "Cirsium tatakaense",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--source-manifest", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--max-observations-per-taxon", type=int, default=50)
    p.add_argument("--max-photos-per-observation", type=int, default=3)
    p.add_argument("--timeout-sec", type=int, default=60)
    return p.parse_args()


def numeric_key(value: object) -> tuple[int, str]:
    text = "" if pd.isna(value) else str(value).strip()
    try:
        return (0, f"{int(float(text)):020d}")
    except Exception:
        return (1, text)


def safe_slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1.0,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=8, pool_maxsize=8)
    s.mount("https://", adapter)
    s.headers.update({"User-Agent": "EAzami-public-image-pilot/1.0 research-use"})
    return s


def main() -> int:
    args = parse_args()
    source = pd.read_csv(args.source_manifest, dtype=str, keep_default_na=False)
    required = {
        "system_id", "focal_taxon", "colour_state", "pair_role", "source",
        "source_observation_id", "source_photo_id", "photo_url", "observer_id",
        "observed_on", "latitude", "longitude", "photo_license",
    }
    missing = sorted(required.difference(source.columns))
    if missing:
        raise ValueError(f"source manifest missing columns: {missing}")

    # Keep one public platform only. This avoids GBIF/iNaturalist duplicate and synonym
    # issues and makes both sister systems use the same source contract.
    work = source[
        source["source"].eq("iNaturalist")
        & source["focal_taxon"].isin(TAXA)
        & source["photo_url"].astype(str).str.startswith("http")
    ].copy()
    # The audit manifest can contain the same iNaturalist photo more than once through
    # source bookkeeping. A photo is one image measurement unit, so remove exact
    # taxon/observation/photo duplicates before any candidate selection or download.
    work = work.drop_duplicates(
        ["focal_taxon", "source_observation_id", "source_photo_id"], keep="first"
    ).copy()
    if set(work["focal_taxon"]) != set(TAXA):
        raise ValueError("all four focal taxa must resolve in iNaturalist rows")

    selected_parts: list[pd.DataFrame] = []
    pool_summary: dict[str, dict[str, int]] = {}
    for taxon in TAXA:
        part = work[work["focal_taxon"].eq(taxon)].copy()
        observations = sorted(part["source_observation_id"].unique(), key=numeric_key)
        observations = observations[: args.max_observations_per_taxon]
        part = part[part["source_observation_id"].isin(observations)].copy()
        part["_photo_key"] = part["source_photo_id"].map(numeric_key)
        part = part.sort_values(["source_observation_id", "_photo_key"], key=None)
        part = part.groupby("source_observation_id", sort=False, as_index=False, group_keys=False).head(
            args.max_photos_per_observation
        )
        selected_parts.append(part.drop(columns=["_photo_key"]))
        pool_summary[taxon] = {
            "available_observations": int(work[work["focal_taxon"].eq(taxon)]["source_observation_id"].nunique()),
            "candidate_observations": int(part["source_observation_id"].nunique()),
            "candidate_photos": int(len(part)),
        }

    selected = pd.concat(selected_parts, ignore_index=True)
    out = args.out_dir
    images = out / "images"
    images.mkdir(parents=True, exist_ok=True)
    s = session()
    rows: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []

    for i, record in enumerate(selected.to_dict("records"), start=1):
        taxon = str(record["focal_taxon"])
        obs = str(record["source_observation_id"])
        photo = str(record["source_photo_id"])
        name = f"{safe_slug(taxon)}__obs_{safe_slug(obs)}__photo_{safe_slug(photo)}.jpg"
        path = images / name
        try:
            response = s.get(str(record["photo_url"]), timeout=(15, args.timeout_sec))
            response.raise_for_status()
            payload = response.content
            if len(payload) < 2000:
                raise RuntimeError(f"download too small: {len(payload)} bytes")
            path.write_bytes(payload)
            sha = hashlib.sha256(payload).hexdigest()
            unit = f"{safe_slug(taxon)}__obs_{safe_slug(obs)}__photo_{safe_slug(photo)}"
            rows.append({
                "annotation_unit_id": unit,
                "crop_path": name,
                "context_crop_path": name,
                "obs_id": obs,
                "taxon_name": taxon,
                "system_id": record["system_id"],
                "colour_state": record["colour_state"],
                "pair_role": record["pair_role"],
                "photo_id": photo,
                "observer_id": record["observer_id"],
                "observed_on": record["observed_on"],
                "latitude": record["latitude"],
                "longitude": record["longitude"],
                "photo_license": record["photo_license"],
                "source_url": record["photo_url"],
                "image_sha256": sha,
            })
        except Exception as exc:
            failures.append({"taxon": taxon, "obs_id": obs, "photo_id": photo, "error": f"{type(exc).__name__}:{exc}"})
        if i % 25 == 0:
            print(f"[INFO] downloaded {i}/{len(selected)} candidate photos; success={len(rows)}")
        time.sleep(0.03)

    manifest = pd.DataFrame(rows)
    if manifest.empty:
        raise RuntimeError("no public images downloaded")
    manifest = manifest.drop_duplicates("annotation_unit_id", keep="first")
    if manifest["annotation_unit_id"].duplicated().any():
        raise RuntimeError("annotation_unit_id remains duplicated after exact photo deduplication")
    manifest = manifest.sort_values(["taxon_name", "obs_id", "photo_id"]).reset_index(drop=True)
    manifest.to_csv(out / "chapter2_four_taxon_measurement_candidate_manifest_v1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(failures).to_csv(out / "chapter2_four_taxon_measurement_download_failures_v1.csv", index=False, encoding="utf-8-sig")

    report = {
        "contract_version": "chapter2_four_taxon_public_image_measurement_pilot_v1",
        "source": "iNaturalist only from the frozen four-taxon coverage audit",
        "selection_before_image_measurement": {
            "max_observations_per_taxon": args.max_observations_per_taxon,
            "max_photos_per_observation": args.max_photos_per_observation,
            "observation_order": "deterministic ascending source observation id",
            "photo_order": "deterministic ascending source photo id",
            "exact_photo_deduplication": "focal_taxon + source_observation_id + source_photo_id before selection",
            "trait_values_used_for_selection": False,
        },
        "pool_summary": pool_summary,
        "downloaded_photos": int(len(manifest)),
        "download_failures": int(len(failures)),
        "claim_boundary": [
            "candidate photos are public-platform convenience samples, not independent evolutionary replicates",
            "raw images remain ephemeral workflow inputs and are not redistributed by the analysis artifact",
            "phenotype values are not used to choose candidate observations or candidate photos",
        ],
    }
    (out / "chapter2_four_taxon_measurement_preparation_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
