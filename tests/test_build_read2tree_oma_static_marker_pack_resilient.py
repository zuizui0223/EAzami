from __future__ import annotations

import importlib.util
import io
import json
import sys
import tempfile
import unittest
import urllib.error
from pathlib import Path

ANALYSIS = Path(__file__).resolve().parents[1] / "analysis"
if str(ANALYSIS) not in sys.path:
    sys.path.insert(0, str(ANALYSIS))
MODULE = ANALYSIS / "build_read2tree_oma_static_marker_pack_resilient.py"
SPEC = importlib.util.spec_from_file_location("oma_resilient", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def record(omaid: str) -> dict[str, str]:
    return {
        "omaid": omaid,
        "sequence": "MAAAAA",
        "cdna": "ATG" + "GCT" * 5,
    }


class ResilientOmaFetchTests(unittest.TestCase):
    def test_bulk_success_is_used_directly(self):
        ids = ["CYNCS00001", "HELAN00001"]

        def request(req):
            self.assertTrue(req.full_url.endswith("/protein/bulk_retrieve/"))
            return json.dumps([[omaid, record(omaid)] for omaid in ids]).encode()

        with tempfile.TemporaryDirectory() as td:
            result = mod.resilient_api_fetch(
                ids,
                api_base="https://example.invalid/api",
                cache_dir=Path(td),
                request_func=request,
                batch_size=500,
                single_workers=2,
            )
        self.assertEqual(set(result), set(ids))
        self.assertEqual(result[ids[0]]["_query_omaid"], ids[0])

    def test_http_404_bulk_falls_back_to_documented_single_endpoint(self):
        ids = ["CYNCS00001", "HELAN00001", "DAUCS00001"]
        calls = []

        def request(req):
            calls.append((req.method, req.full_url))
            if req.full_url.endswith("/protein/bulk_retrieve/"):
                raise urllib.error.HTTPError(
                    req.full_url, 404, "Not Found", {}, io.BytesIO(b"")
                )
            omaid = req.full_url.rstrip("/").rsplit("/", 1)[-1]
            return json.dumps(record(omaid)).encode()

        with tempfile.TemporaryDirectory() as td:
            cache = Path(td)
            result = mod.resilient_api_fetch(
                ids,
                api_base="https://example.invalid/api",
                cache_dir=cache,
                request_func=request,
                batch_size=500,
                single_workers=3,
            )
            self.assertTrue(all((cache / f"{omaid}.json").is_file() for omaid in ids))
        self.assertEqual(set(result), set(ids))
        self.assertEqual(sum(url.endswith("/protein/bulk_retrieve/") for _, url in calls), 1)
        individual = [url for method, url in calls if method == "GET"]
        self.assertEqual(len(individual), 3)
        self.assertTrue(all("/protein/" in url for url in individual))

    def test_cache_avoids_network(self):
        ids = ["CYNCS00001"]
        with tempfile.TemporaryDirectory() as td:
            cache = Path(td)
            cached = mod.base.normalize_protein_target(ids[0], record(ids[0]))
            mod.write_cache(cache, ids[0], cached)

            def fail(_req):
                raise AssertionError("network should not be called")

            result = mod.resilient_api_fetch(
                ids,
                api_base="https://example.invalid/api",
                cache_dir=cache,
                request_func=fail,
            )
        self.assertEqual(result[ids[0]]["_query_omaid"], ids[0])

    def test_malformed_bulk_success_is_not_silently_downgraded(self):
        ids = ["CYNCS00001"]

        def request(_req):
            return json.dumps({"unexpected": "schema"}).encode()

        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                mod.resilient_api_fetch(
                    ids,
                    api_base="https://example.invalid/api",
                    cache_dir=Path(td),
                    request_func=request,
                )


if __name__ == "__main__":
    unittest.main()
