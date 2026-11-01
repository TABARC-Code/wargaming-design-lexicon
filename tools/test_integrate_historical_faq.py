"""Synthetic end-to-end check for the optional historical research integration."""
import csv
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from integrate_historical_faq import build, sha, MASTER_SHA, SOURCE_MAP


def write(path, header, records):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(records)


class HistoricalIntegrationTests(unittest.TestCase):
    def fixture(self, root):
        base, research = root / "base", root / "research"
        base.mkdir()
        research.mkdir()
        term_keys = ["term_id"]
        source_keys = ["source_key", "game_system", "publisher_steward", "source_type",
                       "url", "notes", "legacy_supplementary", "additional_url"]
        occurrence_keys = ["Occurrence ID", "Game / System", "Edition", "Publication",
                           "Publication date", "Publisher / Designer", "Genre",
                           "Period / setting", "Page / section", "Original rule keyword",
                           "Canonical WG ID", "Archival class",
                           "Paraphrased rule context", "Source key", "Source URL"]
        review_keys = ["Queue reference", "Reason", "Required action", "Confidence",
                       "Priority", "Status", "Entry type", "Registered candidate"]
        write(base / "terms.csv", term_keys,
              [{"term_id": f"WG-{i:04}"} for i in range(1, 3476)])
        write(base / "sources.csv", source_keys, [
            {"source_key": f"SRC-{i:04}"} for i in range(816)])
        write(base / "rule_occurrences.csv", occurrence_keys, [
            {"Occurrence ID": f"OCC-{i:04}", "Source key": "SRC-0000",
             "Canonical WG ID": "WG-0001"} for i in range(1, 576)])
        write(base / "review_queue.csv", review_keys, [
            {"Queue reference": f"REVIEW-{i}"} for i in range(70)])
        for filename in ["aliases.csv", "relationships.csv", "term_sources.csv",
                         "discoveries.csv", "candidates.csv"]:
            (base / filename).write_text("", encoding="utf-8")
        with sqlite3.connect(base / "wargaming_lexicon.sqlite") as db:
            db.executescript("""
              CREATE TABLE terms(term_id TEXT PRIMARY KEY);
              CREATE TABLE sources(source_key TEXT PRIMARY KEY, game_system TEXT,
                publisher_steward TEXT, source_type TEXT, url TEXT, notes TEXT,
                legacy_supplementary TEXT, additional_url TEXT);
              CREATE TABLE research_records (
                sheet_name TEXT NOT NULL, record_id TEXT NOT NULL,
                payload TEXT NOT NULL, PRIMARY KEY(sheet_name, record_id));
            """)
            db.executemany("INSERT INTO terms VALUES (?)",
                           [(f"WG-{i:04}",) for i in range(1, 3476)])
            db.executemany("INSERT INTO sources(source_key) VALUES (?)",
                           [(f"SRC-{i:04}",) for i in range(816)])
            for i in range(1, 576):
                db.execute("INSERT INTO research_records VALUES (?,?,?)",
                           ("Rule Occurrences", f"OCC-{i:04}", "{}"))
            for i in range(70):
                db.execute("INSERT INTO research_records VALUES (?,?,?)",
                           ("Review Queue", f"REVIEW-{i}", "{}"))
        (base / "manifest.json").write_text(json.dumps({
            "source_sha256": MASTER_SHA,
            "files_sha256": {
                f.name: sha(f) for f in base.iterdir() if f.is_file()
            },
        }), encoding="utf-8")
        source_header = ["staged_source_key", "game", "publisher", "document",
                         "edition", "document_revision", "document_date",
                         "source_role", "url", "landing_page", "pdf_pages",
                         "locally_hashed", "admission", "notes"]
        write(research / "staged_sources.csv", source_header, [
            {"staged_source_key": key, "game": key, "publisher": "Publisher",
             "source_role": "OFFICIAL_HISTORICAL_FAQ", "url": "https://example.org/" + key}
            for key in SOURCE_MAP])
        cross_header = ["research_id", "game", "period", "document",
                        "document_revision", "document_date", "topic",
                        "paraphrased_mechanic", "pdf_page_1_based",
                        "nearest_wg_ids", "assessment", "research_status",
                        "source_key_staged", "official_source_url", "source_role",
                        "existing_wg_valid", "in_v522_research_tables",
                        "admission", "next_check"]
        staged = list(SOURCE_MAP)
        cross = []
        for i in range(27):
            final = i == 26
            cross.append({
                "research_id": f"RES-{i:02}",
                "game": "Dust Warfare" if final else "Dropzone",
                "paraphrased_mechanic": f"Historical paraphrase {i}",
                "nearest_wg_ids": "WG-0001; WG-0002",
                "source_key_staged": staged[2 if final else 0],
                "research_status": "SUPERSESSION_RECORDED" if final
                                   else "HOLD_EXISTING_COMPARISON",
                "admission": "NO_NEW_WG",
                "official_source_url": "https://example.org/doc",
                "pdf_page_1_based": "2",
            })
        write(research / "research_crosswalk.csv", cross_header, cross)
        hold_keys = ["ref", "issue", "current_source_key", "existing_primary_url",
                     "finding", "priority", "status", "safe_action"]
        write(research / "held_provenance.csv", hold_keys, [
            {"ref": f"HOLD-{i}", "issue": "Source review",
             "priority": "Medium", "status": "OPEN"} for i in range(5)])
        return base, research

    def test_integration_preserves_canonical_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base, research = self.fixture(root)
            output = root / "release"
            result = build(base, research, output)
            self.assertEqual(result["canonical_terms"], 3475)
            self.assertEqual(result["registered_sources"], 819)
            self.assertEqual(result["historical_unmapped_occurrences"], 26)
            with sqlite3.connect(output / "wargaming_lexicon.sqlite") as db:
                self.assertEqual(db.execute(
                    "SELECT count(*) FROM historical_faq_crosswalks").fetchone()[0], 27)
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(db.execute(
                    "SELECT count(*) FROM historical_nearest_wg").fetchone()[0], 54)
            self.assertEqual(sha(base / "terms.csv"), sha(output / "terms.csv"))
            with self.assertRaises(ValueError):
                build(base, research, output)

    def test_unknown_nearest_wg_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base, research = self.fixture(root)
            cross = list(csv.DictReader(
                (research / "research_crosswalk.csv").open(newline="", encoding="utf-8")))
            cross[0]["nearest_wg_ids"] = "WG-9999"
            write(research / "research_crosswalk.csv", list(cross[0]), cross)
            with self.assertRaises(ValueError):
                build(base, research, root / "release")


if __name__ == "__main__":
    unittest.main()
