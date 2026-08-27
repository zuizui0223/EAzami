#!/usr/bin/env python3
"""Screen licensed Japan-local Cirsium yezoense images with the pinned Azami colour algorithm.

Predeclared promotion rule: JPN30 can become the fifth clean Japan-local colour concept
only when at least one image from each of two independent locality/date series passes
the already-frozen Azami colour-confidence floor (0.55). Thresholds are never relaxed
after inspecting results. Locality medians, not raw image replicates, are the concept-level
aggregation unit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import cv2


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_azami_measurement(path: Path):
    spec = importlib.util.spec_from_file_location("azami_primary_measurement", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import Azami measurement module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "colour_measurement"):
        raise RuntimeError("pinned Azami module has no colour_measurement function")
    return module


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def median_abs_deviation(values):
    if not values:
        return None
    med = statistics.median(values)
    return statistics.median(abs(x - med) for x in values)


def truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--image-dir", type=Path, required=True)
    parser.add_argument("--azami-measure-script", type=Path, required=True)
    parser.add_argument("--colour-confidence-floor", type=float, default=0.55)
    parser.add_argument("--per-image-output", type=Path, required=True)
    parser.add_argument("--summary-output", type=Path, required=True)
    args = parser.parse_args()

    rows = [row for row in read_csv(args.registry) if truthy(row.get("automated_use"))]
    if len(rows) != 3:
        raise ValueError(f"expected exactly three automated-use rows, got {len(rows)}")
    if {row["paper_japan_member_id"] for row in rows} != {"JPN_30"}:
        raise ValueError("v1 recovery contract is restricted to JPN_30")
    locality_ids = sorted({row["locality_id"] for row in rows})
    if len(locality_ids) != 2:
        raise ValueError(f"predeclared gate requires exactly two independent locality series, got {locality_ids}")

    azami = load_azami_measurement(args.azami_measure_script)
    out_rows = []
    usable_by_locality = defaultdict(list)
    usable_chroma_by_locality = defaultdict(list)

    for row in rows:
        image_path = args.image_dir / f"{row['source_id']}.jpg"
        if not image_path.exists():
            raise FileNotFoundError(image_path)
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"unreadable downloaded image: {image_path}")
        result = azami.colour_measurement(image)
        state = str(result.get("state", ""))
        confidence = float(result.get("confidence") or 0.0)
        lightness = result.get("median_lab_lightness")
        chroma = result.get("median_lab_chroma")
        lightness = float(lightness) if lightness is not None and math.isfinite(float(lightness)) else None
        chroma = float(chroma) if chroma is not None and math.isfinite(float(chroma)) else None
        usable = (
            state != getattr(azami, "NON_SCOREABLE", "unassessable")
            and confidence >= args.colour_confidence_floor
            and lightness is not None
        )
        if usable:
            usable_by_locality[row["locality_id"]].append(lightness)
            if chroma is not None:
                usable_chroma_by_locality[row["locality_id"]].append(chroma)
        out_rows.append({
            "paper_japan_member_id": row["paper_japan_member_id"],
            "taxon_name": row["taxon_name"],
            "source_id": row["source_id"],
            "locality_id": row["locality_id"],
            "location": row["location"],
            "observation_date": row["observation_date"],
            "source_page_url": row["source_page_url"],
            "author": row["author"],
            "license": row["license"],
            "image_sha256": sha256(image_path),
            "image_width_px": image.shape[1],
            "image_height_px": image.shape[0],
            "measurement_state": state,
            "measurement_confidence": confidence,
            "median_lab_lightness": lightness,
            "median_lab_chroma": chroma,
            "floral_pixel_fraction": result.get("floral_pixel_fraction"),
            "mask_quality": result.get("mask_quality"),
            "usable_at_confidence_floor": usable,
            "measurement_role": row["measurement_role"],
        })

    locality_summaries = []
    for locality_id in locality_ids:
        vals = usable_by_locality.get(locality_id, [])
        cvals = usable_chroma_by_locality.get(locality_id, [])
        locality_summaries.append({
            "locality_id": locality_id,
            "usable_images": len(vals),
            "lightness_median": statistics.median(vals) if vals else None,
            "chroma_median": statistics.median(cvals) if cvals else None,
        })

    usable_localities = [x for x in locality_summaries if x["usable_images"] >= 1]
    promotion = len(usable_localities) == 2
    locality_lightness = [x["lightness_median"] for x in usable_localities]
    locality_chroma = [x["chroma_median"] for x in usable_localities if x["chroma_median"] is not None]

    args.per_image_output.parent.mkdir(parents=True, exist_ok=True)
    with args.per_image_output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(out_rows[0]))
        writer.writeheader()
        writer.writerows(out_rows)

    summary = {
        "contract_version": "japan38_jpn30_public_colour_recovery_v1",
        "paper_japan_member_id": "JPN_30",
        "taxon_name": "Cirsium yezoense",
        "registered_automated_sources": len(rows),
        "downloaded_images_measured": len(out_rows),
        "predeclared_independent_locality_series": 2,
        "colour_confidence_floor": args.colour_confidence_floor,
        "locality_summaries": locality_summaries,
        "usable_locality_series": len(usable_localities),
        "concept_lightness_median_across_locality_medians": statistics.median(locality_lightness) if locality_lightness else None,
        "concept_lightness_mad_across_locality_medians": median_abs_deviation(locality_lightness),
        "concept_chroma_median_across_locality_medians": statistics.median(locality_chroma) if locality_chroma else None,
        "promotion_gate": {
            "japan_local_colour_bridge_ready_from_this_recovery": promotion,
            "rule": "At least one image from each of both predeclared independent locality/date series must pass the frozen confidence floor 0.55.",
            "threshold_relaxation_allowed": False,
        },
        "claim_boundary": "Licensed direct-image recovery only. Promotion, if passed, supplies a fifth identity-resolved Japan-local continuous-colour concept for the next population-matched history pilot; it does not establish a discrete W/C state, ancestral colour, transition direction, adaptation, convergence, or anthocyanin reactivation."
    }
    args.summary_output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
