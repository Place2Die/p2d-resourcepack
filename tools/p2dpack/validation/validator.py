"""Composition root of the validation: the default checks, run in order."""

from __future__ import annotations

from pathlib import Path

from p2dpack.report import Report
from p2dpack.validation.checks import (
    Check,
    ItemDefinitionCheck,
    JsonSyntaxCheck,
    ModelCheck,
    NamingCheck,
    PackMetaCheck,
    TextureCheck,
)
from p2dpack.validation.tree import PackTree

# Resource pack format of Minecraft Java 26.2 (minecraft.wiki "Pack format").
MINECRAFT_26_2_FORMAT = 88


class PackValidator:
    def __init__(self, checks: list[Check]) -> None:
        self.checks = checks

    @classmethod
    def default(cls, target_format: int = MINECRAFT_26_2_FORMAT) -> PackValidator:
        return cls([
            PackMetaCheck(target_format),
            JsonSyntaxCheck(),
            NamingCheck(),
            TextureCheck(),
            ItemDefinitionCheck(),
            ModelCheck(),
        ])

    def validate(self, root: Path) -> Report:
        report = Report()
        if not root.is_dir():
            report.error(str(root), "pack directory does not exist")
            return report
        tree = PackTree(root)
        for check in self.checks:
            check.run(tree, report)
        return report
