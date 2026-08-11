#!/usr/bin/env python3
"""Run the expanded Compositae1061 audit with URL-safe repository requests.

GitHub code search can return contents-API URLs whose path contains literal
spaces.  ``http.client`` rejects those URLs before an HTTP request is made.  This
thin CLI wrapper percent-encodes path and query components, while preserving
existing percent escapes, then delegates all biological and provenance logic to
``recover_compositae1061_target_expanded.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import recover_compositae1061_target_expanded as expanded


def safe_url(url: str) -> str:
    """Percent-encode spaces/control characters without double-encoding `%xx`."""
    parts = urlsplit(url)
    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            quote(parts.path, safe="/%:@"),
            quote(parts.query, safe="=&?/:;+,%@[]"),
            quote(parts.fragment, safe="=&?/:;+,%@[]"),
        )
    )


def install_safe_download() -> Callable[..., Any]:
    """Patch the shared downloader and return the original callable."""
    original = expanded.base.download

    def wrapped(key: str, url: str, *args: Any, **kwargs: Any) -> Any:
        return original(key, safe_url(url), *args, **kwargs)

    expanded.base.download = wrapped
    return original


def main() -> int:
    install_safe_download()
    return expanded.main()


if __name__ == "__main__":
    raise SystemExit(main())
