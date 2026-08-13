#!/usr/bin/env python3
"""Run the first-pass Compositae1061 audit with URL-safe requests.

The discovery layer intentionally records broad URL-like candidates from public
JSON/HTML metadata. Some non-URL strings can therefore be joined to a repository
base URL and contain literal spaces. This CLI wrapper percent-encodes every
request before delegating all candidate, FASTA and provenance logic to
``recover_compositae1061_target.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import recover_compositae1061_target as audit
from url_safe_download import install_safe_download as _install_safe_download
from url_safe_download import safe_url


def install_safe_download() -> Callable[..., Any]:
    """Patch the base audit downloader and return the original callable."""
    return _install_safe_download(audit)


def main() -> int:
    install_safe_download()
    return audit.main()


if __name__ == "__main__":
    raise SystemExit(main())
