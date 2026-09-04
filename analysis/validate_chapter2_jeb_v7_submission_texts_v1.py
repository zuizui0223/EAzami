#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CH = ROOT / "docs" / "chapter2"
COVER = CH / "JEB_COVER_LETTER_TEMPLATE_V3.md"
TITLE = CH / "JEB_V7_TITLE_PAGE_WORKING.md"


def require(text: str, *tokens: str) -> None:
    missing = [x for x in tokens if x not in text]
    if missing:
        raise AssertionError(f"missing required submission tokens: {missing}")


def forbid(text: str, *tokens: str) -> None:
    bad = [x for x in tokens if x.lower() in text.lower()]
    if bad:
        raise AssertionError(f"stale/forbidden submission tokens present: {bad}")


def main() -> None:
    cover = COVER.read_text(encoding="utf-8")
    title = TITLE.read_text(encoding="utf-8")

    require(
        cover,
        "Repeated mosaic assembly at unequal evolutionary depths in a young thistle radiation",
        "16/792",
        "4/126",
        "3/126",
        "10/56",
        "99/376",
        "composite transition–niche correspondence",
        "historical origin-regime non-persistence",
        "finite exhaustive ranks",
        "Internal-edge environmental values remain reconstructions from present-day taxon niche centroids",
    )
    forbid(
        cover,
        "BIO15 causes orientation",
        "BIO1 causes orientation",
        "precipitation seasonality caused orientation",
        "temperature caused orientation",
        "proves adaptation",
        "proves selection",
    )

    require(
        title,
        "**6,944 words** (<7,500)",
        "**231 words** (<250)",
        "keywords: **7**",
        "workflow run `33867953835`",
        "Orientation transitions track a bidirectional East-Asian present-niche regime",
        "only calendarized origin event",
    )
    forbid(title, "5,811 words", "229 words")

    marker = "> Three thistle capitulum traits were mosaically assembled at unequal evolutionary depths. Orientation transitions track a bidirectional East-Asian present-niche regime, yet that regime is not supported at the only calendarized origin event."
    require(title, marker)
    social = marker[2:]
    if len(social) > 280:
        raise AssertionError(f"social-media abstract exceeds 280 characters: {len(social)}")
    if len(social) != 239:
        raise AssertionError(f"social-media abstract length drifted: {len(social)}")

    print({
        "status": "ok",
        "main_text_words": 6944,
        "abstract_words": 231,
        "keywords": 7,
        "social_media_characters": len(social),
        "transition_regime_synced": True,
        "origin_regime_non_persistence_synced": True,
    })


if __name__ == "__main__":
    main()
