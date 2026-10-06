#!/usr/bin/env python3
import csv, pathlib, re, sys
root = pathlib.Path(__file__).resolve().parents[1]
p = root / "data/terms.csv"
rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
ids = [r.get("term_id", "") for r in rows]
errors = []
if len(ids) != len(set(ids)):
    errors.append("duplicate IDs")
for i in ids:
    if not re.fullmatch(r"WG-\d{4}", i):
        errors.append("bad ID " + i)
for r in rows:
    if not r.get("canonical_term"):
        errors.append("missing term " + r.get("term_id", "?"))
    if not r.get("definition"):
        errors.append("missing definition " + r.get("term_id", "?"))
print(f"Validated {len(rows)} repository mechanics for site build")
if errors:
    print("\n".join(errors[:100]))
    sys.exit(1)
