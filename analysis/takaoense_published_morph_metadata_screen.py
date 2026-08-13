#!/usr/bin/env python3
"""Screen metadata patterns in the six published var. takaoense morph-labelled tips.

Chang et al. (2026) Figure 1 directly labels three transcriptome tips as white
(W) and three as bluish-purple (BP).  The purpose of this script is deliberately
narrow:

* join those direct figure labels to the already audited voucher, SRA and
  BioSample metadata;
* quantify the altitude pattern in the six published samples with an exact
  label-permutation calculation;
* expose leave-one-sample-out sensitivity;
* produce a reusable morph-linked public-sample manifest.

This is a hypothesis-generating metadata screen, not a test of environmental
selection.  The samples were not randomly drawn for an altitude experiment,
there is one plant per locality, altitude is spatially confounded, and the leaf
transcriptomes do not measure floral anthocyanin expression.
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import re
import statistics
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DEFAULT_ASSIGNMENTS = Path(
    "data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv"
)
DEFAULT_METADATA = Path(
    "data/evidence/chang2026_takaoense_ncbi_voucher_morph_audit_2026-08-11.csv"
)
DEFAULT_SAMPLE_OUTPUT = Path(
    "data/evidence/chang2026_takaoense_morph_linked_public_samples_v1.csv"
)
DEFAULT_METRIC_OUTPUT = Path(
    "analysis/takaoense_published_morph_altitude_screen.csv"
)
DEFAULT_PERMUTATION_OUTPUT = Path(
    "analysis/takaoense_published_morph_altitude_permutations.csv"
)
DEFAULT_LOO_OUTPUT = Path(
    "analysis/takaoense_published_morph_altitude_leave_one_out.csv"
)
DEFAULT_SUMMARY_OUTPUT = Path(
    "analysis/takaoense_published_morph_metadata_screen_summary.json"
)

EXPECTED_VOUCHERS = {
    "ccy3559",
    "ccy3560",
    "ccy3629",
    "ccy3807",
    "ccy3835",
    "ccy3839",
}
EXPECTED_MORPH_COUNTS = {"W": 3, "BP": 3}

SAMPLE_FIELDS = (
    "accepted_taxon",
    "code",
    "voucher",
    "published_figure_label",
    "flower_colour_state",
    "binary_colour_code",
    "location",
    "coordinate",
    "latitude_decimal",
    "longitude_decimal",
    "altitude_m",
    "run",
    "experiment",
    "biosample",
    "sample_name",
    "biosample_isolate",
    "herbarium_supplement_s1",
    "figure1_panel_b_label",
    "figure1_panel_c_label",
    "figure1_image_sha256",
    "evidence_status",
    "analysis_role",
    "limitations",
)

METRIC_FIELDS = (
    "metric",
    "value",
    "unit",
    "interpretation",
)

PERMUTATION_FIELDS = (
    "allocation_index",
    "bp_vouchers",
    "w_vouchers",
    "mean_altitude_bp_m",
    "mean_altitude_w_m",
    "difference_bp_minus_w_m",
    "at_least_observed_one_sided",
    "at_least_observed_absolute",
)

LOO_FIELDS = (
    "removed_voucher",
    "removed_code",
    "removed_morph",
    "removed_altitude_m",
    "remaining_n_bp",
    "remaining_n_w",
    "mean_altitude_bp_m",
    "mean_altitude_w_m",
    "difference_bp_minus_w_m",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing CSV header")
        return [
            {key: clean(value) for key, value in row.items()}
            for row in reader
            if any(clean(value) for value in row.values())
        ]


def write_csv(
    path: Path,
    rows: Iterable[Mapping[str, object]],
    fields: Sequence[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def unique_index(
    rows: Sequence[Mapping[str, str]],
    field: str,
    source: Path,
) -> dict[str, Mapping[str, str]]:
    output: dict[str, Mapping[str, str]] = {}
    for row in rows:
        key = clean(row.get(field))
        if not key:
            raise ValueError(f"{source}: empty {field}")
        if key in output:
            raise ValueError(f"{source}: duplicate {field}={key}")
        output[key] = row
    return output


def dms_to_decimal(value: str) -> tuple[float, float]:
    """Parse coordinates such as ``23°30'N, 120°41'E``."""
    pattern = re.compile(
        r"(\d+(?:\.\d+)?)°\s*(\d+(?:\.\d+)?)'\s*([NS])"
        r"\s*,?\s*"
        r"(\d+(?:\.\d+)?)°\s*(\d+(?:\.\d+)?)'\s*([EW])",
        flags=re.IGNORECASE,
    )
    match = pattern.search(clean(value))
    if not match:
        raise ValueError(f"Unrecognized coordinate: {value!r}")
    lat_deg, lat_min, lat_hemi, lon_deg, lon_min, lon_hemi = match.groups()
    latitude = float(lat_deg) + float(lat_min) / 60.0
    longitude = float(lon_deg) + float(lon_min) / 60.0
    if lat_hemi.upper() == "S":
        latitude *= -1
    if lon_hemi.upper() == "W":
        longitude *= -1
    return latitude, longitude


def join_samples(
    assignments: Sequence[Mapping[str, str]],
    metadata: Sequence[Mapping[str, str]],
) -> list[dict[str, object]]:
    assignment_index = unique_index(assignments, "voucher", DEFAULT_ASSIGNMENTS)
    metadata_index = unique_index(metadata, "voucher", DEFAULT_METADATA)
    if set(assignment_index) != EXPECTED_VOUCHERS:
        raise ValueError(
            f"Figure assignments changed: {sorted(assignment_index)}"
        )
    if not EXPECTED_VOUCHERS.issubset(metadata_index):
        missing = sorted(EXPECTED_VOUCHERS - set(metadata_index))
        raise ValueError(f"Metadata missing published vouchers: {missing}")

    output: list[dict[str, object]] = []
    morph_counts = {"W": 0, "BP": 0}
    for voucher in sorted(EXPECTED_VOUCHERS):
        figure = assignment_index[voucher]
        source = metadata_index[voucher]
        label = clean(figure.get("direct_figure_label"))
        if label not in morph_counts:
            raise ValueError(f"{voucher}: invalid direct Figure 1 label {label!r}")
        morph_counts[label] += 1

        for field, figure_field, metadata_field in (
            ("code", "code", "code"),
            ("run", "run", "run"),
            ("biosample", "biosample", "biosample"),
        ):
            if clean(figure.get(figure_field)) != clean(source.get(metadata_field)):
                raise ValueError(
                    f"{voucher}: {field} mismatch between Figure and NCBI audits"
                )

        latitude, longitude = dms_to_decimal(source["coordinate"])
        altitude = float(source["altitude_m"])
        if not math.isfinite(altitude):
            raise ValueError(f"{voucher}: non-finite altitude")
        output.append(
            {
                "accepted_taxon": figure["accepted_taxon"],
                "code": figure["code"],
                "voucher": voucher,
                "published_figure_label": label,
                "flower_colour_state": figure["flower_colour_state"],
                "binary_colour_code": figure["binary_colour_code"],
                "location": source["location"],
                "coordinate": source["coordinate"],
                "latitude_decimal": f"{latitude:.6f}",
                "longitude_decimal": f"{longitude:.6f}",
                "altitude_m": f"{altitude:.0f}",
                "run": source["run"],
                "experiment": source["experiment"],
                "biosample": source["biosample"],
                "sample_name": source["sample_name"],
                "biosample_isolate": source["biosample_isolate"],
                "herbarium_supplement_s1": source["herbarium_supplement_s1"],
                "figure1_panel_b_label": figure["figure1_panel_b_label"],
                "figure1_panel_c_label": figure["figure1_panel_c_label"],
                "figure1_image_sha256": figure["source_image_sha256"],
                "evidence_status": "morph_and_public_accession_directly_linked",
                "analysis_role": (
                    "morph-labelled young-leaf transcriptome anchor for ancestry, "
                    "topology and candidate coding-variation screens"
                ),
                "limitations": (
                    "one plant per locality; non-random sampling; young-leaf RNA; "
                    "not a floral expression replicate"
                ),
            }
        )
    if morph_counts != EXPECTED_MORPH_COUNTS:
        raise ValueError(f"Unexpected morph counts: {morph_counts}")
    return sorted(output, key=lambda row: str(row["code"]))


def mean_altitude(rows: Sequence[Mapping[str, object]], label: str) -> float:
    values = [
        float(row["altitude_m"])
        for row in rows
        if row["published_figure_label"] == label
    ]
    if not values:
        raise ValueError(f"No altitude values for morph {label}")
    return statistics.mean(values)


def median_altitude(rows: Sequence[Mapping[str, object]], label: str) -> float:
    values = [
        float(row["altitude_m"])
        for row in rows
        if row["published_figure_label"] == label
    ]
    return statistics.median(values)


def enumerate_permutations(
    rows: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], float, float, float]:
    n_bp = sum(row["published_figure_label"] == "BP" for row in rows)
    if n_bp != 3 or len(rows) != 6:
        raise ValueError("Exact screen currently expects three BP and three W samples")
    observed = mean_altitude(rows, "BP") - mean_altitude(rows, "W")
    output: list[dict[str, object]] = []
    tolerance = 1e-12
    for index, bp_indices in enumerate(itertools.combinations(range(len(rows)), n_bp), start=1):
        bp_set = set(bp_indices)
        bp_rows = [rows[i] for i in range(len(rows)) if i in bp_set]
        w_rows = [rows[i] for i in range(len(rows)) if i not in bp_set]
        mean_bp = statistics.mean(float(row["altitude_m"]) for row in bp_rows)
        mean_w = statistics.mean(float(row["altitude_m"]) for row in w_rows)
        difference = mean_bp - mean_w
        output.append(
            {
                "allocation_index": index,
                "bp_vouchers": "|".join(sorted(str(row["voucher"]) for row in bp_rows)),
                "w_vouchers": "|".join(sorted(str(row["voucher"]) for row in w_rows)),
                "mean_altitude_bp_m": f"{mean_bp:.6f}",
                "mean_altitude_w_m": f"{mean_w:.6f}",
                "difference_bp_minus_w_m": f"{difference:.6f}",
                "at_least_observed_one_sided": (
                    "yes" if difference >= observed - tolerance else "no"
                ),
                "at_least_observed_absolute": (
                    "yes" if abs(difference) >= abs(observed) - tolerance else "no"
                ),
            }
        )
    one_sided = sum(
        row["at_least_observed_one_sided"] == "yes" for row in output
    ) / len(output)
    two_sided = sum(
        row["at_least_observed_absolute"] == "yes" for row in output
    ) / len(output)
    return output, observed, one_sided, two_sided


def leave_one_out(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for index, removed in enumerate(rows):
        retained = [row for i, row in enumerate(rows) if i != index]
        n_bp = sum(row["published_figure_label"] == "BP" for row in retained)
        n_w = sum(row["published_figure_label"] == "W" for row in retained)
        mean_bp = mean_altitude(retained, "BP")
        mean_w = mean_altitude(retained, "W")
        output.append(
            {
                "removed_voucher": removed["voucher"],
                "removed_code": removed["code"],
                "removed_morph": removed["published_figure_label"],
                "removed_altitude_m": removed["altitude_m"],
                "remaining_n_bp": n_bp,
                "remaining_n_w": n_w,
                "mean_altitude_bp_m": f"{mean_bp:.6f}",
                "mean_altitude_w_m": f"{mean_w:.6f}",
                "difference_bp_minus_w_m": f"{mean_bp - mean_w:.6f}",
            }
        )
    return output


def metric_rows(
    rows: Sequence[Mapping[str, object]],
    observed: float,
    one_sided: float,
    two_sided: float,
    permutations: Sequence[Mapping[str, object]],
    loo: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    bp_values = [
        float(row["altitude_m"])
        for row in rows
        if row["published_figure_label"] == "BP"
    ]
    w_values = [
        float(row["altitude_m"])
        for row in rows
        if row["published_figure_label"] == "W"
    ]
    loo_differences = [float(row["difference_bp_minus_w_m"]) for row in loo]
    complete_separation = min(bp_values) > max(w_values)
    return [
        {
            "metric": "n_published_samples",
            "value": str(len(rows)),
            "unit": "samples",
            "interpretation": "one morph-labelled young-leaf transcriptome per locality",
        },
        {
            "metric": "n_white",
            "value": str(len(w_values)),
            "unit": "samples",
            "interpretation": "WY-3560, FB-3629 and LT-3839",
        },
        {
            "metric": "n_bluish_purple",
            "value": str(len(bp_values)),
            "unit": "samples",
            "interpretation": "FC-3559, TJ-3807 and NH-3835",
        },
        {
            "metric": "mean_altitude_bluish_purple",
            "value": f"{statistics.mean(bp_values):.6f}",
            "unit": "m",
            "interpretation": "descriptive mean of the three published BP samples",
        },
        {
            "metric": "mean_altitude_white",
            "value": f"{statistics.mean(w_values):.6f}",
            "unit": "m",
            "interpretation": "descriptive mean of the three published W samples",
        },
        {
            "metric": "mean_difference_bp_minus_w",
            "value": f"{observed:.6f}",
            "unit": "m",
            "interpretation": "hypothesis-generating; altitude is spatially confounded",
        },
        {
            "metric": "median_altitude_bluish_purple",
            "value": f"{median_altitude(rows, 'BP'):.6f}",
            "unit": "m",
            "interpretation": "descriptive median",
        },
        {
            "metric": "median_altitude_white",
            "value": f"{median_altitude(rows, 'W'):.6f}",
            "unit": "m",
            "interpretation": "descriptive median",
        },
        {
            "metric": "complete_rank_separation",
            "value": "yes" if complete_separation else "no",
            "unit": "boolean",
            "interpretation": "minimum BP altitude exceeds maximum W altitude in these six samples",
        },
        {
            "metric": "exact_label_allocations",
            "value": str(len(permutations)),
            "unit": "allocations",
            "interpretation": "all choose(6,3)=20 allocations enumerated",
        },
        {
            "metric": "exact_one_sided_p",
            "value": f"{one_sided:.6f}",
            "unit": "probability",
            "interpretation": "descriptive label-permutation tail for BP higher than W",
        },
        {
            "metric": "exact_two_sided_p",
            "value": f"{two_sided:.6f}",
            "unit": "probability",
            "interpretation": "descriptive absolute-difference label-permutation tail",
        },
        {
            "metric": "leave_one_out_difference_min",
            "value": f"{min(loo_differences):.6f}",
            "unit": "m",
            "interpretation": "smallest BP-minus-W mean difference after deleting one sample",
        },
        {
            "metric": "leave_one_out_difference_max",
            "value": f"{max(loo_differences):.6f}",
            "unit": "m",
            "interpretation": "largest BP-minus-W mean difference after deleting one sample",
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--assignments", type=Path, default=DEFAULT_ASSIGNMENTS)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA)
    parser.add_argument("--sample-output", type=Path, default=DEFAULT_SAMPLE_OUTPUT)
    parser.add_argument("--metric-output", type=Path, default=DEFAULT_METRIC_OUTPUT)
    parser.add_argument(
        "--permutation-output", type=Path, default=DEFAULT_PERMUTATION_OUTPUT
    )
    parser.add_argument("--loo-output", type=Path, default=DEFAULT_LOO_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    joined = join_samples(read_csv(args.assignments), read_csv(args.metadata))
    permutations, observed, one_sided, two_sided = enumerate_permutations(joined)
    loo = leave_one_out(joined)
    metrics = metric_rows(
        joined, observed, one_sided, two_sided, permutations, loo
    )

    write_csv(args.sample_output, joined, SAMPLE_FIELDS)
    write_csv(args.metric_output, metrics, METRIC_FIELDS)
    write_csv(args.permutation_output, permutations, PERMUTATION_FIELDS)
    write_csv(args.loo_output, loo, LOO_FIELDS)

    summary = {
        "accepted_taxon": "Cirsium japonicum var. takaoense",
        "published_samples": len(joined),
        "morph_counts": {"W": 3, "BP": 3},
        "white_vouchers": sorted(
            row["voucher"]
            for row in joined
            if row["published_figure_label"] == "W"
        ),
        "bluish_purple_vouchers": sorted(
            row["voucher"]
            for row in joined
            if row["published_figure_label"] == "BP"
        ),
        "mean_altitude_bp_m": mean_altitude(joined, "BP"),
        "mean_altitude_w_m": mean_altitude(joined, "W"),
        "mean_difference_bp_minus_w_m": observed,
        "complete_rank_separation": (
            min(float(row["altitude_m"]) for row in joined if row["published_figure_label"] == "BP")
            > max(float(row["altitude_m"]) for row in joined if row["published_figure_label"] == "W")
        ),
        "exact_allocation_count": len(permutations),
        "exact_one_sided_p": one_sided,
        "exact_two_sided_p": two_sided,
        "leave_one_out_difference_range_m": [
            min(float(row["difference_bp_minus_w_m"]) for row in loo),
            max(float(row["difference_bp_minus_w_m"]) for row in loo),
        ],
        "allowed_inference": (
            "The six published samples show a strong altitude-stratified morph pattern "
            "that should guide balanced field sampling and ancestry analyses."
        ),
        "prohibited_inference": (
            "These six non-random localities do not establish altitude-dependent selection, "
            "causality, a reaction norm, or the direction of flower-colour evolution."
        ),
        "transcriptome_scope": (
            "Young-leaf RNA-seq can support ancestry, topology and candidate coding-variation "
            "screens, but cannot establish floral anthocyanin expression or regulatory reactivation."
        ),
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"published_samples={summary['published_samples']}")
    print(f"mean_altitude_bp_m={summary['mean_altitude_bp_m']:.6f}")
    print(f"mean_altitude_w_m={summary['mean_altitude_w_m']:.6f}")
    print(
        "mean_difference_bp_minus_w_m="
        f"{summary['mean_difference_bp_minus_w_m']:.6f}"
    )
    print(f"complete_rank_separation={summary['complete_rank_separation']}")
    print(f"exact_one_sided_p={summary['exact_one_sided_p']:.6f}")
    print(f"exact_two_sided_p={summary['exact_two_sided_p']:.6f}")
    print(args.summary_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
