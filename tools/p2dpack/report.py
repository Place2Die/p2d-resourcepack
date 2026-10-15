"""Collects validation and merge findings so a run reports every problem at once."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Level(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True)
class Issue:
    level: Level
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.level.value} {self.path}: {self.message}"


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def error(self, path: str, message: str) -> None:
        self.issues.append(Issue(Level.ERROR, path, message))

    def warning(self, path: str, message: str) -> None:
        self.issues.append(Issue(Level.WARNING, path, message))

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.level is Level.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.level is Level.WARNING]

    @property
    def ok(self) -> bool:
        return not self.errors

    def messages(self) -> list[str]:
        return [str(issue) for issue in sorted(self.issues, key=lambda i: (i.level.value, i.path, i.message))]
