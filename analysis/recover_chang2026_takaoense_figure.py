#!/usr/bin/env python3
"""Recover Figure 1 evidence for the six published var. takaoense tips.

Chang et al. (2026) Supplementary Table S1 identifies six transcriptome
vouchers but omits their white versus bluish-purple morph identity. The main
article's Figure 1 caption explicitly states that tip suffixes ``(W)`` and
``(BP)`` identify the two corolla morphs. This script downloads the open-access
article PDF, preserves provenance, extracts page text/words and embedded images,
and renders the Figure 1 pages at high resolution for an auditable manual or
machine-assisted tip-label recovery.

The script never assigns a morph from locality or taxon-level expectations.
A tip remains unresolved unless a figure label, voucher image, label, or author
confirmation directly supports the assignment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Mapping, Sequence

DOI = "10.1186/s12870-026-08097-6"
DEFAULT_URLS = (
    "https://link.springer.com/content/pdf/10.1186/s12870-026-08097-6.pdf",
    "https://bmcplantbiol.biomedcentral.com/counter/pdf/10.1186/s12870-026-08097-6.pdf",
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_takaoense_figure")
# The published PDF is 0-indexed here. Figure 1 occupies article/PDF page 7,
# while its full caption continues on the following page.
DEFAULT_PAGE_INDICES = (6, 7)

VOUCHERS = (
    {
        "location": "Fenchihu, Chiayi",
        "code": "FC",
        "coordinate": "23°30'N, 120°41'E",
        "altitude_m": "1364",
        "voucher": "ccy3559",
        "herbarium": "TNM",
    },
    {
        "location": "Tengji, Kaohsiung",
        "code": "TJ",
        "coordinate": "23°02'N, 120°42'E",
        "altitude_m": "1127",
        "voucher": "ccy3807",
        "herbarium": "TCF",
    },
    {
        "location": "Nanheng, Taitung",
        "code": "NH",
        "coordinate": "23°10'N, 121°02'E",
        "altitude_m": "991",
        "voucher": "ccy3835",
        "herbarium": "TCF",
    },
    {
        "location": "Wutai, Pingtung",
        "code": "WY",
        "coordinate": "22°44'N, 120°44'E",
        "altitude_m": "977",
        "voucher": "ccy3560",
        "herbarium": "TNM",
    },
    {
        "location": "Fengbin, Hualien",
        "code": "FB",
        "coordinate": "23°40'N, 121°32'E",
        "altitude_m": "21",
        "voucher": "ccy3629",
        "herbarium": "TNM",
    },
    {
        "location": "Ludao, Taitung",
        "code": "LT",
        "coordinate": "22°40'N, 121°30'E",
        "altitude_m": "73",
        "voucher": "ccy3839",
        "herbarium": "TCF",
    },
)

OUTPUT_FIELDS = (
    "accepted_taxon",
    "location",
    "code",
    "coordinate",
    "altitude_m",
    "voucher",
    "herbarium",
    "published_figure_label",
    "flower_colour_state",
    "binary_colour_code",
    "evidence_source",
    "evidence_locator",
    "assignment_method",
    "morph_assignment_confidence",
    "review_status",
    "notes",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def download_first(
    urls: Sequence[str],
    path: Path,
    timeout: int = 180,
    retries: int = 3,
) -> tuple[str, list[dict[str, str]]]:
    """Download the first valid PDF and retain every attempted endpoint."""
    path.parent.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, str]] = []
    headers = {
        "User-Agent": "EAzami-Chang2026-figure-recovery/1.0",
        "Accept": "application/pdf,*/*",
    }
    for url in urls:
        for attempt in range(1, retries + 1):
            temp = path.with_suffix(path.suffix + ".part")
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    payload = response.read()
                    content_type = response.headers.get("Content-Type", "")
                    final_url = response.geturl()
                if not payload.startswith(b"%PDF"):
                    raise ValueError(
                        f"response is not a PDF (content-type={content_type!r}, "
                        f"magic={payload[:16]!r})"
                    )
                temp.write_bytes(payload)
                temp.replace(path)
                attempts.append(
                    {
                        "url": url,
                        "attempt": str(attempt),
                        "status": "downloaded",
                        "final_url": final_url,
                        "content_type": content_type,
                        "error": "",
                    }
                )
                return url, attempts
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError,
                ValueError,
            ) as exc:
                if temp.exists():
                    temp.unlink()
                attempts.append(
                    {
                        "url": url,
                        "attempt": str(attempt),
                        "status": "failed",
                        "final_url": "",
                        "content_type": "",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                if attempt < retries:
                    time.sleep(2 ** (attempt - 1))
    raise RuntimeError("No configured Chang 2026 article endpoint returned a valid PDF")


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


def normalize_label_text(value: str) -> str:
    value = value.replace("−", "-").replace("–", "-").replace("—", "-")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def parse_direct_tip_labels(text: str) -> dict[str, str]:
    """Parse only explicit identifier + (W)/(BP) labels on the same text line.

    Restricting a match to one extracted line prevents a short locality code from
    borrowing the state attached to the next tree tip. If the figure is rasterized
    and its labels are therefore absent from PDF text, all six rows remain
    unresolved for high-resolution figure review.
    """
    lines = [
        normalize_label_text(line)
        for line in text.splitlines()
        if normalize_label_text(line)
    ]
    identifiers: dict[str, str] = {}
    for row in VOUCHERS:
        identifiers[row["code"]] = row["voucher"]
        identifiers[row["voucher"]] = row["voucher"]

    states_by_voucher: dict[str, set[str]] = {}
    for line in lines:
        line_states = {
            match.upper()
            for match in re.findall(r"\((W|BP)\)", line, flags=re.IGNORECASE)
        }
        if not line_states:
            continue
        for identifier, voucher in identifiers.items():
            if re.search(
                rf"(?<![A-Za-z0-9]){re.escape(identifier)}(?![A-Za-z0-9])",
                line,
                flags=re.IGNORECASE,
            ):
                states_by_voucher.setdefault(voucher, set()).update(line_states)

    output: dict[str, str] = {}
    for voucher, states in states_by_voucher.items():
        if len(states) == 1:
            output[voucher] = next(iter(states))
        elif len(states) > 1:
            output[voucher] = "CONFLICT"
    return output


def build_tip_rows(assignments: Mapping[str, str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in VOUCHERS:
        state = assignments.get(source["voucher"], "")
        if state == "W":
            colour = "white"
            binary = "W"
            status = "assigned_from_explicit_figure_label"
            confidence = "high"
        elif state == "BP":
            colour = "bluish-purple"
            binary = "C"
            status = "assigned_from_explicit_figure_label"
            confidence = "high"
        elif state == "CONFLICT":
            colour = ""
            binary = ""
            status = "conflicting_explicit_labels_require_adjudication"
            confidence = "conflict"
        else:
            colour = ""
            binary = ""
            status = "unresolved_pending_figure_review"
            confidence = "unresolved"
        rows.append(
            {
                "accepted_taxon": "Cirsium japonicum var. takaoense",
                **source,
                "published_figure_label": state if state in {"W", "BP"} else "",
                "flower_colour_state": colour,
                "binary_colour_code": binary,
                "evidence_source": f"Chang et al. 2026; DOI {DOI}; Figure 1",
                "evidence_locator": "Figure 1 tip label; caption defines W and BP",
                "assignment_method": (
                    "explicit_identifier_and_state_text"
                    if state in {"W", "BP"}
                    else "manual_high_resolution_figure_review_required"
                ),
                "morph_assignment_confidence": confidence,
                "review_status": status,
                "notes": "No assignment from geography or taxon-level colour assumptions.",
            }
        )
    return rows


def recover_pdf_evidence(
    pdf_path: Path,
    outdir: Path,
    page_indices: Sequence[int],
    zoom: float,
) -> dict[str, object]:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover - exercised in workflow
        raise RuntimeError("PyMuPDF is required; install package 'PyMuPDF'") from exc

    render_dir = outdir / "rendered_pages"
    image_dir = outdir / "embedded_images"
    render_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    if doc.page_count <= max(page_indices):
        raise ValueError(
            f"PDF has {doc.page_count} pages; requested page {max(page_indices)}"
        )

    all_text_parts: list[str] = []
    word_rows: list[dict[str, object]] = []
    rendered: list[str] = []
    embedded: list[str] = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_text = page.get_text("text")
        all_text_parts.append(f"\n===== PDF PAGE {page_index + 1} =====\n{page_text}")
        if page_index not in page_indices:
            continue

        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        render_path = render_dir / f"page_{page_index + 1:02d}_zoom_{zoom:g}.png"
        pix.save(render_path)
        rendered.append(str(render_path))

        for word in page.get_text("words"):
            x0, y0, x1, y1, token, block, line, word_index = word
            word_rows.append(
                {
                    "pdf_page": page_index + 1,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "token": token,
                    "block": block,
                    "line": line,
                    "word_index": word_index,
                }
            )

        seen_xrefs: set[int] = set()
        for image_index, image in enumerate(page.get_images(full=True), start=1):
            xref = int(image[0])
            if xref in seen_xrefs:
                continue
            seen_xrefs.add(xref)
            extracted = doc.extract_image(xref)
            extension = extracted.get("ext", "bin")
            image_path = image_dir / (
                f"page_{page_index + 1:02d}_image_{image_index:02d}_xref_{xref}.{extension}"
            )
            image_path.write_bytes(extracted["image"])
            embedded.append(str(image_path))

    full_text = "".join(all_text_parts)
    text_path = outdir / "article_text.txt"
    text_path.write_text(full_text, encoding="utf-8")
    write_csv(
        outdir / "figure1_page_words.csv",
        word_rows,
        (
            "pdf_page",
            "x0",
            "y0",
            "x1",
            "y1",
            "token",
            "block",
            "line",
            "word_index",
        ),
    )

    caption_has_definition = bool(
        re.search(r"\(W\).*white-corolla morph", full_text, flags=re.I | re.S)
        and re.search(
            r"\(BP\).*bluish-purple-corolla morph",
            full_text,
            flags=re.I | re.S,
        )
    )
    assignments = parse_direct_tip_labels(full_text)
    write_csv(
        outdir / "takaoense_tip_morph_recovery.csv",
        build_tip_rows(assignments),
        OUTPUT_FIELDS,
    )

    return {
        "pdf_page_count": doc.page_count,
        "rendered_pages": rendered,
        "embedded_images": embedded,
        "figure_page_word_count": len(word_rows),
        "caption_defines_W_and_BP": caption_has_definition,
        "direct_text_assignments": assignments,
        "direct_assignment_count": sum(
            state in {"W", "BP"} for state in assignments.values()
        ),
        "manual_figure_review_required": len(assignments) < len(VOUCHERS),
        "article_text_path": str(text_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--url", action="append", dest="urls")
    parser.add_argument("--page-index", action="append", type=int, dest="page_indices")
    parser.add_argument("--zoom", type=float, default=5.0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    urls = tuple(args.urls or DEFAULT_URLS)
    page_indices = tuple(args.page_indices or DEFAULT_PAGE_INDICES)
    args.outdir.mkdir(parents=True, exist_ok=True)
    pdf_path = args.outdir / "chang2026_article.pdf"

    attempts: list[dict[str, str]] = []
    selected_url = ""
    if args.force or not pdf_path.exists():
        selected_url, attempts = download_first(urls, pdf_path)
    else:
        selected_url = "cached_existing_file"

    evidence = recover_pdf_evidence(
        pdf_path=pdf_path,
        outdir=args.outdir,
        page_indices=page_indices,
        zoom=args.zoom,
    )
    summary = {
        "doi": DOI,
        "selected_url": selected_url,
        "download_attempts": attempts,
        "pdf_path": str(pdf_path),
        "pdf_size_bytes": pdf_path.stat().st_size,
        "pdf_sha256": sha256_file(pdf_path),
        "requested_page_indices_zero_based": list(page_indices),
        "render_zoom": args.zoom,
        **evidence,
        "interpretation": (
            "The article caption establishes W/BP as sample-level morph labels. "
            "Assignments are accepted only when a voucher/code and state are directly "
            "recoverable from the figure; otherwise high-resolution manual review remains required."
        ),
    }
    summary_path = args.outdir / "recovery_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"pdf_pages={summary['pdf_page_count']}")
    print(f"caption_defines_W_and_BP={summary['caption_defines_W_and_BP']}")
    print(f"rendered_pages={len(summary['rendered_pages'])}")
    print(f"embedded_images={len(summary['embedded_images'])}")
    print(f"direct_assignment_count={summary['direct_assignment_count']}")
    print(f"manual_figure_review_required={summary['manual_figure_review_required']}")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
