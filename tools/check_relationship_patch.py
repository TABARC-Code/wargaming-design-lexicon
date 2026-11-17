#!/usr/bin/env python3
"""Check a proposed relationship endpoint patch without changing source data."""
import csv
import sys
import re
from collections import Counter
from pathlib import Path

SYMMETRIC = {"similar_to", "contrasts_with", "often_confused_with"}
FIELDS = ("row", "expected_source", "predicate", "expected_target",
          "replacement_source", "replacement_target", "reason")


def validate(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError("Unexpected patch columns")
        rows = list(reader)
    errors = []
    if not rows:
        errors.append("Empty patch")
    old = Counter()
    new = Counter()
    seen_rows = set()
    for record in rows:
        try:
            number = int(record["row"])
        except (ValueError, TypeError):
            errors.append("Invalid worksheet row")
            continue
        if number < 2:
            errors.append(f"Invalid data row {number}")
        if number in seen_rows:
            errors.append(f"Duplicate worksheet row {number}")
        seen_rows.add(number)
        for key in ("expected_source", "expected_target",
                    "replacement_source", "replacement_target"):
            value = record[key] or ""
            if not re.fullmatch(r"WG-[0-9]{4}", value):
                errors.append(f"Invalid WG ID at row {number}: {key}")
        if None in record or any(value is None for value in record.values()):
            errors.append(f"Malformed CSV record at row {number}")
        if not (record["reason"] or "").strip():
            errors.append(f"Missing reason at row {number}")
        if not (record["predicate"] or "").strip() or record["predicate"] != record["predicate"].strip():
            errors.append(f"Invalid predicate at row {number}")
        if record["expected_source"] == record["expected_target"]:
            errors.append(f"Old self-link at row {number}")
        if record["replacement_source"] == record["replacement_target"]:
            errors.append(f"New self-link at row {number}")
        if record["expected_source"] == record["replacement_source"] and record["expected_target"] == record["replacement_target"]:
            errors.append(f"No endpoint change at row {number}")
        old[(record["expected_source"], record["predicate"], record["expected_target"])] += 1
        new[(record["replacement_source"], record["predicate"], record["replacement_target"])] += 1
    for label, tuples in (("old", old), ("replacement", new)):
        for (source, predicate, target), count in tuples.items():
            if count != 1:
                errors.append(f"Repeated {label} tuple: {source}/{predicate}/{target}")
            if predicate in SYMMETRIC and tuples[(target, predicate, source)] != 1:
                errors.append(f"Missing {label} reciprocal: {source}/{predicate}/{target}")
    return len(rows), errors


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python tools/check_relationship_patch.py path/to/patch.csv")
    try:
        count, failures = validate(sys.argv[1])
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
    for failure in failures:
        print("FAIL:", failure)
    print(f"Rows checked: {count}; errors: {len(failures)}")
    sys.exit(bool(failures))
