#!/usr/bin/env python3
"""Build a deterministic May-2026 OMA marker pack without Browser export.

This profile is intentionally *not* claimed to reproduce the OMA Browser
"most complete marker genes" ranking. It uses the official May-2026 OMA Groups
flat file to find strict groups containing CYNCS, HELAN and DAUCS, ranks
qualifying groups by broad OMA-group membership (descending) and a stable
membership fingerprint, selects the first N groups (400 by default), then
retrieves only the selected 3*N protein records from the current OMA REST API.

The current API is required to report the pinned May-2026 database release.
This prevents silently combining an archived group definition with sequences
from a later OMA release.

Outputs include a Browser-export-like paired AA/DNA marker tarball that can be
fed through ``validate_read2tree_oma_marker_pack.py`` to obtain the standard
EAzami Read2Tree marker contract.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import tarfile
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence

PROFILE_ID = "oma_may2026_static_broadconservation400_v1"
DEFAULT_RELEASE = "May2026"
EXPECTED_CODES = ("CYNCS", "HELAN", "DAUCS")
DEFAULT_TARGET_COUNT = 400
DEFAULT_GROUP_URLS = (
    "https://omabrowser.org/All.May2026/oma-groups.txt.gz",
    "https://zenodo.org/records/20922901/files/oma-groups.txt.gz?download=1",
)
EXPECTED_GROUP_MD5 = "9ba959acbece7547b59eb8e6bc1b7947"
DEFAULT_API_BASE = "https://omabrowser.org/api"
OMA_ID_RE = re.compile(r"(?<![A-Z0-9])([A-Z0-9]{5}\d{5})(?!\d)")
AA_ALPHABET = frozenset("ABCDEFGHIKLMNPQRSTVWXYZJUO*")
DNA_ALPHABET = frozenset("ACGTURYSWKMBDHVN")
SELECTION_FIELDS = (
    "rank", "source_line_number", "group_fingerprint", "total_group_members",
    "cynara_omaid", "helianthus_omaid", "daucus_omaid", "all_member_sha256",
    "marker_id",
)


def clean(value: object) -> str:
    return str(value or "").strip()


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json_bytes(payload: bytes, label: str) -> object:
    try:
        return json.loads(payload.decode("utf-8"))
    except Exception as exc:
        raise ValueError(f"{label}: response is not valid UTF-8 JSON") from exc


def http_request(
    request: urllib.request.Request,
    *,
    timeout: int = 120,
    retries: int = 5,
    sleep: Callable[[float], None] = time.sleep,
) -> bytes:
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if attempt + 1 >= retries:
                raise RuntimeError(
                    f"HTTP request failed after {retries} attempts: {request.full_url}"
                ) from exc
            delay = float(2 ** attempt)
            if isinstance(exc, urllib.error.HTTPError):
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if retry_after and retry_after.isdigit():
                    delay = max(delay, float(retry_after))
            sleep(delay)
    raise AssertionError("unreachable")


def download_group_file(
    destination: Path,
    *,
    urls: Sequence[str] = DEFAULT_GROUP_URLS,
    expected_md5: str = EXPECTED_GROUP_MD5,
) -> tuple[str, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        observed = md5_file(destination)
        if observed != expected_md5:
            raise ValueError(
                f"Existing OMA group file MD5 mismatch: {observed} != {expected_md5}"
            )
        return str(destination), "existing_verified"

    errors: list[str] = []
    for url in urls:
        temp = destination.with_suffix(destination.suffix + ".part")
        if temp.exists():
            temp.unlink()
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "EAzami-OMA-static-marker-builder/1.0",
                    "Accept": "application/gzip,application/octet-stream,*/*",
                },
            )
            payload = http_request(request, timeout=300)
            temp.write_bytes(payload)
            observed = md5_file(temp)
            if observed != expected_md5:
                raise ValueError(f"MD5 mismatch from {url}: {observed}")
            temp.replace(destination)
            return url, "downloaded_verified"
        except Exception as exc:
            errors.append(f"{url}: {exc}")
            if temp.exists():
                temp.unlink()
    raise RuntimeError(
        "Unable to recover verified May2026 oma-groups.txt.gz:\n" + "\n".join(errors)
    )


@dataclass(frozen=True)
class QualifyingGroup:
    source_line_number: int
    member_ids: tuple[str, ...]
    ref_ids: tuple[str, ...]

    @property
    def total_members(self) -> int:
        return len(self.member_ids)

    @property
    def fingerprint(self) -> str:
        joined = "|".join(self.member_ids)
        return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]

    @property
    def member_sha256(self) -> str:
        return sha256_text("|".join(self.member_ids))


def parse_group_line(
    line: str,
    line_number: int,
    expected_codes: Sequence[str] = EXPECTED_CODES,
) -> QualifyingGroup | None:
    ids = sorted(set(OMA_ID_RE.findall(line)))
    if not ids:
        return None
    refs: list[str] = []
    for code in expected_codes:
        matches = [omaid for omaid in ids if omaid.startswith(code)]
        if len(matches) != 1:
            return None
        refs.append(matches[0])
    return QualifyingGroup(
        source_line_number=line_number,
        member_ids=tuple(ids),
        ref_ids=tuple(refs),
    )


def iter_qualifying_groups(
    path: Path,
    expected_codes: Sequence[str] = EXPECTED_CODES,
) -> Iterable[QualifyingGroup]:
    opener = gzip.open if path.suffix.casefold() == ".gz" else open
    with opener(path, "rt", encoding="utf-8", errors="strict") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            group = parse_group_line(stripped, line_number, expected_codes)
            if group is not None:
                yield group


def select_groups(
    groups: Iterable[QualifyingGroup],
    *,
    target_count: int = DEFAULT_TARGET_COUNT,
) -> list[QualifyingGroup]:
    if target_count < 1:
        raise ValueError("target_count must be >=1")
    unique: dict[str, QualifyingGroup] = {}
    for group in groups:
        key = group.member_sha256
        previous = unique.get(key)
        if previous is None or group.source_line_number < previous.source_line_number:
            unique[key] = group
    ordered = sorted(
        unique.values(),
        key=lambda group: (
            -group.total_members,
            group.fingerprint,
            group.source_line_number,
        ),
    )
    if len(ordered) < target_count:
        raise ValueError(
            f"Only {len(ordered)} qualifying three-reference OMA groups are available; "
            f"cannot select {target_count}"
        )
    return ordered[:target_count]


def marker_id(rank: int, group: QualifyingGroup) -> str:
    return f"OMAGroup_STATIC_{rank:04d}_{group.fingerprint}"


def selection_rows(groups: Sequence[QualifyingGroup]) -> list[dict[str, object]]:
    rows = []
    for rank, group in enumerate(groups, start=1):
        rows.append(
            {
                "rank": rank,
                "source_line_number": group.source_line_number,
                "group_fingerprint": group.fingerprint,
                "total_group_members": group.total_members,
                "cynara_omaid": group.ref_ids[0],
                "helianthus_omaid": group.ref_ids[1],
                "daucus_omaid": group.ref_ids[2],
                "all_member_sha256": group.member_sha256,
                "marker_id": marker_id(rank, group),
            }
        )
    return rows


def recursive_strings(value: object) -> list[str]:
    output: list[str] = []
    if isinstance(value, str):
        output.append(value)
    elif isinstance(value, Mapping):
        for key, nested in value.items():
            output.extend(recursive_strings(key))
            output.extend(recursive_strings(nested))
    elif isinstance(value, Sequence) and not isinstance(
        value, (bytes, bytearray, str)
    ):
        for nested in value:
            output.extend(recursive_strings(nested))
    return output


def validate_api_release(
    payload: object,
    expected_release: str = DEFAULT_RELEASE,
) -> str:
    tokens = [text.replace(" ", "").casefold() for text in recursive_strings(payload)]
    expected = expected_release.replace(" ", "").casefold()
    acceptable = {expected, ("all." + expected).casefold()}
    if not any(
        any(candidate in token for candidate in acceptable) for token in tokens
    ):
        raise ValueError(
            f"OMA API does not report pinned release {expected_release}; "
            f"version payload={payload!r}"
        )
    return expected_release


def get_api_version(
    *,
    api_base: str = DEFAULT_API_BASE,
    cache_dir: Path | None = None,
    request_func: Callable[[urllib.request.Request], bytes] = http_request,
) -> object:
    cache_path = cache_dir / "api_version.json" if cache_dir else None
    if cache_path and cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    request = urllib.request.Request(
        api_base.rstrip("/") + "/version/",
        headers={
            "User-Agent": "EAzami-OMA-static-marker-builder/1.0",
            "Accept": "application/json",
        },
    )
    payload = read_json_bytes(request_func(request), "OMA API version")
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    return payload


def normalize_protein_target(query_id: str, target: object) -> dict[str, object]:
    if target is None or target == {} or target == []:
        raise ValueError(f"OMA API returned no protein record for {query_id}")
    if isinstance(target, Mapping):
        record = dict(target)
    else:
        raise ValueError(
            f"OMA API target for {query_id} is not an object: {target!r}"
        )
    observed = clean(record.get("omaid") or record.get("oma_id") or record.get("id"))
    if observed and observed != query_id:
        raise ValueError(
            f"OMA API ID mismatch: requested {query_id}, returned {observed}"
        )
    record["_query_omaid"] = query_id
    return record


def parse_bulk_response(
    query_ids: Sequence[str],
    payload: object,
) -> dict[str, dict[str, object]]:
    if isinstance(payload, Mapping):
        if "results" in payload:
            payload = payload["results"]
        elif all(query_id in payload for query_id in query_ids):
            return {
                query_id: normalize_protein_target(query_id, payload[query_id])
                for query_id in query_ids
            }
    if not isinstance(payload, list):
        raise ValueError(f"Unexpected OMA bulk response: {type(payload).__name__}")
    if len(payload) != len(query_ids):
        raise ValueError(
            f"OMA bulk response length differs from query: {len(payload)} != {len(query_ids)}"
        )

    output: dict[str, dict[str, object]] = {}
    for expected_id, item in zip(query_ids, payload):
        query_id = expected_id
        target = item
        if isinstance(item, (list, tuple)) and len(item) == 2:
            query_id = clean(item[0]) or expected_id
            target = item[1]
            if query_id != expected_id:
                raise ValueError(
                    f"OMA bulk response order/id mismatch: {expected_id} != {query_id}"
                )
        elif isinstance(item, Mapping) and "query_id" in item and "target" in item:
            query_id = clean(item.get("query_id")) or expected_id
            target = item.get("target")
            if query_id != expected_id:
                raise ValueError(
                    f"OMA bulk response query id mismatch: {expected_id} != {query_id}"
                )
        output[expected_id] = normalize_protein_target(expected_id, target)
    return output


def api_bulk_fetch(
    query_ids: Sequence[str],
    *,
    api_base: str = DEFAULT_API_BASE,
    cache_dir: Path | None = None,
    batch_size: int = 500,
    request_func: Callable[[urllib.request.Request], bytes] = http_request,
) -> dict[str, dict[str, object]]:
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("OMA bulk API batch_size must be 1..1000")
    cache_dir = cache_dir or Path(".oma_api_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    output: dict[str, dict[str, object]] = {}
    missing: list[str] = []
    for omaid in query_ids:
        path = cache_dir / f"{omaid}.json"
        if path.exists():
            output[omaid] = normalize_protein_target(
                omaid, json.loads(path.read_text(encoding="utf-8"))
            )
        else:
            missing.append(omaid)

    for start in range(0, len(missing), batch_size):
        batch = missing[start:start + batch_size]
        body = json.dumps(batch).encode("utf-8")
        request = urllib.request.Request(
            api_base.rstrip("/") + "/protein/bulk_retrieve/",
            data=body,
            method="POST",
            headers={
                "User-Agent": "EAzami-OMA-static-marker-builder/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        payload = read_json_bytes(
            request_func(request), "OMA bulk protein response"
        )
        parsed = parse_bulk_response(batch, payload)
        for omaid, record in parsed.items():
            (cache_dir / f"{omaid}.json").write_text(
                json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            output[omaid] = record

    missing_after = [omaid for omaid in query_ids if omaid not in output]
    if missing_after:
        raise ValueError(
            "Missing OMA API records after fetch: " + "|".join(missing_after[:20])
        )
    return output


def extract_sequence(
    record: Mapping[str, object],
    keys: Sequence[str],
    label: str,
) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return re.sub(r"\s+", "", value).upper()
    raise ValueError(
        f"OMA API protein {record.get('_query_omaid')} lacks {label}; "
        f"tried {list(keys)}"
    )


def validate_seq(seq: str, alphabet: frozenset[str], label: str) -> None:
    invalid = sorted(set(seq) - alphabet)
    if invalid:
        raise ValueError(f"{label}: invalid characters {invalid}")
    if not seq:
        raise ValueError(f"{label}: empty sequence")


def sequence_pair(record: Mapping[str, object]) -> tuple[str, str]:
    omaid = clean(record.get("_query_omaid"))
    aa = extract_sequence(
        record, ("sequence", "protein_sequence", "protein"), "protein sequence"
    )
    dna = extract_sequence(
        record, ("cdna", "cds", "coding_sequence", "dna"), "coding DNA"
    )
    aa = aa.rstrip("*")
    dna = dna.replace("U", "T")
    validate_seq(aa, AA_ALPHABET, f"{omaid} AA")
    validate_seq(dna, DNA_ALPHABET, f"{omaid} DNA")
    if len(dna) % 3:
        raise ValueError(
            f"{omaid}: coding DNA length {len(dna)} is not divisible by 3"
        )
    codons = len(dna) // 3
    if codons not in {len(aa), len(aa) + 1}:
        raise ValueError(
            f"{omaid}: protein/CDS length mismatch aa={len(aa)}, codons={codons}"
        )
    return aa, dna


def wrap_fasta(omaid: str, seq: str, width: int = 80) -> str:
    lines = [f">{omaid}"]
    lines.extend(seq[start:start + width] for start in range(0, len(seq), width))
    return "\n".join(lines) + "\n"


def write_selection(
    path: Path,
    rows: Sequence[Mapping[str, object]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(SELECTION_FIELDS))
        writer.writeheader()
        writer.writerows(rows)


def build_export_tarball(
    selected: Sequence[QualifyingGroup],
    protein_records: Mapping[str, Mapping[str, object]],
    *,
    output_tarball: Path,
) -> tuple[Path, list[dict[str, object]]]:
    """Write a byte-reproducible gzip tarball of paired AA/DNA marker files."""
    output_tarball.parent.mkdir(parents=True, exist_ok=True)
    selection = selection_rows(selected)
    files: dict[str, bytes] = {}
    for rank, group in enumerate(selected, start=1):
        mid = marker_id(rank, group)
        aa_parts: list[str] = []
        dna_parts: list[str] = []
        for omaid in group.ref_ids:
            aa, dna = sequence_pair(protein_records[omaid])
            aa_parts.append(wrap_fasta(omaid, aa))
            dna_parts.append(wrap_fasta(omaid, dna))
        files[f"{mid}.fa"] = "".join(aa_parts).encode("utf-8")
        files[f"{mid}.fna"] = "".join(dna_parts).encode("utf-8")

    with output_tarball.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w") as tar:
                for name in sorted(files):
                    payload = files[name]
                    info = tarfile.TarInfo(name=name)
                    info.size = len(payload)
                    info.mtime = 0
                    info.uid = 0
                    info.gid = 0
                    info.uname = ""
                    info.gname = ""
                    info.mode = 0o644
                    tar.addfile(info, io.BytesIO(payload))
    return output_tarball, selection


def build_static_pack(
    *,
    group_file: Path,
    reference_manifest: Path,
    outdir: Path,
    target_count: int = DEFAULT_TARGET_COUNT,
    api_base: str = DEFAULT_API_BASE,
    expected_release: str = DEFAULT_RELEASE,
    expected_group_md5: str = EXPECTED_GROUP_MD5,
    source_url: str = DEFAULT_GROUP_URLS[0],
    cache_dir: Path | None = None,
    api_version_payload: object | None = None,
    protein_fetcher: Callable[
        [Sequence[str]], Mapping[str, Mapping[str, object]]
    ] | None = None,
) -> dict[str, object]:
    observed_md5 = md5_file(group_file)
    if expected_group_md5 and observed_md5 != expected_group_md5:
        raise ValueError(
            f"OMA group file MD5 mismatch: {observed_md5} != {expected_group_md5}"
        )

    with reference_manifest.open(encoding="utf-8-sig", newline="") as handle:
        refs = list(csv.DictReader(handle))
    codes = tuple(clean(row.get("oma_code")) for row in refs)
    releases = {clean(row.get("oma_release")) for row in refs}
    if codes != EXPECTED_CODES:
        raise ValueError(f"Expected reference codes {EXPECTED_CODES}, observed {codes}")
    if releases != {expected_release}:
        raise ValueError(f"Reference manifest release mismatch: {releases}")

    qualifying = list(iter_qualifying_groups(group_file, EXPECTED_CODES))
    selected = select_groups(qualifying, target_count=target_count)
    selected_ids = [omaid for group in selected for omaid in group.ref_ids]

    cache_dir = cache_dir or outdir / "api_cache"
    if api_version_payload is None:
        api_version_payload = get_api_version(
            api_base=api_base, cache_dir=cache_dir
        )
    validate_api_release(api_version_payload, expected_release)

    if protein_fetcher is None:
        protein_records = api_bulk_fetch(
            selected_ids, api_base=api_base, cache_dir=cache_dir
        )
    else:
        protein_records = dict(protein_fetcher(selected_ids))
        for omaid in selected_ids:
            if omaid not in protein_records:
                raise ValueError(f"Injected protein fetcher omitted {omaid}")
            if "_query_omaid" not in protein_records[omaid]:
                protein_records[omaid] = normalize_protein_target(
                    omaid, protein_records[omaid]
                )

    outdir.mkdir(parents=True, exist_ok=True)
    selection_path = outdir / "static_marker_selection.csv"
    export_path = outdir / "oma_static_broadconservation_marker_export.tar.gz"
    export_path, selection = build_export_tarball(
        selected, protein_records, output_tarball=export_path
    )
    write_selection(selection_path, selection)

    contract = {
        "profile_id": PROFILE_ID,
        "execution_allowed_for_contract_validation": True,
        "oma_release": expected_release,
        "reference_codes": list(EXPECTED_CODES),
        "selection_method": {
            "coverage": (
                "exactly one selected reference from each of CYNCS, HELAN, DAUCS"
            ),
            "ranking": (
                "total OMA-group membership descending, then stable SHA256 membership "
                "fingerprint, then source line"
            ),
            "target_marker_count": target_count,
            "browser_export_equivalent": False,
            "reason_not_browser_equivalent": (
                "OMA Browser documents export of the most complete groups for selected "
                "species, but its tie/ranking behavior among groups with identical "
                "selected-species coverage is not used here. This static profile "
                "deliberately ranks broader OMA-group conservation."
            ),
        },
        "group_source": {
            "url": source_url,
            "filename": group_file.name,
            "expected_md5": expected_group_md5,
            "observed_md5": observed_md5,
            "sha256": sha256_file(group_file),
            "qualifying_groups": len(qualifying),
        },
        "api": {
            "base": api_base,
            "version_payload": api_version_payload,
            "release_validation": expected_release,
            "selected_protein_records": len(selected_ids),
        },
        "outputs": {
            "selection_csv": selection_path.name,
            "export_tarball": export_path.name,
            "export_tarball_sha256": sha256_file(export_path),
        },
        "claim_limit": (
            "This pack is an independent May2026 OMA static broad-conservation marker "
            "profile for Read2Tree topology sensitivity. It is not the OMA Browser "
            "marker export, not Compositae1061, not a Chang orthogroup matrix, and not "
            "evidence of molecular regain."
        ),
    }
    (outdir / "static_marker_source_contract.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return contract


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--group-file", type=Path)
    parser.add_argument("--reference-manifest", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--target-count", type=int, default=DEFAULT_TARGET_COUNT)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--oma-release", default=DEFAULT_RELEASE)
    parser.add_argument("--group-url", action="append", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    group_file = args.group_file or (args.outdir / "source" / "oma-groups.txt.gz")
    urls = tuple(args.group_url) if args.group_url else DEFAULT_GROUP_URLS
    source_url = str(group_file)
    if not group_file.exists():
        source_url, status = download_group_file(group_file, urls=urls)
        print(f"group_file_recovery={status}")
    else:
        if md5_file(group_file) != EXPECTED_GROUP_MD5:
            raise SystemExit("Existing group file failed pinned May2026 MD5")
        source_url = "local_verified:" + str(group_file)

    contract = build_static_pack(
        group_file=group_file,
        reference_manifest=args.reference_manifest,
        outdir=args.outdir,
        target_count=args.target_count,
        api_base=args.api_base,
        expected_release=args.oma_release,
        source_url=source_url,
        cache_dir=args.cache_dir,
    )
    print(f"profile_id={contract['profile_id']}")
    print(f"oma_release={contract['oma_release']}")
    print(f"qualifying_groups={contract['group_source']['qualifying_groups']}")
    print(f"selected_markers={contract['selection_method']['target_marker_count']}")
    print(f"selected_protein_records={contract['api']['selected_protein_records']}")
    print(f"export_tarball_sha256={contract['outputs']['export_tarball_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
