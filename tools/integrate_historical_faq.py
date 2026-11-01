#!/usr/bin/env python3
"""Register historical publisher FAQs without guessing canonical WG equivalence.

This produces a separate research-integrated v522 release. It never overwrites
the supplied baseline or promotes a nearest-WG comparison into a proven link.
"""
import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path

MASTER_SHA = "c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b"
SOURCE_MAP = {
    "STAGE-DZC-BFE-2019-FAQ": "DZC-BFE-2019-FAQ",
    "STAGE-DW-2012-FAQ13": "DW-2012-FAQ13",
    "STAGE-DW-2013-FAQ14": "DW-2013-FAQ14",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, header, records):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(header), lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(records)


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def build(base, research, output):
    insist(not output.exists(), "Output directory already exists; nothing overwritten")
    report = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    insist(report.get("source_sha256") == MASTER_SHA, "Incorrect master baseline")
    for name, digest in report["files_sha256"].items():
        insist(sha(base / name) == digest, "Baseline checksum mismatch: " + name)

    source_rows = read_csv(base / "sources.csv")
    occurrence_rows = read_csv(base / "rule_occurrences.csv")
    review_rows = read_csv(base / "review_queue.csv")
    term_rows = read_csv(base / "terms.csv")
    crosswalks = read_csv(research / "research_crosswalk.csv")
    new_sources = read_csv(research / "staged_sources.csv")
    holds = read_csv(research / "held_provenance.csv")

    insist((len(source_rows), len(occurrence_rows), len(review_rows), len(term_rows))
           == (816, 575, 70, 3475), "Unexpected v522 baseline counts")
    insist((len(crosswalks), len(new_sources), len(holds)) == (27, 3, 5),
           "Unexpected research inventory")
    ids = {row["term_id"] for row in term_rows}
    insist(len(ids) == 3475, "Repeated WG identifier")
    source_ids = {row["source_key"] for row in source_rows}
    insist(set(SOURCE_MAP).issubset({s["staged_source_key"] for s in new_sources})
           and len({s["staged_source_key"] for s in new_sources}) == 3,
           "Unexpected staged source")
    insist(not (source_ids & set(SOURCE_MAP.values())), "Source registration already exists")
    insist(len({r["research_id"] for r in crosswalks}) == 27,
           "Repeated crosswalk identifier")

    added_sources = []
    source_roles = []
    for s in new_sources:
        key = SOURCE_MAP[s["staged_source_key"]]
        added_sources.append({
            "source_key": key, "game_system": s["game"],
            "publisher_steward": s["publisher"], "source_type": s["source_role"],
            "url": s["url"],
            "notes": s["document"] + "; " + s["document_revision"] + "; " + s["notes"],
            "legacy_supplementary": "", "additional_url": s["landing_page"],
        })
        source_roles.append({
            "source_key": key, "edition": s["edition"],
            "document_revision": s["document_revision"], "document_date": s["document_date"],
            "source_role": s["source_role"], "locally_hashed": s["locally_hashed"],
            "notes": s["notes"],
        })

    historical = []
    for i, r in enumerate(crosswalks):
        insist(r["admission"] == "NO_NEW_WG", "Unexpected canonical admission")
        insist(r["source_key_staged"] in SOURCE_MAP, "Unregistered research source")
        neighbours = [x.strip() for x in r["nearest_wg_ids"].split(";") if x.strip()]
        insist(bool(neighbours) and all(wg in ids for wg in neighbours),
               "Unregistered nearest WG identifier in " + r["research_id"])
        if r["research_status"] == "SUPERSESSION_RECORDED":
            insist(r["source_key_staged"] == "STAGE-DW-2013-FAQ14",
                   "Supersession must point to the later FAQ")
            continue
        insist(r["research_status"] == "HOLD_EXISTING_COMPARISON",
               "Unexpected historical research status")
        number = 576 + len(historical)
        historical.append({
            "Occurrence ID": "OCC-%04d" % number, "Game / System": r["game"],
            "Edition": r["period"],
            "Publication": r["document"] + " [" + r["document_revision"] + "]",
            "Publication date": r["document_date"],
            "Publisher / Designer": "TTCombat" if r["game"].startswith("Dropzone")
                                     else "Fantasy Flight Games",
            "Genre": "Science-fiction miniature wargame",
            "Period / setting": r["period"],
            "Page / section": "FAQ p. " + r["pdf_page_1_based"],
            "Original rule keyword": "",
            "Canonical WG ID": "",
            "Archival class": "RESEARCH_HOLD_UNMAPPED",
            "Paraphrased rule context": r["paraphrased_mechanic"],
            "Source key": SOURCE_MAP[r["source_key_staged"]],
            "Source URL": r["official_source_url"],
        })

    insist(len(historical) == 26, "Expected 26 research observations")
    added_reviews = []
    for r in crosswalks:
        added_reviews.append({
            "Queue reference": r["research_id"],
            "Reason": "Publisher FAQ candidate comparison" if r["research_status"]
                      == "HOLD_EXISTING_COMPARISON" else "Superseding FAQ correction",
            "Required action": r["next_check"] + " " + r["official_source_url"],
            "Confidence": "", "Priority": "Medium", "Status": "OPEN",
            "Entry type": "HISTORICAL_RESEARCH", "Registered candidate": "NO",
        })
    for r in holds:
        added_reviews.append({
            "Queue reference": r["ref"], "Reason": r["issue"],
            "Required action": r["safe_action"] + " " + r["finding"],
            "Confidence": "", "Priority": r["priority"], "Status": "OPEN",
            "Entry type": "PROVENANCE_HOLD", "Registered candidate": "NO",
        })
    insist(len(added_reviews) == 32, "Review count mismatch")
    all_sources = source_rows + added_sources
    all_occurrences = occurrence_rows + historical

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".historical-", dir=output.parent) as folder:
        stage = Path(folder)
        for f in base.iterdir():
            if f.is_file() and f.name != "manifest.json":
                shutil.copy2(f, stage / f.name)

        write_csv(stage / "sources.csv", source_rows[0], all_sources)
        write_csv(stage / "rule_occurrences.csv", occurrence_rows[0], all_occurrences)
        write_csv(stage / "review_queue.csv", review_rows[0], review_rows + added_reviews)
        write_csv(stage / "historical_faq_crosswalks.csv", crosswalks[0], crosswalks)
        write_csv(stage / "historical_source_roles.csv", source_roles[0], source_roles)
        write_csv(stage / "provenance_holds.csv", holds[0], holds)

        with sqlite3.connect(stage / "wargaming_lexicon.sqlite") as db:
            db.execute("PRAGMA foreign_keys=ON")
            for row in added_sources:
                db.execute("INSERT INTO sources VALUES (?,?,?,?,?,?,?,?)",
                           tuple(row.values()))
            db.executescript("""
                CREATE TABLE historical_faq_crosswalks (
                  research_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                  registered_source_key TEXT NOT NULL REFERENCES sources(source_key));
                CREATE TABLE historical_source_roles (
                  source_key TEXT PRIMARY KEY REFERENCES sources(source_key),
                  edition TEXT, revision TEXT, document_date TEXT,
                  source_role TEXT, locally_hashed TEXT, notes TEXT);
                CREATE TABLE historical_nearest_wg (
                  research_id TEXT NOT NULL REFERENCES historical_faq_crosswalks(research_id),
                  term_id TEXT NOT NULL REFERENCES terms(term_id),
                  mapping_status TEXT NOT NULL CHECK(mapping_status='NEAREST_ONLY'),
                  PRIMARY KEY(research_id,term_id));
                CREATE TABLE historical_rule_occurrences (
                  occurrence_id TEXT PRIMARY KEY,
                  research_id TEXT NOT NULL REFERENCES historical_faq_crosswalks(research_id),
                  source_key TEXT NOT NULL REFERENCES sources(source_key),
                  canonical_term_id TEXT,
                  archival_class TEXT NOT NULL CHECK(archival_class='RESEARCH_HOLD_UNMAPPED'));
                CREATE TABLE provenance_holds (ref TEXT PRIMARY KEY, payload TEXT NOT NULL);
            """)
            for role in source_roles:
                db.execute("INSERT INTO historical_source_roles VALUES (?,?,?,?,?,?,?)",
                           (role["source_key"], role["edition"], role["document_revision"],
                            role["document_date"], role["source_role"], role["locally_hashed"],
                            role["notes"]))
            for row in crosswalks:
                key = SOURCE_MAP[row["source_key_staged"]]
                db.execute("INSERT INTO historical_faq_crosswalks VALUES (?,?,?)",
                           (row["research_id"], json.dumps(row, sort_keys=True), key))
                for term_id in [x.strip() for x in row["nearest_wg_ids"].split(";") if x.strip()]:
                    db.execute("INSERT INTO historical_nearest_wg VALUES (?,?,?)",
                               (row["research_id"], term_id, "NEAREST_ONLY"))
            for row in holds:
                db.execute("INSERT INTO provenance_holds VALUES (?,?)",
                           (row["ref"], json.dumps(row, sort_keys=True)))
            for row in historical:
                matched = [c for c in crosswalks if c["paraphrased_mechanic"]
                           == row["Paraphrased rule context"] and
                           SOURCE_MAP[c["source_key_staged"]] == row["Source key"]]
                insist(len(matched) == 1, "Ambiguous historical occurrence")
                db.execute("INSERT INTO historical_rule_occurrences VALUES (?,?,?,?,?)",
                           (row["Occurrence ID"], matched[0]["research_id"],
                            row["Source key"], None, row["Archival class"]))
                db.execute("INSERT INTO research_records VALUES (?,?,?)",
                           ("Rule Occurrences", row["Occurrence ID"],
                            json.dumps(row, sort_keys=True, ensure_ascii=False)))
            for row in added_reviews:
                db.execute("INSERT INTO research_records VALUES (?,?,?)",
                           ("Review Queue", row["Queue reference"],
                            json.dumps(row, sort_keys=True, ensure_ascii=False)))
            insist(db.execute("PRAGMA integrity_check").fetchone()[0] == "ok",
                   "SQLite integrity failure")
            insist(not db.execute("PRAGMA foreign_key_check").fetchall(),
                   "Foreign key failure")
            insist(db.execute("SELECT count(*) FROM terms").fetchone()[0] == 3475,
                   "Canonical term count changed")
            insist(db.execute("SELECT count(*) FROM sources").fetchone()[0] == 819,
                   "Source count mismatch")
            insist(db.execute("SELECT count(*) FROM historical_rule_occurrences").fetchone()[0] == 26,
                   "Historical occurrence count mismatch")
            db.commit()

        for name in ("terms.csv", "term_sources.csv", "relationships.csv", "aliases.csv",
                     "discoveries.csv", "candidates.csv"):
            insist(sha(stage / name) == sha(base / name),
                   "Canonical file changed: " + name)
        manifest = {
            "status": "research-integrated; canonical master unchanged",
            "master_version": "v522", "master_sha256": MASTER_SHA,
            "v521_fresh_comparison": "unavailable",
            "canonical_terms": 3475, "registered_sources": 819,
            "source_occurrences_total": 601, "original_occurrences": 575,
            "historical_unmapped_occurrences": 26, "historical_crosswalks": 27,
            "relationships": 1611, "canonical_source_links_added": 0,
            "review_queue": 102,
            "files_sha256": {
                f.name: sha(f) for f in sorted(stage.iterdir()) if f.is_file()
            },
        }
        (stage / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        stage.rename(output)
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("base_stage", type=Path)
    p.add_argument("research_directory", type=Path)
    p.add_argument("output_directory", type=Path)
    args = p.parse_args()
    print(json.dumps(build(args.base_stage, args.research_directory,
                           args.output_directory), indent=2))


if __name__ == "__main__":
    main()
