#!/usr/bin/env python3
"""Build the active JEB package after applying the frozen space-time patch."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from docx import Document

import apply_chapter2_space_time_package_patch_v1 as patcher
import build_chapter2_jeb_docx_v1 as legacy

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"
OUT = CH / "submission_package"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", type=Path, default=OUT)
    return p.parse_args()


def render_sources(tmp: Path) -> tuple[Path, Path]:
    manuscript = tmp / "MANUSCRIPT_JEB_V5.md"
    si = tmp / "JEB_SUPPORTING_INFORMATION_V3.md"
    manuscript.write_text(
        patcher.patch_manuscript((CH / "MANUSCRIPT_JEB_V4.md").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    si.write_text(
        patcher.patch_si((CH / "JEB_SUPPORTING_INFORMATION_V2.md").read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    return manuscript, si


def build_markdown(source: Path, output: Path, *, line_numbers: bool, stop_heading: str | None = None) -> Path:
    doc = Document()
    legacy.configure_document(doc, running_header="", line_numbers=line_numbers)
    legacy.render_markdown(
        doc,
        source,
        skip_metadata_prefixes=(
            "**Target journal:**",
            "**Manuscript status:**",
            "**Running title:**",
            "**Word-limit contract:**",
        ) if "MANUSCRIPT" in source.name else (),
        stop_heading=stop_heading,
    )
    legacy.save_document(doc, output)
    return output


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="chapter2_jeb_v5_") as td:
        manuscript, si = render_sources(Path(td))
        outputs = [
            build_markdown(manuscript, args.output_dir / "Chapter2_JEB_Anonymous_Manuscript_V5.docx", line_numbers=True, stop_heading="Submission completion gates"),
            build_markdown(si, args.output_dir / "Chapter2_JEB_Supporting_Information_V3.docx", line_numbers=True),
            build_markdown(CH / "JEB_TITLE_PAGE_TEMPLATE_V1.md", args.output_dir / "Chapter2_JEB_Title_Page_TEMPLATE_V1.docx", line_numbers=False),
            build_markdown(CH / "JEB_COVER_LETTER_TEMPLATE_V1.md", args.output_dir / "Chapter2_JEB_Cover_Letter_TEMPLATE_V1.docx", line_numbers=False),
        ]
    for path in outputs:
        try:
            print(path.relative_to(ROOT))
        except ValueError:
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
