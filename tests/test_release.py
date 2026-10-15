import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from p2dpack.release import Bump, GitHistory, Version, bump_of, next_version


class GitmojiTest(unittest.TestCase):
    def test_shortcodes(self):
        self.assertEqual(Bump.MAJOR, bump_of(":boom: (pack) Rename the survival namespace PERSO-90"))
        self.assertEqual(Bump.MINOR, bump_of(":sparkles: Add the walker model PERSO-83"))
        self.assertEqual(Bump.PATCH, bump_of(":bento: Replace the canteen texture PERSO-83"))
        self.assertEqual(Bump.PATCH, bump_of(":bug: Fix the bandage model PERSO-1"))

    def test_gitmojis_without_a_release(self):
        for subject in (":tada: Bootstrap", ":memo: Docs", ":construction_worker: CI", ":recycle: Refactor",
                        ":white_check_mark: Tests", ":hammer: Script"):
            self.assertEqual(Bump.NONE, bump_of(subject), subject)

    def test_unicode_emojis(self):
        self.assertEqual(Bump.MINOR, bump_of("✨ Add a feature"))
        self.assertEqual(Bump.PATCH, bump_of("🔧️ Tweak config"))
        self.assertEqual(Bump.NONE, bump_of("🔀 Merge pull request #1 from Place2Die/hermes/perso-81"))

    def test_no_gitmoji(self):
        self.assertEqual(Bump.NONE, bump_of("feat: conventional commit"))
        self.assertEqual(Bump.NONE, bump_of(":unknown: whatever"))


class VersionTest(unittest.TestCase):
    def test_first_release_starts_from_zero(self):
        self.assertEqual(Version(0, 1, 0), next_version(None, [":tada: Init", ":sparkles: Feature"]))
        self.assertEqual(Version(0, 0, 1), next_version(None, [":bento: Assets"]))

    def test_the_highest_bump_wins(self):
        latest = Version(0, 3, 2)
        self.assertEqual(Version(0, 3, 3), next_version(latest, [":bug: a", ":memo: b"]))
        self.assertEqual(Version(0, 4, 0), next_version(latest, [":bug: a", ":sparkles: b"]))

    def test_boom_is_a_real_major_even_in_0x(self):
        self.assertEqual(Version(1, 0, 0), next_version(Version(0, 9, 4), [":sparkles: a", ":boom: b"]))

    def test_no_release_without_a_releasing_gitmoji(self):
        self.assertIsNone(next_version(Version(1, 2, 3), [":memo: Docs", ":construction_worker: CI"]))
        self.assertIsNone(next_version(Version(1, 2, 3), []))

    def test_tags(self):
        self.assertEqual(Version(1, 10, 2), Version.parse_tag("v1.10.2"))
        self.assertIsNone(Version.parse_tag("v1.2"))
        self.assertIsNone(Version.parse_tag("release-3"))
        self.assertEqual("v1.10.2", Version(1, 10, 2).tag)
        self.assertLess(Version(1, 9, 0), Version(1, 10, 0))


class GitHistoryTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.repo = Path(directory.name)
        self.env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                    "GIT_COMMITTER_EMAIL": "t@t", "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", "-b", "main")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True, env=self.env)

    def commit(self, subject):
        self.git("commit", "-q", "--allow-empty", "-m", subject)

    def test_reads_subjects_since_the_highest_tag(self):
        self.commit(":tada: Init")
        self.commit(":sparkles: First")
        self.git("tag", "v0.1.0")
        self.commit(":bug: Fix")
        self.git("tag", "v0.1.1")
        self.git("tag", "not-a-version")
        self.commit(":bento: Art")
        self.commit(":memo: Docs")
        history = GitHistory(self.repo)
        latest = history.latest_release()
        self.assertEqual(Version(0, 1, 1), latest)
        subjects = history.subjects_since(latest)
        self.assertEqual([":memo: Docs", ":bento: Art"], subjects)
        self.assertEqual(Version(0, 1, 2), next_version(latest, subjects))

    def test_without_tags_every_commit_counts(self):
        self.commit(":tada: Init")
        self.commit(":sparkles: First")
        history = GitHistory(self.repo)
        self.assertIsNone(history.latest_release())
        self.assertEqual(2, len(history.subjects_since(None)))


if __name__ == "__main__":
    unittest.main()
