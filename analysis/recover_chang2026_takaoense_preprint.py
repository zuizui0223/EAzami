#!/usr/bin/env python3
"""Recover the Chang et al. preprint PDF and its morph-labelled Figure 1.

The version-of-record Springer PDF and media endpoints can reject automated CI
clients. A CC BY 4.0 Research Square preprint is publicly mirrored as a complete
ResearchGate PDF. This script downloads that PDF with browser-like curl headers,
locates the Figure 1 caption from PDF text, renders the figure/caption pages,
extracts embedded page images, and creates an auditable six-voucher morph table.

No flower-colour state is inferred from locality. A voucher receives W/BP only
when its identifier and explicit state are recoverable from the figure or text.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable, Mapping, Sequence

from recover_chang2026_takaoense_figure import (
    OUTPUT_FIELDS,
    VOUCHERS,
    build_tip_rows,
    parse_direct_tip_labels,
    write_csv,
)

DOI = "10.21203/rs.3.rs-7470174/v1"
PUBLICATION_URL = (
    "https://www.researchgate.net/publication/400638061_"
    "Phylotranscriptomics_and_genome-size_evidence_clarify_the_Taiwanese_"
    "Cirsium_japonicum_complex_and_delimit_C_brevicaule_and_allied_East_Asian_thistles"
)
PDF_URL = (
    PUBLICATION_URL
    + "/fulltext/698ba2ea12f837212a196034/"
    + "Phylotranscriptomics-and-genome-size-evidence-clarify-the-Taiwanese-"
    + "Cirsium-japonicum-complex-and-delimit-C-brevicaule-and-allied-East-"
    + "Asian-thistles.pdf"
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_takaoense_figure")
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_pdf(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 1000 and path.read_bytes()[:4] == b"%PDF"


def curl_download(url: str, output: Path, timeout: int = 180) -> dict[str, object]:
    temp = output.with_suffix(output.suffix + ".part")
    command = [
        "curl",
        "--fail",
        "--location",
        "--compressed",
        "--retry",
        "3",
        "--retry-delay",
        "2",
        "--connect-timeout",
        "30",
        "--max-time",
        str(timeout),
        "--user-agent",
        USER_AGENT,
        "--referer",
        PUBLICATION_URL,
        "--header",
        "Accept: application/pdf,text/html;q=0.9,*/*;q=0.8",
        "--header",
        "Accept-Language: en-US,en;q=0.9",
        "--output",
        str(temp),
        "--write-out",
        "%{http_code}\t%{content_type}\t%{url_effective}",
        url,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    result: dict[str, object] = {
        "method": "curl",
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "valid_pdf": False,
    }
    if completed.returncode == 0 and is_pdf(temp):
        temp.replace(output)
        result["valid_pdf"] = True
        result["size_bytes"] = output.stat().st_size
    elif temp.exists():
        result["downloaded_size_bytes"] = temp.stat().st_size
        result["magic_hex"] = temp.read_bytes()[:32].hex()
        temp.unlink()
    return result


def urllib_download(url: str, output: Path, timeout: int = 180) -> dict[str, object]:
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": PUBLICATION_URL,
        "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    result: dict[str, object] = {"method": "urllib", "valid_pdf": False}
    temp = output.with_suffix(output.suffix + ".part")
    try:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read()
            result.update(
                {
                    "status": getattr(response, "status", 200),
                    "content_type": response.headers.get("Content-Type", ""),
                    "final_url": response.geturl(),
                    "downloaded_size_bytes": len(payload),
                    "magic_hex": payload[:32].hex(),
                }
            )
        temp.write_bytes(payload)
        if is_pdf(temp):
            temp.replace(output)
            result["valid_pdf"] = True
            result["size_bytes"] = output.stat().st_size
        else:
            temp.unlink(missing_ok=True)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        temp.unlink(missing_ok=True)
    return result


def download_pdf(url: str, output: Path) -> list[dict[str, object]]:
    output.parent.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, object]] = []
    attempts.append(curl_download(url, output))
    if is_pdf(output):
        return attempts
    attempts.append(urllib_download(url, output))
    if not is_pdf(output):
        raise RuntimeError(
            "ResearchGate preprint PDF recovery failed: "
            + json.dumps(attempts, ensure_ascii=False)
        )
    return attempts


def caption_page_indices(doc: object) -> list[int]:
    """Locate Figure 1 and return nearby figure/caption pages."""
    hits: list[int] = []
    for page_index in range(doc.page_count):
        text = doc.load_page(page_index).get_text("text")
        compact = re.sub(r"\s+", " ", text).casefold()
        if (
            "figure 1" in compact
            and "phylotranscriptomic reconstruction and species delimitation" in compact
        ):
            hits.append(page_index)
    if not hits:
        # ResearchGate extraction sometimes inserts spaces into "Figure".
        for page_index in range(doc.page_count):
            text = doc.load_page(page_index).get_text("text")
            compact = re.sub(r"\s+", " ", text).casefold()
            if (
                "phylotranscriptomic reconstruction and species delimitation" in compact
                and "white-corolla morph" in compact
                and "bluish-purple-corolla morph" in compact
            ):
                hits.append(page_index)
    if not hits:
        raise ValueError("Figure 1 caption was not located in the recovered preprint")

    selected: set[int] = set()
    for hit in hits:
        for page_index in (hit - 1, hit, hit + 1):
            if 0 <= page_index < doc.page_count:
                selected.add(page_index)
    return sorted(selected)


def render_figure_pages(
    pdf_path: Path,
    outdir: Path,
    zoom: float = 5.0,
) -> dict[str, object]:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required") from exc

    render_dir = outdir / "rendered_preprint_figure1"
    embedded_dir = outdir / "embedded_preprint_figure1"
    render_dir.mkdir(parents=True, exist_ok=True)
    embedded_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    page_indices = caption_page_indices(doc)
    text_parts: list[str] = []
    rendered: list[str] = []
    embedded: list[str] = []
    word_rows: list[dict[str, object]] = []

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        page_text = page.get_text("text")
        text_parts.append(f"\n===== PDF PAGE {page_index + 1} =====\n{page_text}")
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

        seen: set[int] = set()
        for image_index, image_info in enumerate(page.get_images(full=True), start=1):
            xref = int(image_info[0])
            if xref in seen:
                continue
            seen.add(xref)
            image = doc.extract_image(xref)
            extension = image.get("ext", "bin")
            image_path = embedded_dir / (
                f"page_{page_index + 1:02d}_image_{image_index:02d}_xref_{xref}.{extension}"
            )
            image_path.write_bytes(image["image"])
            embedded.append(str(image_path))

    full_text = "".join(text_parts)
    text_path = outdir / "preprint_text.txt"
    text_path.write_text(full_text, encoding="utf-8")
    write_csv(
        outdir / "preprint_figure1_page_words.csv",
        word_rows,
        ("pdf_page", "x0", "y0", "x1", "y1", "token", "block", "line", "word_index"),
    )

    explicit_assignments = parse_direct_tip_labels(full_text)
    write_csv(
        outdir / "takaoense_tip_morph_recovery.csv",
        build_tip_rows(explicit_assignments),
        OUTPUT_FIELDS,
    )
    caption_defines_states = bool(
        re.search(r"\(W\).*white-corolla morph", full_text, flags=re.I | re.S)
        and re.search(r"\(BP\).*bluish-purple-corolla morph", full_text, flags=re.I | re.S)
    )
    return {
        "pdf_page_count": doc.page_count,
        "figure1_page_indices_zero_based": page_indices,
        "rendered_pages": rendered,
        "embedded_images": embedded,
        "word_count_on_selected_pages": len(word_rows),
        "caption_defines_W_and_BP": caption_defines_states,
        "direct_text_assignments": explicit_assignments,
        "direct_text_assignment_count": sum(
            state in {"W", "BP"} for state in explicit_assignments.values()
        ),
        "manual_visual_review_required": len(explicit_assignments) < len(VOUCHERS),
        "text_path": str(text_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--url", default=PDF_URL)
    parser.add_argument("--zoom", type=float, default=5.0)
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    pdf_path = args.outdir / "chang2026_researchsquare_preprint.pdf"
    attempts: list[dict[str, object]] = []
    if args.force or not is_pdf(pdf_path):
        attempts = download_pdf(args.url, pdf_path)

    evidence = render_figure_pages(pdf_path, args.outdir, zoom=args.zoom)
    summary = {
        "preprint_doi": DOI,
        "publication_url": PUBLICATION_URL,
        "download_url": args.url,
        "download_attempts": attempts,
        "pdf_path": str(pdf_path),
        "pdf_size_bytes": pdf_path.stat().st_size,
        "pdf_sha256": sha256_file(pdf_path),
        "license": "CC BY 4.0",
        **evidence,
        "assignment_policy": (
            "Accept W/BP only from an explicit figure/voucher label; never infer from locality."
        ),
    }
    summary_path = args.outdir / "preprint_recovery_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"pdf_page_count={summary['pdf_page_count']}")
    print("figure1_pages=" + "|".join(map(str, summary["figure1_page_indices_zero_based"])))
    print(f"rendered_pages={len(summary['rendered_pages'])}")
    print(f"embedded_images={len(summary['embedded_images'])}")
    print(f"caption_defines_W_and_BP={summary['caption_defines_W_and_BP']}")
    print(f"direct_text_assignment_count={summary['direct_text_assignment_count']}")
    print(f"manual_visual_review_required={summary['manual_visual_review_required']}")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
