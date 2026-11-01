#!/usr/bin/env python3
"""Check frozen WG identifiers and order without pretending that later text cannot change.

I keep this separate from the exporter. Changing a definition is one thing;
quietly recycling a WG number is quite another.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from export_master import MasterWorkbook, ReleaseError, WG_ID, digest


def compare_rows(frozen, current):
    if not frozen or not current:
        raise ReleaseError('Missing Lexicon rows')
    keys = tuple(frozen[0])
    if set(keys) != set(current[0]):
        raise ReleaseError('Lexicon columns differ; compare an agreed mapping first')
    old_ids = [row.get('ID', '').strip() for row in frozen]
    current_ids = [row.get('ID', '').strip() for row in current]
    for name, ids in [('frozen', old_ids), ('current', current_ids)]:
        if len(ids) != len(set(ids)):
            raise ReleaseError(f'{name}: repeated WG identifier')
        if any(not WG_ID.fullmatch(ident) for ident in ids):
            raise ReleaseError(f'{name}: invalid WG identifier')
    old_set = set(old_ids)
    missing = [ident for ident in old_ids if ident not in set(current_ids)]
    order = [ident for ident in current_ids if ident in old_set]
    prefix_ok = current_ids[:len(old_ids)] == old_ids
    if missing or order != old_ids or not prefix_ok:
        raise ReleaseError('Frozen identifiers missing, reordered or moved from their original positions')
    by_id = {row['ID']: row for row in current}
    changed_fields = Counter()
    changed_rows = 0
    for row in frozen:
        current_row = by_id[row['ID']]
        touched = False
        for field in keys:
            if row.get(field, '') != current_row.get(field, ''):
                touched = True
                changed_fields[field] += 1
        if touched:
            changed_rows += 1
    return {
        'frozen_wg_count': len(old_ids),
        'current_wg_count': len(current_ids),
        'frozen_identifiers_present': True,
        'frozen_relative_order_preserved': True,
        'frozen_prefix_positions_preserved': True,
        'new_wg_identifiers': len(current_ids) - len(old_ids),
        'inherited_rows_with_changed_fields': changed_rows,
        'field_change_counts': dict(sorted(changed_fields.items())),
        'note': 'Checks identifier preservation, not whether later textual changes were correct.',
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('frozen_v281', type=Path)
    parser.add_argument('current', type=Path)
    parser.add_argument('--expected-frozen-sha256', help='Known historical hash, when available')
    parser.add_argument('--expected-current-sha256', required=True)
    args = parser.parse_args(argv)
    for path in [args.frozen_v281, args.current]:
        if not path.is_file():
            raise ReleaseError(f'Workbook missing: {path}')
    old_hash, current_hash = digest(args.frozen_v281), digest(args.current)
    if args.expected_frozen_sha256 and old_hash != args.expected_frozen_sha256.lower():
        raise ReleaseError('Frozen workbook SHA-256 mismatch')
    if current_hash != args.expected_current_sha256.lower():
        raise ReleaseError('Current workbook SHA-256 mismatch')
    old, cur = MasterWorkbook(args.frozen_v281), MasterWorkbook(args.current)
    try:
        report = compare_rows(old.read_sheet('Lexicon'), cur.read_sheet('Lexicon'))
    finally:
        old.close()
        cur.close()
    report.update({'frozen_sha256': old_hash, 'current_sha256': current_hash})
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ReleaseError, OSError, ValueError) as exc:
        print('Frozen identifier check refused:', exc, file=sys.stderr)
        sys.exit(1)
