"""Check the published staging CSVs remain a consistent, unpromoted release."""
import csv
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "releases" / "staged-v522-historical-faq-20261101"
MASTER_SHA = "c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b"


def rows(path):
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


class VersionedHistoricalReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((RELEASE / "manifest.json").read_text(encoding="utf-8"))
        cls.sources = rows(RELEASE / "sources.csv")
        cls.occurrences = rows(RELEASE / "rule_occurrences.csv")
        cls.crosswalk = rows(RELEASE / "historical_faq_crosswalks.csv")
        cls.reviews = rows(RELEASE / "review_queue.csv")
        cls.roles = rows(RELEASE / "historical_source_roles.csv")
        cls.holds = rows(RELEASE / "provenance_holds.csv")

    def test_file_checksums(self):
        for name, checksum in self.manifest["file_sha256"].items():
            with self.subTest(name=name):
                self.assertEqual(sha(RELEASE / name), checksum)

    def test_release_counts(self):
        self.assertEqual(self.manifest["master_sha256"], MASTER_SHA)
        self.assertTrue(self.manifest["no_canonical_changes"])
        self.assertFalse(self.manifest["parent_v521_fresh_comparison"])
        self.assertEqual(len(self.sources), 819)
        self.assertEqual(len(self.occurrences), 601)
        self.assertEqual(len(self.crosswalk), 27)
        self.assertEqual(len(self.reviews), 102)
        self.assertEqual(len(self.roles), 3)
        self.assertEqual(len(self.holds), 5)

    def test_source_registry_and_provenance(self):
        keys = [r["source_key"] for r in self.sources]
        self.assertEqual(len(keys), len(set(keys)))
        staged = {"DZC-BFE-2019-FAQ", "DW-2012-FAQ13", "DW-2013-FAQ14"}
        self.assertTrue(staged.issubset(keys))
        self.assertEqual({r["source_key"] for r in self.roles}, staged)
        self.assertEqual(
            {r["source_key"]: r["source_role"] for r in self.roles}["DW-2012-FAQ13"],
            "OFFICIAL_PUBLISHER_FAQ_SUPERSEDED")
        self.assertEqual(
            {r["source_key"]: r["source_role"] for r in self.roles}["DW-2013-FAQ14"],
            "OFFICIAL_PUBLISHER_FAQ_SUPERSEDING")

    def test_held_occurrences_have_no_unverified_mapping(self):
        ids = [r["Occurrence ID"] for r in self.occurrences]
        self.assertEqual(len(ids), len(set(ids)))
        known_sources = {r["source_key"] for r in self.sources}
        for entry in self.occurrences:
            for key in entry["Source key"].split(";"):
                if key.strip():
                    self.assertIn(key.strip(), known_sources)
        held = [r for r in self.occurrences
                if r["Archival class"] == "RESEARCH_HOLD_UNMAPPED"]
        self.assertEqual(len(held), 26)
        self.assertTrue(all(not r["Canonical WG ID"] for r in held))
        self.assertEqual(
            {r["Source key"] for r in held},
            {"DZC-BFE-2019-FAQ", "DW-2013-FAQ14"})

    def test_supersession_and_review(self):
        states = {r["research_id"]: r["research_status"] for r in self.crosswalk}
        self.assertEqual(len(states), 27)
        self.assertEqual(sum(s == "SUPERSESSION_RECORDED"
                             for s in states.values()), 1)
        self.assertEqual(sum(s == "HOLD_EXISTING_COMPARISON"
                             for s in states.values()), 26)
        self.assertEqual(len({r["Queue reference"] for r in self.reviews}), 102)
        self.assertTrue({r["research_id"] for r in self.crosswalk}.issubset(
            {r["Queue reference"] for r in self.reviews}))


if __name__ == "__main__":
    unittest.main()
