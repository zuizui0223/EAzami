#!/usr/bin/env python3
"""Download the official Chang et al. 2026 Figure 1 image.

The Springer article PDF endpoint can reject automated clients even though the
article is open access. The article HTML exposes an official Figure 1 image.
This downloader tries both Springer static-content and media delivery hosts,
preserves the exact successful source, and records every failed endpoint.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Sequence

DOI = "10.1186/s12870-026-08097-6"
ARTICLE_URL = "https://link.springer.com/article/10.1186/s12870-026-08097-6"
IMAGE_OBJECT = (
    "art%3A10.1186%2Fs12870-026-08097-6/"
    "MediaObjects/12870_2026_8097_Fig1_HTML.png"
)
DEFAULT_URLS = (
    f"https://static-content.springer.com/image/{IMAGE_OBJECT}",
    f"https://media.springernature.com/full/springer-static/image/{IMAGE_OBJECT}",
    f"https://media.springernature.com/lw1200/springer-static/image/{IMAGE_OBJECT}",
    f"https://media.springernature.com/lw685/springer-static/image/{IMAGE_OBJECT}",
)
DEFAULT_OUTDIR = Path("data/evidence/generated/chang2026_takaoense_figure")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def image_kind(payload: bytes) -> str:
    if payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if payload.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if payload.startswith((b"GIF87a", b"GIF89a")):
        return "gif"
    if payload[:12].startswith(b"RIFF") and payload[8:12] == b"WEBP":
        return "webp"
    return "unknown"


def write_attempts(path: Path, attempts: Sequence[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(list(attempts), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def download_first_image(
    urls: Sequence[str],
    output: Path,
    timeout: int = 120,
    retries: int = 3,
) -> tuple[str, list[dict[str, str]]]:
    output.parent.mkdir(parents=True, exist_ok=True)
    attempts: list[dict[str, str]] = []
    attempts_path = output.parent / "figure1_download_attempts.json"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "Chrome/126.0 Safari/537.36 EAzami-evidence-audit/1.0"
        ),
        "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": ARTICLE_URL,
    }
    for url in urls:
        for attempt in range(1, retries + 1):
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=timeout) as response:
                    payload = response.read()
                    content_type = response.headers.get("Content-Type", "")
                    final_url = response.geturl()
                kind = image_kind(payload)
                if kind == "unknown":
                    raise ValueError(
                        f"not a recognized image: content-type={content_type!r}, "
                        f"magic={payload[:20]!r}"
                    )
                output.write_bytes(payload)
                attempts.append(
                    {
                        "url": url,
                        "attempt": str(attempt),
                        "status": "downloaded",
                        "final_url": final_url,
                        "content_type": content_type,
                        "image_kind": kind,
                        "error": "",
                    }
                )
                write_attempts(attempts_path, attempts)
                return url, attempts
            except (
                urllib.error.HTTPError,
                urllib.error.URLError,
                TimeoutError,
                ValueError,
            ) as exc:
                attempts.append(
                    {
                        "url": url,
                        "attempt": str(attempt),
                        "status": "failed",
                        "final_url": "",
                        "content_type": "",
                        "image_kind": "",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
                write_attempts(attempts_path, attempts)
                if attempt < retries:
                    time.sleep(2 ** (attempt - 1))
    raise RuntimeError(
        "No configured official Figure 1 endpoint returned an image; "
        f"see {attempts_path}"
    )


def image_dimensions(path: Path) -> tuple[int, int, str]:
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - exercised in workflow
        raise RuntimeError("Pillow is required; install package 'Pillow'") from exc
    with Image.open(path) as image:
        width, height = image.size
        return width, height, image.format or ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--url", action="append", dest="urls")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    image_path = args.outdir / "chang2026_figure1.png"
    attempts: list[dict[str, str]] = []
    if args.force or not image_path.exists():
        selected_url, attempts = download_first_image(
            tuple(args.urls or DEFAULT_URLS), image_path
        )
    else:
        selected_url = "cached_existing_file"

    width, height, image_format = image_dimensions(image_path)
    summary = {
        "doi": DOI,
        "article_url": ARTICLE_URL,
        "figure": "Figure 1",
        "selected_url": selected_url,
        "attempts": attempts,
        "image_path": str(image_path),
        "image_size_bytes": image_path.stat().st_size,
        "image_sha256": sha256_file(image_path),
        "image_width_px": width,
        "image_height_px": height,
        "image_format": image_format,
        "source_interpretation": (
            "Official Springer Nature Figure 1 image. The published caption defines "
            "W as white-corolla and BP as bluish-purple-corolla for var. takaoense tips."
        ),
        "assignment_policy": (
            "Read only labels visible in this figure; do not infer morph from locality."
        ),
    }
    summary_path = args.outdir / "figure1_image_summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    print(f"image_width_px={width}")
    print(f"image_height_px={height}")
    print(f"image_size_bytes={summary['image_size_bytes']}")
    print(f"image_sha256={summary['image_sha256']}")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
