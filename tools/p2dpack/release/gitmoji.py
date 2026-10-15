"""The semver level of each gitmoji (``references/gitmoji.md`` of the place2die skill).

Gitmojis not listed here (``:tada:``, ``:recycle:``, ``:memo:``, ``:white_check_mark:``,
``:construction_worker:``...) do not trigger a release.
"""

from __future__ import annotations

import re
from enum import IntEnum


class Bump(IntEnum):
    NONE = 0
    PATCH = 1
    MINOR = 2
    MAJOR = 3


SHORTCODE_BUMPS: dict[str, Bump] = {
    "boom": Bump.MAJOR,
    "sparkles": Bump.MINOR,
    **{code: Bump.PATCH for code in (
        "zap", "bug", "ambulance", "lipstick", "lock", "arrow_down", "arrow_up", "pushpin",
        "chart_with_upwards_trend", "heavy_plus_sign", "heavy_minus_sign", "wrench",
        "globe_with_meridians", "pencil2", "rewind", "package", "alien", "bento", "wheelchair",
        "speech_balloon", "card_file_box", "children_crossing", "iphone", "egg", "alembic", "mag",
        "label", "triangular_flag_on_post", "goal_net", "dizzy", "wastebasket", "passport_control",
        "adhesive_bandage", "necktie",
    )},
}

# Commits should use shortcodes, but GitHub's own merge commits and hand-typed ones may use
# the emoji: map the release-relevant ones (without the U+FE0F variation selector).
EMOJI_SHORTCODES: dict[str, str] = {
    "💥": "boom", "✨": "sparkles", "⚡": "zap", "🐛": "bug", "🚑": "ambulance", "💄": "lipstick",
    "🔒": "lock", "⬇": "arrow_down", "⬆": "arrow_up", "📌": "pushpin", "📈": "chart_with_upwards_trend",
    "➕": "heavy_plus_sign", "➖": "heavy_minus_sign", "🔧": "wrench", "🌐": "globe_with_meridians",
    "✏": "pencil2", "⏪": "rewind", "📦": "package", "👽": "alien", "🍱": "bento", "♿": "wheelchair",
    "💬": "speech_balloon", "🗃": "card_file_box", "🚸": "children_crossing", "📱": "iphone",
    "🥚": "egg", "⚗": "alembic", "🔍": "mag", "🏷": "label", "🚩": "triangular_flag_on_post",
    "🥅": "goal_net", "💫": "dizzy", "🗑": "wastebasket", "🛂": "passport_control",
    "🩹": "adhesive_bandage", "👔": "necktie",
}

SHORTCODE = re.compile(r":([a-z0-9_+-]+):")


def bump_of(subject: str) -> Bump:
    """The semver level of one commit subject, read from its leading gitmoji."""
    subject = subject.strip()
    match = SHORTCODE.match(subject)
    if match:
        return SHORTCODE_BUMPS.get(match.group(1), Bump.NONE)
    for emoji, code in EMOJI_SHORTCODES.items():
        if subject.startswith(emoji):
            return SHORTCODE_BUMPS[code]
    return Bump.NONE
