#!/usr/bin/env python3
"""Validate and normalize an OMA marker-gene export for the Chang 2026 Read2Tree screen.

The official OMA Browser marker export is an external scientific input. This
validator turns a downloaded archive into a versioned local contract before any
Read2Tree mapping is allowed. It never tries to reverse-engineer or call an
undocumented OMA export endpoint.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import tarfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

DEFAULT_RELEASE = "May2026"
DEFAULT_COVERAGE = 1.0
DEFAULT_MAX_MARKERS = 400
DEFAULT_EXPECTED_MARKERS = 400
EXPECTED_CODES = ("CYNCS", "HELAN", "DAUCS")
DNA_ALPHABET = frozenset("ACGTURYSWKMBDHVN-")
AA_ALPHABET = frozenset("ABCDEFGHIKLMNPQRSTVWXYZJUO*-")
FASTA_EXTENSIONS = {".fa", ".faa", ".fasta", ".fna"}
DNA_EXTENSIONS = {".fna"}
AUDIT_FIELDS = (
    "marker_id", "aa_source_member", "dna_source_member", "aa_sequence_count",
    "dna_sequence_count", "aa_species_codes", "dna_species_codes", "aa_min_length",
    "aa_max_length", "dna_min_length", "dna_max_length", "same_sequence_ids",
    "frame_length_consistent", "status", "normalized_aa_file", "normalized_dna_file",
)

@dataclass(frozen=True)
class FastaRecord:
    header: str
    sequence: str
    @property
    def sequence_id(self) -> str:
        return self.header.split()[0]
    @property
    def oma_code(self) -> str:
        match = re.match(r"^([A-Z0-9]{5})(?:\d|$)", self.sequence_id)
        if not match:
            raise ValueError(f"Cannot parse five-character OMA code from {self.sequence_id!r}")
        return match.group(1)

def clean(value: object) -> str:
    return str(value or "").strip()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle) if any(clean(value) for value in row.values())]

def validate_reference_manifest(path: Path, release: str) -> list[dict[str, str]]:
    rows = read_csv(path)
    if not rows:
        raise ValueError("OMA reference manifest is empty")
    required = {"oma_release", "oma_code", "scientific_name", "ncbi_taxid", "reference_role", "verified_in_oma", "verification_url"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"OMA reference manifest lacks columns: {sorted(missing)}")
    codes = tuple(row["oma_code"] for row in rows)
    if codes != EXPECTED_CODES:
        raise ValueError(f"Expected reference codes {EXPECTED_CODES}, observed {codes}")
    if any(row["oma_release"] != release for row in rows):
        raise ValueError(f"Reference manifest is not pinned to OMA release {release}")
    if any(row["verified_in_oma"].casefold() != "true" for row in rows):
        raise ValueError("Every OMA reference genome must be independently verified")
    if any(not row["ncbi_taxid"].isdigit() for row in rows):
        raise ValueError("Every OMA reference genome must carry an NCBI taxon ID")
    return rows

def safe_tar_member_name(name: str) -> None:
    posix = PurePosixPath(name)
    if posix.is_absolute() or ".." in posix.parts:
        raise ValueError(f"Unsafe archive member path: {name}")

def read_marker_members(archive: Path) -> tuple[dict[str, bytes], str]:
    raw_sha = sha256_file(archive)
    members: dict[str, bytes] = {}
    seen_basenames: set[str] = set()
    with tarfile.open(archive, "r:*") as tar:
        for member in tar.getmembers():
            safe_tar_member_name(member.name)
            if member.issym() or member.islnk():
                raise ValueError(f"Links are not allowed in the OMA marker archive: {member.name}")
            if not member.isfile() or Path(member.name).suffix.casefold() not in FASTA_EXTENSIONS:
                continue
            basename = Path(member.name).name
            if basename in seen_basenames:
                raise ValueError(f"Duplicate FASTA basename in archive: {basename}")
            seen_basenames.add(basename)
            handle = tar.extractfile(member)
            if handle is None:
                raise ValueError(f"Cannot read archive member {member.name}")
            members[member.name] = handle.read()
    if not members:
        raise ValueError("No marker FASTA files were found in the OMA export archive")
    return members, raw_sha

def parse_fasta(data: bytes, *, alphabet: frozenset[str], label: str) -> list[FastaRecord]:
    text = data.decode("utf-8")
    records: list[FastaRecord] = []
    header: str | None = None
    sequence: list[str] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append(FastaRecord(header=header, sequence="".join(sequence).upper()))
            header = line[1:].strip()
            if not header:
                raise ValueError(f"Empty FASTA header in {label}:{line_number}")
            sequence = []
            continue
        if header is None:
            raise ValueError(f"Sequence before first FASTA header in {label}:{line_number}")
        seq = re.sub(r"\s+", "", line).upper()
        invalid = sorted(set(seq) - alphabet)
        if invalid:
            raise ValueError(f"Invalid sequence characters {invalid} in {label}:{line_number}")
        sequence.append(seq)
    if header is not None:
        records.append(FastaRecord(header=header, sequence="".join(sequence).upper()))
    if not records or any(not record.sequence for record in records):
        raise ValueError(f"Missing or empty FASTA records in {label}")
    ids = [record.sequence_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate FASTA sequence IDs in {label}")
    return records

def marker_id_from_name(name: str) -> str:
    stem = Path(name).stem
    if not re.fullmatch(r"OMAGroup_[A-Za-z0-9_.-]+", stem):
        raise ValueError(f"Unexpected OMA marker filename: {Path(name).name}")
    return stem

def pair_marker_files(members: Mapping[str, bytes]) -> dict[str, dict[str, tuple[str, bytes]]]:
    pairs: dict[str, dict[str, tuple[str, bytes]]] = {}
    for member_name, data in members.items():
        marker_id = marker_id_from_name(member_name)
        kind = "dna" if Path(member_name).suffix.casefold() in DNA_EXTENSIONS else "aa"
        slot = pairs.setdefault(marker_id, {})
        if kind in slot:
            raise ValueError(f"Multiple {kind} FASTA files for marker {marker_id}")
        slot[kind] = (member_name, data)
    incomplete = sorted(marker for marker, pair in pairs.items() if set(pair) != {"aa", "dna"})
    if incomplete:
        raise ValueError("Every OMA marker must have paired AA and DNA files: " + "|".join(incomplete[:20]))
    return pairs

def sort_records(records: Sequence[FastaRecord]) -> list[FastaRecord]:
    return sorted(records, key=lambda record: (record.oma_code, record.sequence_id))

def fasta_text(records: Sequence[FastaRecord], width: int = 80) -> str:
    lines: list[str] = []
    for record in records:
        lines.append(">" + record.header)
        for start in range(0, len(record.sequence), width):
            lines.append(record.sequence[start:start + width])
    return "\n".join(lines) + "\n"

def validate_marker_pair(marker_id: str, aa_source: str, aa_data: bytes, dna_source: str, dna_data: bytes, expected_codes: Sequence[str]):
    aa_records = sort_records(parse_fasta(aa_data, alphabet=AA_ALPHABET, label=aa_source))
    dna_records = sort_records(parse_fasta(dna_data, alphabet=DNA_ALPHABET, label=dna_source))
    aa_codes = [record.oma_code for record in aa_records]
    dna_codes = [record.oma_code for record in dna_records]
    expected = list(expected_codes)
    if len(aa_codes) != len(expected) or set(aa_codes) != set(expected) or len(dna_codes) != len(expected) or set(dna_codes) != set(expected):
        raise ValueError(f"{marker_id}: expected exactly one sequence for {expected}; AA={aa_codes}, DNA={dna_codes}")
    if [r.sequence_id for r in aa_records] != [r.sequence_id for r in dna_records]:
        raise ValueError(f"{marker_id}: AA and DNA sequence identifiers differ")
    for aa_record, dna_record in zip(aa_records, dna_records):
        if len(dna_record.sequence) % 3:
            raise ValueError(f"{marker_id}: coding DNA is not divisible by three")
        aa_len = len(aa_record.sequence.replace("-", "").rstrip("*"))
        dna_len = len(dna_record.sequence.replace("-", "")) // 3
        if dna_len not in {aa_len, aa_len + 1}:
            raise ValueError(f"{marker_id}: coding-DNA length is inconsistent with AA length")
    audit = {
        "marker_id": marker_id, "aa_source_member": aa_source, "dna_source_member": dna_source,
        "aa_sequence_count": len(aa_records), "dna_sequence_count": len(dna_records),
        "aa_species_codes": "|".join(aa_codes), "dna_species_codes": "|".join(dna_codes),
        "aa_min_length": min(len(r.sequence) for r in aa_records), "aa_max_length": max(len(r.sequence) for r in aa_records),
        "dna_min_length": min(len(r.sequence) for r in dna_records), "dna_max_length": max(len(r.sequence) for r in dna_records),
        "same_sequence_ids": "true", "frame_length_consistent": "true", "status": "validated",
        "normalized_aa_file": f"marker_genes/{marker_id}.fa", "normalized_dna_file": f"marker_genes/{marker_id}.fna",
    }
    return audit, aa_records, dna_records

def deterministic_pack_sha(files: Mapping[str, bytes]) -> str:
    digest = hashlib.sha256()
    for name in sorted(files):
        digest.update(name.encode()); digest.update(b"\0"); digest.update(files[name]); digest.update(b"\0")
    return digest.hexdigest()

def validate_and_normalize(*, archive: Path, reference_manifest: Path, outdir: Path, oma_release: str, export_date: str, export_url: str, minimum_species_coverage: float, maximum_markers: int, expected_marker_count: int) -> dict[str, object]:
    if minimum_species_coverage != 1.0:
        raise ValueError("EAzami Read2Tree contract requires minimum species coverage exactly 1.0")
    if maximum_markers != expected_marker_count:
        raise ValueError("Maximum markers and expected marker count must match for a frozen export")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", export_date):
        raise ValueError("export_date must be YYYY-MM-DD")
    refs = validate_reference_manifest(reference_manifest, oma_release)
    expected_codes = tuple(row["oma_code"] for row in refs)
    members, archive_sha = read_marker_members(archive)
    pairs = pair_marker_files(members)
    if len(pairs) != expected_marker_count:
        raise ValueError(f"Expected exactly {expected_marker_count} OMA marker pairs, observed {len(pairs)}")
    normalized: dict[str, bytes] = {}; audits = []; all_dna_records: list[FastaRecord] = []; global_ids: set[str] = set()
    for marker_id in sorted(pairs):
        aa_source, aa_data = pairs[marker_id]["aa"]; dna_source, dna_data = pairs[marker_id]["dna"]
        audit, aa_records, dna_records = validate_marker_pair(marker_id, aa_source, aa_data, dna_source, dna_data, expected_codes)
        for record in dna_records:
            if record.sequence_id in global_ids:
                raise ValueError(f"OMA sequence ID occurs in multiple markers: {record.sequence_id}")
            global_ids.add(record.sequence_id)
        normalized[f"marker_genes/{marker_id}.fa"] = fasta_text(aa_records).encode()
        normalized[f"marker_genes/{marker_id}.fna"] = fasta_text(dna_records).encode()
        all_dna_records.extend(dna_records); audits.append(audit)
    dna_ref = fasta_text(all_dna_records).encode(); normalized["dna_ref.fa"] = dna_ref
    if outdir.exists(): shutil.rmtree(outdir)
    (outdir / "marker_genes").mkdir(parents=True)
    for relative, data in normalized.items():
        destination = outdir / relative; destination.parent.mkdir(parents=True, exist_ok=True); destination.write_bytes(data)
    with (outdir / "marker_pack_locus_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(AUDIT_FIELDS)); writer.writeheader(); writer.writerows(audits)
    contract = {
        "contract_version": "eazami_read2tree_oma_marker_pack_v1", "execution_allowed": True,
        "oma_release": oma_release, "export_date": export_date, "export_url": export_url,
        "export_parameters": {"minimum_species_coverage": minimum_species_coverage, "maximum_markers": maximum_markers},
        "reference_codes": list(expected_codes),
        "reference_taxa": [{"oma_code": r["oma_code"], "scientific_name": r["scientific_name"], "ncbi_taxid": r["ncbi_taxid"], "reference_role": r["reference_role"]} for r in refs],
        "marker_count": len(pairs), "sequence_count_per_marker": len(expected_codes), "archive_path_recorded": archive.name,
        "archive_sha256": archive_sha, "normalized_pack_sha256": deterministic_pack_sha(normalized),
        "normalized_marker_dir": "marker_genes", "dna_reference": "dna_ref.fa", "dna_reference_sha256": sha256_bytes(dna_ref),
        "locus_audit": "marker_pack_locus_audit.csv",
        "claim_limit": "This is a May2026 OMA three-reference marker pack for a Read2Tree topology sensitivity screen. It is not the Moreyra Compositae1061 target set, not the Chang orthogroup set, and not evidence of anthocyanin reactivation."
    }
    (outdir / "marker_pack_contract.json").write_text(json.dumps(contract, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return contract

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(); p.add_argument("--archive", type=Path, required=True); p.add_argument("--reference-manifest", type=Path, required=True); p.add_argument("--outdir", type=Path, required=True); p.add_argument("--oma-release", default=DEFAULT_RELEASE); p.add_argument("--export-date", required=True); p.add_argument("--export-url", default=""); p.add_argument("--minimum-species-coverage", type=float, default=DEFAULT_COVERAGE); p.add_argument("--maximum-markers", type=int, default=DEFAULT_MAX_MARKERS); p.add_argument("--expected-marker-count", type=int, default=DEFAULT_EXPECTED_MARKERS); return p.parse_args()
def main() -> int:
    a = parse_args(); c = validate_and_normalize(archive=a.archive, reference_manifest=a.reference_manifest, outdir=a.outdir, oma_release=a.oma_release, export_date=a.export_date, export_url=a.export_url, minimum_species_coverage=a.minimum_species_coverage, maximum_markers=a.maximum_markers, expected_marker_count=a.expected_marker_count)
    print(f"execution_allowed={str(c['execution_allowed']).lower()}"); print(f"oma_release={c['oma_release']}"); print(f"reference_codes={'|'.join(c['reference_codes'])}"); print(f"marker_count={c['marker_count']}"); print(f"archive_sha256={c['archive_sha256']}"); print(f"normalized_pack_sha256={c['normalized_pack_sha256']}"); return 0
if __name__ == "__main__": raise SystemExit(main())
