#!/usr/bin/env python3
"""Reconcile a staged CSV/SQLite release against the approved research workbook."""
import argparse
import csv
import json
import pathlib
import sqlite3
import sys

from export_master import (
    CORE_SHEETS, RESEARCH_SHEETS, TERM_COLUMNS, MasterWorkbook,
    ReleaseError, build_tables, digest, validate,
)


def csv_rows(path):
    with open(path, encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def compare(label, expected, actual, errors):
    if expected != actual:
        errors.append(f'{label}: source and output differ')


def verify(workbook, stage, approved_hash):
    errors = []
    manifest_path = stage / 'manifest.json'
    if not manifest_path.is_file():
        raise ReleaseError('Missing staged manifest')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    checksum = digest(workbook)
    if checksum != approved_hash.lower() or manifest.get('source_sha256') != checksum:
        raise ReleaseError('Workbook SHA-256 does not match approval and manifest')
    if manifest.get('release_status') != 'staged-not-published':
        raise ReleaseError('Expected an unpublished staged release')
    for filename, checksum in manifest['files_sha256'].items():
        path = stage / filename
        if not path.is_file() or digest(path) != checksum:
            errors.append(f'{filename}: missing or different checksum')

    book = MasterWorkbook(workbook)
    try:
        data = {name: book.read_sheet(name) for name in CORE_SHEETS + RESEARCH_SHEETS}
    finally:
        book.close()
    invalid, _, counts, status, aliases, links = validate(data, expected_v522=True)
    errors.extend(invalid)
    compare('count manifest', counts, manifest.get('counts'), errors)
    terms, sources, relationships, source_cols, relation_cols = build_tables(data, status, aliases, links)
    for filename, expected in [
        ('terms.csv', terms), ('sources.csv', sources),
        ('relationships.csv', relationships),
        ('aliases.csv', [dict(term_id=k, alias=v) for k, v in aliases]),
        ('term_sources.csv', [dict(term_id=k, source_key=v) for k, v in links]),
    ]:
        actual = csv_rows(stage / filename)
        compare(filename, expected, actual, errors)
    for sheet in RESEARCH_SHEETS:
        path = stage / (sheet.lower().replace(' ', '_') + '.csv')
        compare(sheet, data[sheet], csv_rows(path), errors)

    with sqlite3.connect(f'file:{(stage / "wargaming_lexicon.sqlite").resolve()}?mode=ro', uri=True) as db:
        db.execute('PRAGMA foreign_keys=ON')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            errors.append('SQLite integrity check failed')
        if db.execute('PRAGMA foreign_key_check').fetchall():
            errors.append('SQLite foreign keys invalid')
        for table, expected in [
            ('terms', len(terms)), ('sources', len(sources)),
            ('relationships', len(relationships)), ('aliases', len(aliases)),
            ('term_sources', len(links)), ('term_search', len(terms)),
            ('research_records', sum(len(data[s]) for s in RESEARCH_SHEETS)),
        ]:
            count = db.execute('SELECT count(*) FROM ' + table).fetchone()[0]
            if count != expected:
                errors.append(f'SQLite {table}: expected {expected}, found {count}')
        db.row_factory = sqlite3.Row
        actual_terms = {r['term_id']: dict(r) for r in db.execute('SELECT * FROM terms')}
        for row in terms:
            if row['term_id'] not in actual_terms:
                errors.append('SQLite missing term ' + row['term_id'])
                continue
            if any((actual_terms[row['term_id']][k] or '') != (value or '') for k, value in row.items()):
                errors.append('SQLite mismatched term ' + row['term_id'])
        compare('SQLite sources', sources, [dict(r) for r in db.execute('SELECT * FROM sources ORDER BY rowid')], errors)
        compare('SQLite relationships', relationships,
                [{k: r[k] for k in relationships[0]}
                 for r in db.execute('SELECT * FROM relationships ORDER BY relationship_id')], errors)
        compare('SQLite aliases', aliases,
                [(r['term_id'], r['alias']) for r in db.execute('SELECT term_id,alias FROM aliases ORDER BY rowid')], errors)
        compare('SQLite source links', links,
                [(r['term_id'], r['source_key']) for r in db.execute('SELECT term_id,source_key FROM term_sources ORDER BY rowid')], errors)
        expected_search = [(r['term_id'], r['canonical_term'], r['aliases'], r['category'],
                            r['subcategory'], r['definition'], r['mechanical_role'],
                            r['design_notes'], r['search_tags']) for r in terms]
        actual_search = [tuple(r) for r in db.execute('SELECT * FROM term_search ORDER BY rowid')]
        compare('SQLite full-text rows', expected_search, actual_search, errors)
        for sheet in RESEARCH_SHEETS:
            id_col = next(iter(data[sheet][0]))
            actual = {
                r['record_id']: json.loads(r['payload'])
                for r in db.execute('SELECT record_id,payload FROM research_records WHERE sheet_name=?', (sheet,))
            }
            expected = {r[id_col]: r for r in data[sheet]}
            compare('SQLite ' + sheet, expected, actual, errors)
    return errors, counts


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('workbook', type=pathlib.Path)
    parser.add_argument('stage', type=pathlib.Path)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args(argv)
    problems, counts = verify(args.workbook, args.stage, args.expected_sha256)
    if problems:
        raise ReleaseError('Staged release differs:\n' + '\n'.join(problems[:25]))
    print(json.dumps({'result': 'reconciled', 'counts': counts}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ReleaseError, OSError, sqlite3.Error, KeyError, ValueError) as exc:
        print('Reconciliation refused:', exc, file=sys.stderr)
        sys.exit(1)
