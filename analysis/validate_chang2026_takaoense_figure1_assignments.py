#!/usr/bin/env python3
"""Validate direct Figure 1 morph assignments for six var. takaoense tips.

The frozen table was transcribed from the official Springer Nature Figure 1 PNG.
Every assignment must be printed concordantly in both the Neighbor-Net panel (B)
and species-delimitation tree panel (C), match the exact voucher/run/BioSample
identity, and retain the official image and Actions artifact provenance.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping, Sequence

DEFAULT_INPUT = Path(
    "data/evidence/chang2026_takaoense_figure1_morph_assignments_2026-08-11.csv"
)
DEFAULT_SUMMARY = Path(
    "data/evidence/generated/chang2026_takaoense_figure1_assignment_summary.json"
)

REQUIRED_FIELDS = (
    "accepted_taxon",
    "code",
    "location",
    "voucher",
    "run",
    "biosample",
    "figure1_panel_b_label",
    "figure1_panel_c_label",
    "direct_figure_label",
    "flower_colour_state",
    "binary_colour_code",
    "source_figure",
    "source_image_sha256",
    "source_image_width_px",
    "source_image_height_px",
    "source_workflow_run",
    "source_artifact_id",
    "source_artifact_sha256",
    "review_method",
    "assignment_confidence",
    "review_status",
    "notes",
)

EXPECTED = {
    "ccy3559": {
        "code": "FC",
        "run": "SRR35152718",
        "biosample": "SAMN50798021",
        "label": "BP",
        "state": "bluish-purple",
        "binary": "C",
    },
    "ccy3560": {
        "code": "WY",
        "run": "SRR35152717",
        "biosample": "SAMN50798022",
        "label": "W",
        "state": "white",
        "binary": "W",
    },
    "ccy3629": {
        "code": "FB",
        "run": "SRR35152738",
        "biosample": "SAMN50798024",
        "label": "W",
        "state": "white",
        "binary": "W",
    },
    "ccy3807": {
        "code": "TJ",
        "run": "SRR35152736",
        "biosample": "SAMN50798026",
        "label": "BP",
        "state": "bluish-purple",
        "binary": "C",
    },
    "ccy3835": {
        "code": "NH",
        "run": "SRR35152735",
        "biosample": "SAMN50798027",
        "label": "BP",
        "state": "bluish-purple",
        "binary": "C",
    },
    "ccy3839": {
        "code": "LT",
        "run": "SRR35152734",
        "biosample": "SAMN50798028",
        "label": "W",
        "state": "white",
        "binary": "W",
    },
}

IMAGE_SHA256 = "10375f1d79a4799babdebffca84301f602adfa0aabc825b852de84177bbb878c"
ARTIFACT_SHA256 = "6d5f8f4e1e059122629acce751adb8eb57cd3e5fa95ff9dfa92fcc72bb4ea68f"
WORKFLOW_RUN = "31429139819"
ARTIFACT_ID = "9078372622"
WIDTH = "1945"
HEIGHT = "2400"
REVIEW_METHOD = "manual_direct_visual_transcription_crosschecked_between_panels_B_and_C"
REVIEW_STATUS = "assigned_from_direct_figure1_tip_labels"


def clean(value: object) -> str:
    return str(value or "").strip()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"{path}: missing header")
        missing = set(REQUIRED_FIELDS) - set(reader.fieldnames)
        extra = set(reader.fieldnames) - set(REQUIRED_FIELDS)
        if missing or extra:
            raise ValueError(
                f"{path}: schema mismatch missing={sorted(missing)} extra={sorted(extra)}"
            )
        rows = []
        for index, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"{path}:{index}: too many fields: {row[None]!r}")
            cleaned = {key: clean(value) for key, value in row.items()}
            if any(cleaned.values()):
                rows.append(cleaned)
        return rows


def expected_printed_label(row: Mapping[str, str], panel: str) -> str:
    prefix = "var. takaoense" if panel == "B" else "C. japonicum var. takaoense"
    numeric = row["voucher"].removeprefix("ccy")
    return f"{prefix}_{row['code']}-{numeric}({row['direct_figure_label']})"


def validate(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    if len(rows) != 6:
        raise ValueError(f"Expected six Figure 1 assignment rows, observed {len(rows)}")
    by_voucher = {row["voucher"]: row for row in rows}
    if len(by_voucher) != 6 or set(by_voucher) != set(EXPECTED):
        raise ValueError(f"Voucher membership changed: {sorted(by_voucher)}")

    panel_concordant: list[str] = []
    for voucher, expected in EXPECTED.items():
        row = by_voucher[voucher]
        if row["accepted_taxon"] != "Cirsium japonicum var. takaoense":
            raise ValueError(f"{voucher}: accepted taxon changed")
        for key in ("code", "run", "biosample"):
            if row[key] != expected[key]:
                raise ValueError(
                    f"{voucher}: {key} expected={expected[key]!r} observed={row[key]!r}"
                )
        observed_state = (
            row["direct_figure_label"],
            row["flower_colour_state"],
            row["binary_colour_code"],
        )
        expected_state = (expected["label"], expected["state"], expected["binary"])
        if observed_state != expected_state:
            raise ValueError(
                f"{voucher}: morph expected={expected_state!r} observed={observed_state!r}"
            )

        expected_b = expected_printed_label(row, "B")
        expected_c = expected_printed_label(row, "C")
        if row["figure1_panel_b_label"] != expected_b:
            raise ValueError(f"{voucher}: Panel B label mismatch")
        if row["figure1_panel_c_label"] != expected_c:
            raise ValueError(f"{voucher}: Panel C label mismatch")
        panel_concordant.append(voucher)

        if row["source_figure"] != "Chang et al. 2026 Figure 1 panels B and C":
            raise ValueError(f"{voucher}: source figure changed")
        if row["source_image_sha256"] != IMAGE_SHA256:
            raise ValueError(f"{voucher}: official image hash changed")
        if (row["source_image_width_px"], row["source_image_height_px"]) != (
            WIDTH,
            HEIGHT,
        ):
            raise ValueError(f"{voucher}: image dimensions changed")
        if row["source_workflow_run"] != WORKFLOW_RUN:
            raise ValueError(f"{voucher}: workflow provenance changed")
        if row["source_artifact_id"] != ARTIFACT_ID:
            raise ValueError(f"{voucher}: artifact ID changed")
        if row["source_artifact_sha256"] != ARTIFACT_SHA256:
            raise ValueError(f"{voucher}: artifact digest changed")
        if row["review_method"] != REVIEW_METHOD:
            raise ValueError(f"{voucher}: review method changed")
        if row["assignment_confidence"] != "high":
            raise ValueError(f"{voucher}: assignment confidence changed")
        if row["review_status"] != REVIEW_STATUS:
            raise ValueError(f"{voucher}: review status changed")
        if "No inference from locality or topology" not in row["notes"]:
            raise ValueError(f"{voucher}: no-inference guard is missing")

    white = sorted(voucher for voucher, item in EXPECTED.items() if item["label"] == "W")
    bp = sorted(voucher for voucher, item in EXPECTED.items() if item["label"] == "BP")
    return {
        "accepted_taxon": "Cirsium japonicum var. takaoense",
        "assignment_rows": 6,
        "panel_b_direct_labels": 6,
        "panel_c_direct_labels": 6,
        "panel_b_c_concordant_vouchers": sorted(panel_concordant),
        "white_vouchers": white,
        "bluish_purple_vouchers": bp,
        "morph_counts": {"W": len(white), "BP": len(bp)},
        "source_image_sha256": IMAGE_SHA256,
        "source_image_dimensions_px": [int(WIDTH), int(HEIGHT)],
        "workflow_run": int(WORKFLOW_RUN),
        "artifact_id": int(ARTIFACT_ID),
        "artifact_sha256": ARTIFACT_SHA256,
        "direct_morph_assignment_complete": True,
        "interpretation": (
            "All six published var. takaoense transcriptomes have direct, concordant "
            "W/BP labels in Figure 1 panels B and C: FC/TJ/NH are BP; WY/FB/LT are W."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = validate(read_rows(args.input))
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"assignment_rows={summary['assignment_rows']}")
    print(f"panel_b_direct_labels={summary['panel_b_direct_labels']}")
    print(f"panel_c_direct_labels={summary['panel_c_direct_labels']}")
    print("white_vouchers=" + "|".join(summary["white_vouchers"]))
    print("bluish_purple_vouchers=" + "|".join(summary["bluish_purple_vouchers"]))
    print(f"source_image_sha256={summary['source_image_sha256']}")
    print(args.summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
