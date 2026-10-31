#!/usr/bin/env python3
"""Read a research master, verify its links, and build a separate SQLite/CSV release.

I keep the input read-only. Staging is intentional: old releases do not vanish because
someone has found a newer workbook.
"""

import argparse
import csv
import hashlib
import json
import pathlib
import posixpath
import re
import sqlite3
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter

XML = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
REL = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
WG_ID = re.compile(r'WG-\d{4}\Z')
REDIRECT = re.compile(r'LEGACY_DUPLICATE\s*->\s*(WG-\d{4})\Z')
CORE_SHEETS = ('Lexicon', 'Sources', 'Relationships', 'Canonical View')
RESEARCH_SHEETS = ('Rule Occurrences', 'Discoveries', 'Candidates', 'Review Queue')
RELEASE_COUNTS_V522 = {
    'terms': 3475, 'sources': 816, 'relationships': 1611,
    'occurrences': 575, 'discoveries': 616, 'candidates': 514,
    'active': 3472, 'redirects': 3,
}
TERM_COLUMNS = (
    'term_id', 'canonical_term', 'category', 'subcategory', 'definition',
    'mechanical_role', 'typical_value_unit', 'design_notes', 'scope', 'added',
    'search_tags', 'aliases', 'example_systems', 'source_keys',
    'primary_source_url', 'additional_source_urls', 'status', 'redirect_target',
)


class ReleaseError(ValueError):
    pass


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def tokens(text):
    """The research master uses semicolons for aliases and source keys."""
    return [part.strip() for part in (text or '').split(';') if part.strip()]


def col_index(address):
    letters = re.match(r'[A-Z]+', address)
    if not letters:
        raise ReleaseError(f'Bad cell address: {address}')
    n = 0
    for char in letters.group():
        n = n * 26 + ord(char) - ord('A') + 1
    return n - 1


class MasterWorkbook:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        workbook = ET.fromstring(self.z.read('xl/workbook.xml'))
        links = ET.fromstring(self.z.read('xl/_rels/workbook.xml.rels'))
        targets = {r.attrib['Id']: r.attrib['Target'] for r in links}
        self.sheets = {}
        for sheet in workbook.findall('.//' + XML + 'sheet'):
            rid = sheet.attrib[REL + 'id']
            target = targets[rid]
            path = (target.lstrip('/') if target.startswith('/')
                    else posixpath.normpath(posixpath.join('xl', target)))
            if not path.startswith('xl/worksheets/') or '..' in path.split('/'):
                raise ReleaseError('Unexpected sheet location: ' + path)
            self.sheets[sheet.attrib['name']] = path
        self.strings = []
        if 'xl/sharedStrings.xml' in self.z.namelist():
            shared = ET.fromstring(self.z.read('xl/sharedStrings.xml'))
            self.strings = [
                ''.join(t.text or '' for t in node.iter(XML + 't'))
                for node in shared.findall(XML + 'si')
            ]

    def read_sheet(self, name):
        if name not in self.sheets:
            raise ReleaseError('Missing required worksheet: ' + name)
        records = []
        header = None
        formulas = 0
        with self.z.open(self.sheets[name]) as stream:
            for _, node in ET.iterparse(stream, events=('end',)):
                if node.tag != XML + 'row':
                    continue
                fields = {}
                for cell in node.findall(XML + 'c'):
                    if cell.find(XML + 'f') is not None:
                        formulas += 1
                    value = cell.find(XML + 'v')
                    raw = '' if value is None or value.text is None else value.text
                    if cell.get('t') == 's' and raw:
                        raw = self.strings[int(raw)]
                    elif cell.get('t') == 'inlineStr':
                        raw = ''.join(t.text or '' for t in cell.iter(XML + 't'))
                    fields[col_index(cell.attrib['r'])] = raw
                if fields:
                    width = max(fields) + 1
                    row = [fields.get(i, '') for i in range(width)]
                    if header is None:
                        header = row
                        if len(set(header)) != len(header):
                            raise ReleaseError(f'Duplicate headers in {name}')
                    else:
                        records.append({key: fields.get(i, '') for i, key in enumerate(header)})
                node.clear()
        if header is None:
            raise ReleaseError('Empty worksheet: ' + name)
        if formulas:
            raise ReleaseError(f'{name} contains {formulas} formula cells: cannot export cached values safely')
        return records

    def close(self):
        self.z.close()


def required(records, names, sheet):
    if not records:
        raise ReleaseError('No records in ' + sheet)
    missing = set(names) - set(records[0])
    if missing:
        raise ReleaseError(f'{sheet}: missing column(s) {sorted(missing)}')


def validate(data, expected_v522=False):
    errors, warnings = [], []
    lex, source, rel, canonical = (data[name] for name in CORE_SHEETS)
    required(lex, ('ID', 'Term', 'Plain-English meaning', 'Source keys'), 'Lexicon')
    required(source, ('Key', 'System', 'URL'), 'Sources')
    required(rel, ('Source ID', 'Relationship', 'Target ID'), 'Relationships')
    required(canonical, ('WG ID', 'Status'), 'Canonical View')

    ids = [r['ID'].strip() for r in lex]
    source_keys = [r['Key'].strip() for r in source]
    status_ids = [r['WG ID'].strip() for r in canonical]
    for label, values in [('WG ID', ids), ('source key', source_keys), ('canonical ID', status_ids)]:
        for value, count in Counter(values).items():
            if not value or count != 1:
                errors.append(f'{label} {value!r} occurs {count} times')
    for value in ids:
        if not WG_ID.fullmatch(value):
            errors.append(f'Invalid WG ID: {value}')
    if set(ids) != set(status_ids):
        errors.append('Canonical View IDs differ from Lexicon IDs')
    known_ids, known_sources = set(ids), set(source_keys)
    status = {}
    for row in canonical:
        value = row['Status'].strip()
        match = REDIRECT.fullmatch(value)
        if value != 'ACTIVE' and not match:
            errors.append(f'Unknown canonical status {row["WG ID"]}: {value!r}')
        if match:
            status[row['WG ID']] = ('REDIRECT', match.group(1))
        else:
            status[row['WG ID']] = ('ACTIVE', '')
    for item, (state, target) in status.items():
        if state == 'REDIRECT' and (target not in known_ids or status.get(target) != ('ACTIVE', '')):
            errors.append(f'Invalid redirect {item} -> {target}')

    self_aliases = 0
    term_links = []
    alias_rows = []
    for row in lex:
        term_id = row['ID'].strip()
        term = row['Term'].strip()
        if not term or not row['Plain-English meaning'].strip():
            errors.append(f'{term_id}: blank term or definition')
        observed = set()
        for alias in tokens(row.get('Aliases / Related labels', '')):
            normalized = alias.casefold()
            if normalized in observed:
                warnings.append(f'{term_id}: repeated alias {alias!r}')
                continue
            observed.add(normalized)
            alias_rows.append((term_id, alias))
            if normalized == term.casefold():
                self_aliases += 1
        observed = set()
        for key in tokens(row['Source keys']):
            if key not in known_sources:
                errors.append(f'{term_id}: unregistered source {key}')
            if key not in observed:
                term_links.append((term_id, key))
                observed.add(key)
    rel_keys = set()
    for row in rel:
        triple = (row['Source ID'].strip(), row['Relationship'].strip(), row['Target ID'].strip())
        if not triple[1] or triple[0] not in known_ids or triple[2] not in known_ids:
            errors.append(f'Invalid relationship {triple}')
        if triple in rel_keys:
            errors.append(f'Duplicate relationship {triple}')
        rel_keys.add(triple)

    metrics = {
        'terms': len(lex), 'active': sum(v[0] == 'ACTIVE' for v in status.values()),
        'redirects': sum(v[0] == 'REDIRECT' for v in status.values()),
        'sources': len(source), 'relationships': len(rel),
        'occurrences': len(data['Rule Occurrences']),
        'discoveries': len(data['Discoveries']),
        'candidates': len(data['Candidates']),
        'review_queue': len(data['Review Queue']),
        'aliases': len(alias_rows), 'term_source_links': len(term_links),
        'self_aliases': self_aliases,
    }
    if expected_v522:
        for key, expected in RELEASE_COUNTS_V522.items():
            if metrics[key] != expected:
                errors.append(f'Expected {expected} {key} in v522, got {metrics[key]}')
    warnings.append(f'{self_aliases} self-aliases retained as authored, pending review')
    return errors, warnings, metrics, status, alias_rows, term_links


def write_csv(path, names, rows):
    with open(path, 'w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(names), extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def build_tables(data, status, aliases, links):
    term_rows = []
    for row in data['Lexicon']:
        state, destination = status[row['ID']]
        term_rows.append(dict(zip(TERM_COLUMNS, (
            row['ID'], row['Term'], row.get('Category', ''), row.get('Subcategory', ''),
            row['Plain-English meaning'], row.get('Mechanical role', ''),
            row.get('Typical value / unit', ''), row.get('Design notes / distinctions', ''),
            row.get('Scope', ''), row.get('Added', ''), row.get('Search tags', ''),
            row.get('Aliases / Related labels', ''), row.get('Example systems', ''),
            row.get('Source keys', ''), row.get('Primary source URL', ''),
            row.get('Additional source URLs', ''), state, destination,
        ))))
    source_columns = ('source_key', 'game_system', 'publisher_steward', 'source_type',
                      'url', 'notes', 'legacy_supplementary', 'additional_url')
    sources = [dict(zip(source_columns, (
        row['Key'], row['System'], row.get('Publisher', ''), row.get('Source type', ''),
        row.get('URL', ''), row.get('Why it is useful', ''),
        row.get('Legacy supplementary URLs / notes', ''), row.get('Additional source URL', ''),
    ))) for row in data['Sources']]
    relation_columns = ('from_term_id', 'relation_type', 'to_term_id', 'notes', 'evidence', 'version')
    relationships = [dict(zip(relation_columns, (
        r['Source ID'], r['Relationship'], r['Target ID'], r.get('Rationale', ''),
        r.get('Evidence / provenance', ''), r.get('Version', ''),
    ))) for r in data['Relationships']]
    return (term_rows, sources, relationships, source_columns, relation_columns)


SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE terms (
  term_id TEXT PRIMARY KEY, canonical_term TEXT NOT NULL, category TEXT,
  subcategory TEXT, definition TEXT NOT NULL, mechanical_role TEXT,
  typical_value_unit TEXT, design_notes TEXT, scope TEXT, added TEXT,
  search_tags TEXT, aliases TEXT, example_systems TEXT, source_keys TEXT,
  primary_source_url TEXT, additional_source_urls TEXT,
  status TEXT NOT NULL CHECK(status IN ('ACTIVE','REDIRECT')),
  redirect_target TEXT REFERENCES terms(term_id)
);
CREATE TABLE sources (
  source_key TEXT PRIMARY KEY, game_system TEXT, publisher_steward TEXT,
  source_type TEXT, url TEXT, notes TEXT, legacy_supplementary TEXT, additional_url TEXT
);
CREATE TABLE aliases (
  term_id TEXT NOT NULL REFERENCES terms(term_id), alias TEXT NOT NULL,
  PRIMARY KEY(term_id, alias)
);
CREATE TABLE term_sources (
  term_id TEXT NOT NULL REFERENCES terms(term_id),
  source_key TEXT NOT NULL REFERENCES sources(source_key),
  PRIMARY KEY(term_id, source_key)
);
CREATE TABLE relationships (
  relationship_id INTEGER PRIMARY KEY, from_term_id TEXT NOT NULL REFERENCES terms(term_id),
  relation_type TEXT NOT NULL, to_term_id TEXT NOT NULL REFERENCES terms(term_id),
  notes TEXT, evidence TEXT, version TEXT,
  UNIQUE(from_term_id, relation_type, to_term_id)
);
CREATE TABLE research_records (
  sheet_name TEXT NOT NULL, record_id TEXT NOT NULL, payload TEXT NOT NULL,
  PRIMARY KEY(sheet_name, record_id)
);
CREATE INDEX ix_terms_category ON terms(category, subcategory);
CREATE INDEX ix_relationship_target ON relationships(to_term_id);
CREATE INDEX ix_term_source_key ON term_sources(source_key);
CREATE VIRTUAL TABLE term_search USING fts5(
  term_id UNINDEXED, canonical_term, aliases, category, subcategory,
  definition, mechanical_role, design_notes, search_tags
);
"""


def create_db(path, terms, sources, relationships, aliases, links, data):
    with sqlite3.connect(path) as db:
        db.executescript(SCHEMA)
        # Insert terms in two passes: a redirect may point forward.
        db.executemany(
            'INSERT INTO terms(' + ','.join(TERM_COLUMNS) + ') VALUES(' + ','.join('?' for _ in TERM_COLUMNS) + ')',
            [[r[k] for k in TERM_COLUMNS[:17]] + [None] for r in terms],
        )
        db.executemany('UPDATE terms SET redirect_target=? WHERE term_id=?',
                       [(r['redirect_target'], r['term_id']) for r in terms if r['redirect_target']])
        source_cols = tuple(sources[0])
        db.executemany('INSERT INTO sources VALUES(' + ','.join('?' for _ in source_cols) + ')',
                       [[r[k] for k in source_cols] for r in sources])
        db.executemany('INSERT INTO aliases(term_id,alias) VALUES (?,?)', aliases)
        db.executemany('INSERT INTO term_sources(term_id,source_key) VALUES (?,?)', links)
        rel_cols = tuple(relationships[0])
        db.executemany('INSERT INTO relationships(' + ','.join(rel_cols) + ') VALUES (' + ','.join('?' for _ in rel_cols) + ')',
                       [[r[k] for k in rel_cols] for r in relationships])
        db.executemany(
            'INSERT INTO term_search VALUES (' + ','.join('?' for _ in range(9)) + ')',
            [(r['term_id'], r['canonical_term'], r['aliases'], r['category'], r['subcategory'],
              r['definition'], r['mechanical_role'], r['design_notes'], r['search_tags']) for r in terms],
        )
        for sheet in RESEARCH_SHEETS:
            head = next(iter(data[sheet]))
            id_column = next(iter(head))
            db.executemany('INSERT INTO research_records VALUES (?,?,?)',
                           [(sheet, r[id_column], json.dumps(r, ensure_ascii=False, sort_keys=True))
                            for r in data[sheet]])
        bad = db.execute('PRAGMA foreign_key_check').fetchall()
        if bad:
            raise ReleaseError(f'Foreign-key failures: {bad[:5]}')
        for tbl, expected in [('terms', len(terms)), ('sources', len(sources)),
                              ('relationships', len(relationships)), ('aliases', len(aliases)),
                              ('term_sources', len(links)), ('term_search', len(terms))]:
            actual = db.execute('SELECT count(*) FROM ' + tbl).fetchone()[0]
            if actual != expected:
                raise ReleaseError(f'SQLite {tbl}: expected {expected}, found {actual}')
        db.commit()


def build_release(target, data, metrics, status, aliases, links, master_hash, warnings):
    if target.exists():
        raise ReleaseError(f'Output already exists: {target}. Choose a new directory.')
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.lexicon-', dir=target.parent) as folder:
        staging = pathlib.Path(folder)
        terms, sources, relationships, source_cols, relation_cols = build_tables(data, status, aliases, links)
        write_csv(staging / 'terms.csv', TERM_COLUMNS, terms)
        write_csv(staging / 'sources.csv', source_cols, sources)
        write_csv(staging / 'aliases.csv', ('term_id', 'alias'),
                  [dict(term_id=k, alias=v) for k, v in aliases])
        write_csv(staging / 'term_sources.csv', ('term_id', 'source_key'),
                  [dict(term_id=k, source_key=v) for k, v in links])
        write_csv(staging / 'relationships.csv', relation_cols, relationships)
        for sheet in RESEARCH_SHEETS:
            rows = data[sheet]
            if rows:
                write_csv(staging / (sheet.lower().replace(' ', '_') + '.csv'), rows[0].keys(), rows)
        create_db(staging / 'wargaming_lexicon.sqlite', terms, sources, relationships, aliases, links, data)
        hashes = {file.name: digest(file) for file in staging.iterdir() if file.is_file()}
        manifest = dict(version='v522', source_sha256=master_hash, counts=metrics,
                        warnings=warnings, files_sha256=hashes,
                        verification={'source_links': 'complete', 'relationship_endpoints': 'complete',
                                      'sqlite_foreign_keys': 'passed',
                                      'frozen_v281_comparison': 'not verified',
                                      'parent_v521_comparison': 'not verified'},
                        release_status='staged-not-published')
        (staging / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        staging.rename(target)
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('workbook', type=pathlib.Path)
    p.add_argument('--expected-sha256', required=True, help='Approved workbook SHA-256')
    p.add_argument('--out-dir', type=pathlib.Path, help='A new directory for staged CSV/SQLite outputs')
    p.add_argument('--expect-v522', action='store_true', help='Check fixed v522 record counts')
    args = p.parse_args(argv)
    if not args.workbook.is_file():
        raise ReleaseError('Workbook does not exist: ' + str(args.workbook))
    observed_hash = digest(args.workbook)
    if observed_hash.lower() != args.expected_sha256.lower():
        raise ReleaseError(f'Workbook hash mismatch: found {observed_hash}')
    book = MasterWorkbook(args.workbook)
    try:
        data = {name: book.read_sheet(name) for name in CORE_SHEETS + RESEARCH_SHEETS}
    finally:
        book.close()
    errors, warnings, metrics, status, aliases, links = validate(data, args.expect_v522)
    if errors:
        raise ReleaseError('Validation failed:\n' + '\n'.join(errors[:30]))
    result = {'source_sha256': observed_hash, 'counts': metrics, 'warnings': warnings}
    if args.out_dir:
        manifest = build_release(args.out_dir, data, metrics, status, aliases, links,
                                 observed_hash, warnings)
        result['staged'] = str(args.out_dir)
        result['files_sha256'] = manifest['files_sha256']
    else:
        result['status'] = 'checked-only; no release files written'
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ReleaseError, OSError, sqlite3.Error, zipfile.BadZipFile) as exc:
        print('Export refused:', exc, file=sys.stderr)
        sys.exit(1)
