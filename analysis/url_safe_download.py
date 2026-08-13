#!/usr/bin/env python3
"""Utilities for safely requesting repository/API URLs discovered in metadata.

Public metadata occasionally exposes URL-like strings with literal spaces or
other characters rejected by ``http.client`` before a request is issued.  These
helpers percent-encode path, query and fragment components while preserving
existing ``%xx`` escapes, then wrap a module-level ``download`` callable.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit


def safe_url(url: str) -> str:
    """Return an HTTP URL safe for ``urllib`` without double-encoding `%xx`."""
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


def install_safe_download(module: Any) -> Callable[..., Any]:
    """Wrap ``module.download`` so every requested URL passes through safe_url."""
    original = module.download

    def wrapped(key: str, url: str, *args: Any, **kwargs: Any) -> Any:
        return original(key, safe_url(url), *args, **kwargs)

    module.download = wrapped
    return original
