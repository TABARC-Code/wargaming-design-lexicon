#!/usr/bin/env python3
"""Independently verify an additive historical FAQ build without changing v522."""
import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

MASTER_SHA = "c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b"
FROZEN_SHA = "fa6fa874702627861af960e657c9893b5382ae74e11c9acb86e4f00a81e96a98"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def verify(release, master, v281, base):
    assert sha(master) == MASTER_SHA, "Master checksum changed"
    assert sha(v281) == FROZEN_SHA, "Canonical v281 checksum changed"
    m = json.loads((release / "manifest.json").read_text(encoding="utf-8"))
    assert m["master_sha256"] == MASTER_SHA, "Manifest master mismatch"
    for filename, expected in m["files_sha256"].items():
        assert sha(release / filename) == expected, filename + " checksum mismatch"

    for filename in ("terms.csv", "relationships.csv", "aliases.csv",
                     "term_sources.csv", "discoveries.csv", "candidates.csv"):
        assert sha(release / filename) == sha(base / filename), filename + " changed"

    sources, old_sources = read_csv(release / "sources.csv"), read_csv(base / "sources.csv")
    occ, old_occ = read_csv(release / "rule_occurrences.csv"), read_csv(base / "rule_occurrences.csv")
    reviews, old_reviews = read_csv(release / "review_queue.csv"), read_csv(base / "review_queue.csv")
    cross = read_csv(release / "historical_faq_crosswalks.csv")
    assert len(sources) == 819 and sources[:816] == old_sources
    assert len(occ) == 601 and occ[:575] == old_occ
    assert len(reviews) == 102 and reviews[:70] == old_reviews
    assert len(cross) == 27 and len({r["research_id"] for r in cross}) == 27
    added = occ[575:]
    assert len(added) == 26
    assert all(r["Archival class"] == "RESEARCH_HOLD_UNMAPPED"
               and not r["Canonical WG ID"] for r in added)
    assert {r["source_key"] for r in sources[816:]} == {
        "DZC-BFE-2019-FAQ", "DW-2012-FAQ13", "DW-2013-FAQ14"}
    assert sum(r["research_status"] == "SUPERSESSION_RECORDED" for r in cross) == 1
    assert sum(r["research_status"] == "HOLD_EXISTING_COMPARISON" for r in cross) == 26
    ids = {r["term_id"] for r in read_csv(release / "terms.csv")}
    assert len(ids) == 3475
    for row in cross:
        assert all(x.strip() in ids for x in row["nearest_wg_ids"].split(";"))
    with sqlite3.connect(
            "file:" + str((release / "wargaming_lexicon.sqlite").resolve()) + "?mode=ro",
            uri=True) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        for table, expected in [
            ("terms", 3475), ("sources", 819), ("relationships", 1611),
            ("aliases", 7163), ("term_sources", 3948),
            ("historical_faq_crosswalks", 27),
            ("historical_rule_occurrences", 26), ("provenance_holds", 5),
            ("historical_source_roles", 3)]:
            actual = db.execute("SELECT count(*) FROM " + table).fetchone()[0]
            assert actual == expected, (table, actual, expected)
        assert db.execute(
            "SELECT count(*) FROM research_records WHERE sheet_name='Rule Occurrences'"
        ).fetchone()[0] == 601
        assert db.execute(
            "SELECT count(*) FROM research_records WHERE sheet_name='Review Queue'"
        ).fetchone()[0] == 102
        assert db.execute(
            "SELECT count(*) FROM term_sources WHERE source_key IN "
            "('DZC-BFE-2019-FAQ','DW-2012-FAQ13','DW-2013-FAQ14')"
        ).fetchone()[0] == 0
    return {
        "result": "PASS", "canonical_wg": 3475, "sources": 819,
        "all_observations": 601, "held_unmapped_observations": 26,
        "research_crosswalks": 27, "reviews": 102,
        "v521_fresh_comparison": "not claimed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("integrated_release", type=Path)
    parser.add_argument("v522_master", type=Path)
    parser.add_argument("v281_canonical", type=Path)
    parser.add_argument("base_stage", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.integrated_release, args.v522_master,
                            args.v281_canonical, args.base_stage), indent=2))


if __name__ == "__main__":
    main()
