#!/usr/bin/env python3
"""Measure open iNaturalist candidates for JPN05 and JPN30 with pinned Azami colour code.

Predeclared before image measurement:
- global confidence floor remains 0.55;
- images from one iNaturalist observation are one locality/date series;
- JPN30 already has one passing Aizu series (L*=65.49019622802734); it is
  promoted if >=1 of the new Sendai/Towada series has >=1 usable image;
- JPN05 has no existing passing direct series and is promoted only if both
  Hakodate and Tsugaru series have >=1 usable image;
- concept values are medians across locality medians, never raw image replicates.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import cv2

FLOOR = 0.55
LOCALITY = {
    ("JPN_05", "242578598"): "HAKODATE_20240918",
    ("JPN_05", "322349973"): "TSUGARU_20250820",
    ("JPN_30", "190665296"): "SENDAI_20221005",
    ("JPN_30", "323137995"): "TOWADA_20251018",
}
TAXON = {"JPN_05": "Cirsium aomorense", "JPN_30": "Cirsium yezoense"}
EXISTING = {
    "JPN_05": [],
    "JPN_30": [
        {
            "locality_id": "AIZU_20080927",
            "lightness_median": 65.49019622802734,
            "chroma_median": 47.16990661621094,
            "source": "japan38_jpn30_public_colour_recovery_v1",
        }
    ],
}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h))


def load_measurement(path: Path):
    spec = importlib.util.spec_from_file_location("azami_colour", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "colour_measurement"):
        raise RuntimeError("colour_measurement missing")
    return mod


def med(values):
    return statistics.median(values) if values else None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--candidates", type=Path, required=True)
    p.add_argument("--image-dir", type=Path, required=True)
    p.add_argument("--azami-measure-script", type=Path, required=True)
    p.add_argument("--per-image-output", type=Path, required=True)
    p.add_argument("--summary-output", type=Path, required=True)
    args = p.parse_args()

    rows = [r for r in read_csv(args.candidates) if r["paper_japan_member_id"] in TAXON]
    expected_records = {
        "JPN_05": {"242578598", "322349973"},
        "JPN_30": {"190665296", "323137995"},
    }
    for mid, expected in expected_records.items():
        got = {r["source_record_id"] for r in rows if r["paper_japan_member_id"] == mid}
        if got != expected:
            raise ValueError(f"{mid} candidate records changed: {got} != {expected}")
        for r in [x for x in rows if x["paper_japan_member_id"] == mid]:
            if r["target_taxon_name"] != TAXON[mid] or r["source"] != "iNaturalist" or r["media_license_class"] != "open_reusable":
                raise ValueError(f"candidate contract violation: {r}")

    azami = load_measurement(args.azami_measure_script)
    per_image = []
    by_locality_l = defaultdict(list)
    by_locality_c = defaultdict(list)

    for r in rows:
        mid = r["paper_japan_member_id"]
        obs = r["source_record_id"]
        photo = str(r["media_id"])
        loc = LOCALITY[(mid, obs)]
        path = args.image_dir / f"INAT_{obs}_{photo}.jpg"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            raise ValueError(f"unreadable {path}")
        out = azami.colour_measurement(image)
        state = str(out.get("state", ""))
        conf = float(out.get("confidence") or 0.0)
        light = out.get("median_lab_lightness")
        chroma = out.get("median_lab_chroma")
        light = float(light) if light is not None and math.isfinite(float(light)) else None
        chroma = float(chroma) if chroma is not None and math.isfinite(float(chroma)) else None
        usable = state != getattr(azami, "NON_SCOREABLE", "unassessable") and conf >= FLOOR and light is not None
        if usable:
            by_locality_l[(mid, loc)].append(light)
            if chroma is not None:
                by_locality_c[(mid, loc)].append(chroma)
        per_image.append({
            "paper_japan_member_id": mid,
            "taxon_name": TAXON[mid],
            "source_record_id": obs,
            "media_id": photo,
            "locality_id": loc,
            "record_url": r["record_url"],
            "observed_on": r["observed_on"],
            "place_text": r["place_text"],
            "latitude": r["latitude"],
            "longitude": r["longitude"],
            "media_license": r["media_license"],
            "attribution": r["attribution"],
            "measurement_state": state,
            "measurement_confidence": conf,
            "median_lab_lightness": light,
            "median_lab_chroma": chroma,
            "floral_pixel_fraction": out.get("floral_pixel_fraction"),
            "mask_quality": out.get("mask_quality"),
            "usable_at_frozen_floor": usable,
        })

    summaries = {}
    for mid in ["JPN_05", "JPN_30"]:
        candidate_localities = sorted({LOCALITY[(mid, obs)] for obs in expected_records[mid]})
        locality_rows = []
        for loc in candidate_localities:
            ls = by_locality_l.get((mid, loc), [])
            cs = by_locality_c.get((mid, loc), [])
            locality_rows.append({
                "locality_id": loc,
                "usable_images": len(ls),
                "lightness_median": med(ls),
                "chroma_median": med(cs),
            })
        passing_candidates = [x for x in locality_rows if x["usable_images"] >= 1]
        all_passing = list(EXISTING[mid]) + passing_candidates
        if mid == "JPN_30":
            promotion = len(passing_candidates) >= 1
            rule = "Existing Aizu passing series plus at least one passing Sendai/Towada candidate series."
        else:
            promotion = len(passing_candidates) == 2
            rule = "At least one passing image in each of Hakodate and Tsugaru series."
        lvals = [x["lightness_median"] for x in all_passing if x.get("lightness_median") is not None]
        cvals = [x["chroma_median"] for x in all_passing if x.get("chroma_median") is not None]
        summaries[mid] = {
            "taxon_name": TAXON[mid],
            "candidate_locality_summaries": locality_rows,
            "existing_passing_localities": EXISTING[mid],
            "candidate_passing_locality_count": len(passing_candidates),
            "total_passing_locality_count_if_promoted": len(all_passing),
            "promotion_pass": promotion,
            "promotion_rule": rule,
            "concept_lightness_median_across_locality_medians": med(lvals) if promotion else None,
            "concept_chroma_median_across_locality_medians": med(cvals) if promotion else None,
        }

    result = {
        "contract_version": "japan38_open_candidate_colour_measurement_v1",
        "colour_confidence_floor": FLOOR,
        "threshold_relaxation_allowed": False,
        "results": summaries,
        "fifth_concept_gate_unlocked": bool(summaries["JPN_05"]["promotion_pass"] or summaries["JPN_30"]["promotion_pass"]),
        "promoted_concepts": [mid for mid in ["JPN_05", "JPN_30"] if summaries[mid]["promotion_pass"]],
        "claim_boundary": "Direct licensed live-image quality gate only. Promotion supplies population-local continuous colour proxies for the next history pilot; it does not define W/C states or establish ancestry, adaptation, convergence, transition direction, or anthocyanin reactivation."
    }
    args.per_image_output.parent.mkdir(parents=True, exist_ok=True)
    with args.per_image_output.open("w", encoding="utf-8", newline="") as h:
        writer = csv.DictWriter(h, fieldnames=list(per_image[0]))
        writer.writeheader(); writer.writerows(per_image)
    args.summary_output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
