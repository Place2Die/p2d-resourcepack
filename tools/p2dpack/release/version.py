"""Strict semver, bumped by the highest gitmoji level since the last release."""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

from p2dpack.release.gitmoji import Bump, bump_of

TAG = re.compile(r"v(\d+)\.(\d+)\.(\d+)")


@dataclass(frozen=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def parse_tag(cls, tag: str) -> Version | None:
        match = TAG.fullmatch(tag.strip())
        return cls(*map(int, match.groups())) if match else None

    def bump(self, level: Bump) -> Version:
        if level is Bump.MAJOR:
            return Version(self.major + 1, 0, 0)
        if level is Bump.MINOR:
            return Version(self.major, self.minor + 1, 0)
        if level is Bump.PATCH:
            return Version(self.major, self.minor, self.patch + 1)
        return self

    @property
    def tag(self) -> str:
        return f"v{self}"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


INITIAL = Version(0, 0, 0)


def highest_bump(subjects: Iterable[str]) -> Bump:
    return max((bump_of(subject) for subject in subjects), default=Bump.NONE)


def next_version(latest: Version | None, subjects: Iterable[str]) -> Version | None:
    """The version to release, or ``None`` when no commit since ``latest`` calls for one.

    ``:boom:`` is a real major even in 0.x: the first breaking change gives 1.0.0.
    """
    level = highest_bump(subjects)
    if level is Bump.NONE:
        return None
    return (latest or INITIAL).bump(level)
