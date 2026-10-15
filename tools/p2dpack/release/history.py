"""Reads release tags and commit subjects from git."""

from __future__ import annotations

import subprocess
from pathlib import Path

from p2dpack.release.version import Version


class GitHistory:
    def __init__(self, repository: Path) -> None:
        self.repository = repository

    def _git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repository), *args],
                              check=True, capture_output=True, text=True).stdout

    def latest_release(self) -> Version | None:
        """The highest ``vX.Y.Z`` tag reachable from HEAD."""
        tags = self._git("tag", "--list", "v*", "--merged", "HEAD").split()
        versions = [version for version in map(Version.parse_tag, tags) if version is not None]
        return max(versions, default=None)

    def subjects_since(self, release: Version | None) -> list[str]:
        """Subjects of every commit (merged branches included) after ``release``."""
        revision = f"{release.tag}..HEAD" if release else "HEAD"
        return [line for line in self._git("log", "--format=%s", revision).splitlines() if line]
