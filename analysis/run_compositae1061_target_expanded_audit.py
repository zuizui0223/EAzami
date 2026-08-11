#!/usr/bin/env python3
"""Run the expanded Compositae1061 audit with URL-safe repository requests.

GitHub code search can return contents-API URLs whose path contains literal
spaces. ``http.client`` rejects those URLs before an HTTP request is made. This
thin CLI wrapper installs the shared URL-safe downloader, then delegates all
biological and provenance logic to
``recover_compositae1061_target_expanded.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import recover_compositae1061_target_expanded as expanded
from url_safe_download import install_safe_download as _install_safe_download
from url_safe_download import safe_url


def install_safe_download() -> Callable[..., Any]:
    """Patch the expanded audit's shared downloader and return the original."""
    return _install_safe_download(expanded.base)


def main() -> int:
    install_safe_download()
    return expanded.main()


if __name__ == "__main__":
    raise SystemExit(main())
