"""The build pipeline: validate the sources, merge BetterModel's pack, validate the result, zip it."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from p2dpack.archive import DeterministicZip
from p2dpack.files import IGNORED_FILE_NAMES
from p2dpack.merge import MergeResult, PackMerger
from p2dpack.report import Report
from p2dpack.validation import PackValidator

ARCHIVE_NAME = "p2d-resourcepack.zip"


class BuildError(Exception):
    def __init__(self, stage: str, report: Report) -> None:
        super().__init__(f"{stage}: {len(report.errors)} error(s)")
        self.stage = stage
        self.report = report


@dataclass(frozen=True)
class BuildResult:
    archive: Path
    sha1: str
    merge: MergeResult | None
    source_report: Report
    merged_report: Report


class PackBuilder:
    def __init__(self, validator: PackValidator, merger: PackMerger, zipper: DeterministicZip) -> None:
        self.validator = validator
        self.merger = merger
        self.zipper = zipper

    @classmethod
    def default(cls) -> PackBuilder:
        return cls(PackValidator.default(), PackMerger(), DeterministicZip())

    def build(self, source: Path, output: Path, bettermodel: Path | None = None) -> BuildResult:
        source_report = self.validator.validate(source)
        if not source_report.ok:
            raise BuildError("source pack", source_report)

        staging = output / "pack"
        merge = None
        if bettermodel is not None:
            merge = self.merger.merge(source, bettermodel, staging)
        else:
            if staging.exists():
                shutil.rmtree(staging)
            shutil.copytree(source, staging, ignore=shutil.ignore_patterns(*IGNORED_FILE_NAMES))

        merged_report = self.validator.validate(staging)
        if not merged_report.ok:
            raise BuildError("merged pack", merged_report)

        archive = output / ARCHIVE_NAME
        sha1 = self.zipper.write(staging, archive)
        (output / (ARCHIVE_NAME + ".sha1")).write_text(f"{sha1}  {ARCHIVE_NAME}\n", encoding="utf-8")
        return BuildResult(archive, sha1, merge, source_report, merged_report)
