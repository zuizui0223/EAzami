#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--image-root", required=True, type=Path)
    p.add_argument("--azami-primary-script", required=True, type=Path)
    p.add_argument("--out-dir", required=True, type=Path)
    p.add_argument("--min-crop-dimension", type=int, default=300)
    return p.parse_args()


def load_azami(path: Path):
    spec = importlib.util.spec_from_file_location("azami_primary_measurement", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load Azami measurement script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "central_foreground"):
        raise RuntimeError("pinned Azami script does not expose central_foreground")
    return module


def centre_crop(image: np.ndarray, fraction: float) -> np.ndarray:
    height, width = image.shape[:2]
    crop_h = max(1, int(round(height * fraction)))
    crop_w = max(1, int(round(width * fraction)))
    y0 = max(0, (height - crop_h) // 2)
    x0 = max(0, (width - crop_w) // 2)
    return image[y0:y0 + crop_h, x0:x0 + crop_w].copy()


def expanded_bbox_crop(image: np.ndarray, mask: np.ndarray, expansion: float = 0.18) -> np.ndarray | None:
    rows, cols = np.nonzero(mask)
    if len(rows) < 50:
        return None
    y0, y1 = int(rows.min()), int(rows.max()) + 1
    x0, x1 = int(cols.min()), int(cols.max()) + 1
    height = y1 - y0
    width = x1 - x0
    pad_y = int(round(height * expansion))
    pad_x = int(round(width * expansion))
    y0 = max(0, y0 - pad_y)
    x0 = max(0, x0 - pad_x)
    y1 = min(image.shape[0], y1 + pad_y)
    x1 = min(image.shape[1], x1 + pad_x)
    if y1 <= y0 or x1 <= x0:
        return None
    return image[y0:y1, x0:x1].copy()


def sharpness(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def candidate_record(label: str, image: np.ndarray, azami, min_dim: int) -> dict[str, object]:
    mask, quality = azami.central_foreground(image)
    dimension = int(min(image.shape[:2]))
    sharp = sharpness(image)
    valid = bool(
        dimension >= min_dim
        and np.isfinite(float(quality.get("mask_quality", np.nan)))
        and mask is not None
        and int(np.count_nonzero(mask)) >= 50
    )
    return {
        "label": label,
        "image": image,
        "mask": mask,
        "valid": valid,
        "min_dimension": dimension,
        "sharpness": sharp,
        "mask_quality": float(quality.get("mask_quality", np.nan)),
        "foreground_area_fraction": float(quality.get("foreground_area_fraction", np.nan)),
        "foreground_border_fraction": float(quality.get("foreground_border_fraction", np.nan)),
    }


def choose_candidate(candidates: list[dict[str, object]]) -> dict[str, object]:
    valid = [c for c in candidates if bool(c["valid"])]
    if not valid:
        valid = candidates
    # Lexicographic, trait-neutral choice. The frozen Azami foreground quality is
    # the primary criterion; sharpness and size only break close ties. No floral
    # colour, shape endpoint, known white/coloured state or environment is used.
    return max(
        valid,
        key=lambda c: (
            round(float(c["mask_quality"]), 4) if np.isfinite(float(c["mask_quality"])) else -1.0,
            round(math.log1p(max(float(c["sharpness"]), 0.0)), 4),
            int(c["min_dimension"]),
            str(c["label"]),
        ),
    )


def main() -> int:
    args = parse_args()
    azami = load_azami(args.azami_primary_script)
    manifest = pd.read_csv(args.manifest, dtype=str, keep_default_na=False)
    required = {"annotation_unit_id", "crop_path", "context_crop_path", "obs_id", "taxon_name"}
    missing = sorted(required.difference(manifest.columns))
    if missing:
        raise ValueError(f"manifest missing columns: {missing}")
    if manifest["annotation_unit_id"].duplicated().any():
        raise ValueError("annotation_unit_id must be unique before cropping")

    out = args.out_dir
    image_out = out / "images"
    image_out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    diagnostic_rows: list[dict[str, object]] = []

    for i, record in enumerate(manifest.to_dict("records"), start=1):
        source_path = args.image_root / str(record["crop_path"])
        image = cv2.imread(str(source_path), cv2.IMREAD_COLOR)
        if image is None:
            continue

        candidates: list[dict[str, object]] = []
        for fraction in (1.00, 0.85, 0.70, 0.55):
            crop = centre_crop(image, fraction)
            candidates.append(candidate_record(f"center_{fraction:.2f}", crop, azami, args.min_crop_dimension))

        # Add foreground bounding-box candidates without using any trait output.
        for seed in list(candidates[:3]):
            mask = seed["mask"]
            seed_image = seed["image"]
            if isinstance(mask, np.ndarray) and isinstance(seed_image, np.ndarray):
                bbox = expanded_bbox_crop(seed_image, mask, expansion=0.18)
                if bbox is not None:
                    candidates.append(
                        candidate_record(
                            f"bbox18_from_{seed['label']}", bbox, azami, args.min_crop_dimension
                        )
                    )

        chosen = choose_candidate(candidates)
        unit = str(record["annotation_unit_id"])
        head_name = f"head__{unit}.jpg"
        context_name = f"context__{unit}.jpg"
        cv2.imwrite(str(image_out / head_name), chosen["image"], [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        shutil.copyfile(source_path, image_out / context_name)

        row = dict(record)
        row["crop_path"] = head_name
        row["context_crop_path"] = context_name
        row["neutral_crop_label"] = chosen["label"]
        row["neutral_crop_mask_quality"] = chosen["mask_quality"]
        row["neutral_crop_sharpness"] = chosen["sharpness"]
        row["neutral_crop_min_dimension"] = chosen["min_dimension"]
        row["neutral_crop_foreground_area_fraction"] = chosen["foreground_area_fraction"]
        row["neutral_crop_foreground_border_fraction"] = chosen["foreground_border_fraction"]
        rows.append(row)

        for candidate in candidates:
            diagnostic_rows.append({
                "annotation_unit_id": unit,
                "taxon_name": record["taxon_name"],
                "candidate_label": candidate["label"],
                "selected": candidate is chosen,
                "valid_min_dimension": candidate["valid"],
                "min_dimension": candidate["min_dimension"],
                "sharpness": candidate["sharpness"],
                "mask_quality": candidate["mask_quality"],
                "foreground_area_fraction": candidate["foreground_area_fraction"],
                "foreground_border_fraction": candidate["foreground_border_fraction"],
            })
        if i % 50 == 0:
            print(f"[INFO] neutral-cropped {i}/{len(manifest)} images")

    result = pd.DataFrame(rows)
    if result.empty or result["annotation_unit_id"].duplicated().any():
        raise RuntimeError("trait-neutral crop manifest is empty or non-unique")
    result.to_csv(out / "chapter2_four_taxon_trait_neutral_crop_manifest_v1.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(diagnostic_rows).to_csv(out / "chapter2_four_taxon_trait_neutral_crop_diagnostics_v1.csv", index=False, encoding="utf-8-sig")

    report = {
        "contract_version": "chapter2_four_taxon_trait_neutral_head_crop_v1",
        "n_input_images": int(len(manifest)),
        "n_output_images": int(len(result)),
        "candidate_families": [
            "full image",
            "center 85%",
            "center 70%",
            "center 55%",
            "18% expanded Azami-central-foreground bounding boxes from full/85%/70% candidates",
        ],
        "selection": "highest pinned-Azami central_foreground mask_quality; sharpness and minimum dimension as tie-breaks",
        "minimum_crop_dimension": args.min_crop_dimension,
        "trait_values_used_for_crop_selection": False,
        "known_white_coloured_state_used_for_crop_selection": False,
        "environment_used_for_crop_selection": False,
        "claim_boundary": [
            "the crop ensemble improves assessability only and does not validate taxonomic identity",
            "crop selection is independent of measured floral colour and architecture endpoints",
            "raw crop images are ephemeral workflow inputs and are not redistributed in the artifact",
        ],
    }
    (out / "chapter2_four_taxon_trait_neutral_crop_report_v1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
