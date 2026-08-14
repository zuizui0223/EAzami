#!/usr/bin/env python3
"""Materialize frozen public candidate locus packs from durable repository evidence.

The repository stores each compact pack as base64(gzip(TSV)). Each TSV row keeps
locus name, unwrapped recovered sequence, original per-locus FASTA SHA256, and
sequence length. The source artifact FASTAs all use one tip header, 80-character
wrapping and a final newline, so the exact FASTA bytes can be reconstructed and
verified without keeping time-limited GitHub Actions ZIPs or bulky diagnostics.
"""
from __future__ import annotations

import argparse
import base64
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "data/evidence/public_candidate_locus_packs_v1/manifest.json"
EXPECTED_COLUMNS = ["locus", "sequence_length", "fasta_sha256", "sequence"]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fasta_bytes(tip_id: str, sequence: str, width: int = 80) -> bytes:
    wrapped = "\n".join(sequence[i : i + width] for i in range(0, len(sequence), width))
    return f">{tip_id}\n{wrapped}\n".encode("utf-8")


def materialize(candidate_id: str, output: Path, manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, object]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("contract_version") != "public_candidate_locus_packs_v1":
        raise ValueError("unexpected durable candidate-pack contract")
    if manifest.get("tsv_columns") != EXPECTED_COLUMNS:
        raise ValueError("durable candidate-pack TSV schema drift")
    try:
        spec = manifest["candidates"][candidate_id]
    except KeyError as exc:
        raise ValueError(f"unknown candidate: {candidate_id}") from exc

    payload_path = ROOT / spec["payload_path"]
    payload_bytes = payload_path.read_bytes()
    if sha256_bytes(payload_bytes) != spec["payload_sha256"]:
        raise ValueError(f"{candidate_id} durable payload checksum drift")
    encoded = b"".join(payload_bytes.split())
    compressed = base64.b64decode(encoded, validate=True)
    if sha256_bytes(compressed) != spec["gzip_sha256"]:
        raise ValueError(f"{candidate_id} gzip payload checksum drift")
    tsv_bytes = gzip.decompress(compressed)
    if sha256_bytes(tsv_bytes) != spec["tsv_sha256"]:
        raise ValueError(f"{candidate_id} durable TSV checksum drift")

    reader = csv.DictReader(io.StringIO(tsv_bytes.decode("utf-8")), delimiter="\t")
    if reader.fieldnames != EXPECTED_COLUMNS:
        raise ValueError(f"{candidate_id} TSV columns drift")
    rows = list(reader)

    expected_n = int(spec["strict_locus_count"])
    if len(rows) != expected_n:
        raise ValueError(f"{candidate_id} locus count drift: {len(rows)} != {expected_n}")
    loci = [row["locus"] for row in rows]
    if len(loci) != len(set(loci)):
        raise ValueError(f"{candidate_id} duplicate locus names")

    tip_id = str(spec["tip_id"])
    width = int(manifest["fasta_reconstruction"]["line_width"])
    output.mkdir(parents=True, exist_ok=True)
    loci_dir = output / "loci"
    loci_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        locus = row["locus"]
        sequence = row["sequence"].upper()
        if int(row["sequence_length"]) != len(sequence):
            raise ValueError(f"{candidate_id}/{locus} sequence length drift")
        if not sequence or any(base not in "ACGNT" for base in sequence):
            raise ValueError(f"{candidate_id}/{locus} contains unsupported sequence symbols")
        payload = fasta_bytes(tip_id, sequence, width)
        if sha256_bytes(payload) != row["fasta_sha256"]:
            raise ValueError(f"{candidate_id}/{locus} FASTA checksum drift")
        (loci_dir / f"{locus}.fasta").write_bytes(payload)

    strict_payload = "".join(f"{locus}\n" for locus in loci).encode("utf-8")
    if sha256_bytes(strict_payload) != spec["strict_recovered_loci_sha256"]:
        raise ValueError(f"{candidate_id} strict locus-list checksum drift")
    (output / "strict_recovered_loci.txt").write_bytes(strict_payload)

    summary_payload = (json.dumps(spec["source_summary"], indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if sha256_bytes(summary_payload) != spec["summary_sha256"]:
        raise ValueError(f"{candidate_id} source summary checksum drift")
    summary_name = str(spec["summary_filename"])
    (output / summary_name).write_bytes(summary_payload)

    result = {
        "contract_version": "public_candidate_locus_pack_materialization_v1",
        "candidate_id": candidate_id,
        "tip_id": tip_id,
        "strict_locus_count": expected_n,
        "durable_tsv_sha256": spec["tsv_sha256"],
        "source_artifact_id": spec["artifact_id"],
        "source_artifact_sha256": spec["artifact_sha256"],
        "source_artifact_size_bytes": spec["artifact_size_bytes"],
        "source_artifact_expiry_no_longer_runtime_dependency": True,
        "all_per_locus_source_fasta_checksums_verified": True,
    }
    (output / "durable_materialization.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--candidate", choices=("EA01", "EA02", "CNIPG"), required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    result = materialize(args.candidate, args.output, args.manifest)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
