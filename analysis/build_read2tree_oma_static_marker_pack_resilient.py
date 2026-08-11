#!/usr/bin/env python3
"""Run the May-2026 static OMA marker builder with API endpoint resilience.

OMA's documented ``POST /api/protein/bulk_retrieve/`` endpoint is preferable
because it needs only a few HTTP requests, but on 2026-08-12 the production
``omabrowser.org`` host returned HTTP 404 for that endpoint while the version
endpoint and the Browser/archive remained available.  The documented
single-protein endpoint ``GET /api/protein/{entry_id}/`` is therefore used as a
contract-preserving fallback.

This wrapper does not change marker selection, OMA release validation, sequence
validation, or output hashing in ``build_read2tree_oma_static_marker_pack.py``.
It only replaces the transport used to retrieve the already selected 1,200 OMA
protein/CDS records.  Cached records are reused across restarts.
"""
from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Mapping, Sequence

import build_read2tree_oma_static_marker_pack as base

DEFAULT_SINGLE_WORKERS = 12


def request_once(request: urllib.request.Request, timeout: int = 120) -> bytes:
    """Issue one request without retrying permanent 4xx responses."""
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def read_cached(
    query_ids: Sequence[str], cache_dir: Path
) -> tuple[dict[str, dict[str, object]], list[str]]:
    output: dict[str, dict[str, object]] = {}
    missing: list[str] = []
    cache_dir.mkdir(parents=True, exist_ok=True)
    for omaid in query_ids:
        path = cache_dir / f"{omaid}.json"
        if path.exists():
            output[omaid] = base.normalize_protein_target(
                omaid, json.loads(path.read_text(encoding="utf-8"))
            )
        else:
            missing.append(omaid)
    return output, missing


def write_cache(cache_dir: Path, omaid: str, record: Mapping[str, object]) -> None:
    (cache_dir / f"{omaid}.json").write_text(
        json.dumps(dict(record), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def try_documented_bulk(
    query_ids: Sequence[str],
    *,
    api_base: str,
    request_func: Callable[[urllib.request.Request], bytes] = request_once,
) -> dict[str, dict[str, object]] | None:
    """Try the official bulk endpoint once; return None for endpoint unavailability.

    HTTP 404/405 are treated as transport capability failures and trigger the
    documented single-record fallback.  Other network failures also fall back;
    malformed successful responses remain hard failures because silently
    accepting a changed schema would weaken provenance.
    """
    body = json.dumps(list(query_ids)).encode("utf-8")
    request = urllib.request.Request(
        api_base.rstrip("/") + "/protein/bulk_retrieve/",
        data=body,
        method="POST",
        headers={
            "User-Agent": "EAzami-OMA-static-marker-builder/1.1",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        payload = request_func(request)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        # The caller records transport mode in the source contract. The fallback
        # still validates every returned OMA ID and sequence pair downstream.
        print(f"oma_bulk_transport_unavailable={type(exc).__name__}:{exc}")
        return None
    return base.parse_bulk_response(
        query_ids, base.read_json_bytes(payload, "OMA bulk protein response")
    )


def fetch_one(
    omaid: str,
    *,
    api_base: str,
    request_func: Callable[[urllib.request.Request], bytes] = base.http_request,
) -> dict[str, object]:
    url = api_base.rstrip("/") + "/protein/" + urllib.parse.quote(omaid, safe="") + "/"
    request = urllib.request.Request(
        url,
        method="GET",
        headers={
            "User-Agent": "EAzami-OMA-static-marker-builder/1.1",
            "Accept": "application/json",
        },
    )
    payload = base.read_json_bytes(request_func(request), f"OMA protein {omaid}")
    return base.normalize_protein_target(omaid, payload)


def resilient_api_fetch(
    query_ids: Sequence[str],
    *,
    api_base: str = base.DEFAULT_API_BASE,
    cache_dir: Path | None = None,
    batch_size: int = 500,
    request_func: Callable[[urllib.request.Request], bytes] = base.http_request,
    single_workers: int = DEFAULT_SINGLE_WORKERS,
) -> dict[str, dict[str, object]]:
    """Retrieve selected OMA records with bulk -> individual documented fallback."""
    if batch_size < 1 or batch_size > 1000:
        raise ValueError("OMA bulk API batch_size must be 1..1000")
    if single_workers < 1:
        raise ValueError("single_workers must be >=1")
    cache_dir = cache_dir or Path(".oma_api_cache")
    output, missing = read_cached(query_ids, cache_dir)

    # Use a non-retrying call for the bulk capability probe in production so a
    # permanent 404 does not cost five exponential-backoff attempts per batch.
    bulk_request = request_once if request_func is base.http_request else request_func
    unresolved: list[str] = []
    for start in range(0, len(missing), batch_size):
        batch = missing[start : start + batch_size]
        parsed = try_documented_bulk(
            batch,
            api_base=api_base,
            request_func=bulk_request,
        )
        if parsed is None:
            unresolved.extend(batch)
            continue
        for omaid, record in parsed.items():
            write_cache(cache_dir, omaid, record)
            output[omaid] = record

    if unresolved:
        print(f"oma_single_record_fallback_count={len(unresolved)}")
        failures: list[str] = []
        fetched: dict[str, dict[str, object]] = {}
        with ThreadPoolExecutor(max_workers=single_workers) as pool:
            futures = {
                pool.submit(
                    fetch_one,
                    omaid,
                    api_base=api_base,
                    request_func=request_func,
                ): omaid
                for omaid in unresolved
            }
            for future in as_completed(futures):
                omaid = futures[future]
                try:
                    fetched[omaid] = future.result()
                except Exception as exc:  # preserve all failed IDs for diagnosis
                    failures.append(f"{omaid}:{type(exc).__name__}:{exc}")
        if failures:
            raise RuntimeError(
                "OMA individual-record fallback failed for "
                f"{len(failures)}/{len(unresolved)} IDs; first failures: "
                + " | ".join(sorted(failures)[:20])
            )
        for omaid in unresolved:
            record = fetched[omaid]
            write_cache(cache_dir, omaid, record)
            output[omaid] = record

    missing_after = [omaid for omaid in query_ids if omaid not in output]
    if missing_after:
        raise ValueError(
            "Missing OMA API records after resilient fetch: "
            + "|".join(missing_after[:20])
        )
    return output


def main() -> int:
    # Monkeypatch only the transport function resolved by base.build_static_pack.
    # All scientific selection/validation/output contracts remain in base.
    base.api_bulk_fetch = resilient_api_fetch
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
