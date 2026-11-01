# v522 migration status

The research master and the repository's published database are currently **different releases**. Do not label the existing CSV, SQLite database or website as v522.

## Research master

- File: `wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx`
- SHA-256: `c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b`
- 348 worksheets; 3,475 WG records (3,472 active, three redirects); 816 sources; 1,611 relationships; 575 occurrences; 616 discoveries; 514 candidates
- Most recent independent structural audit: 31 October 2026; zero reported structural failures

The exact frozen v281 workbook and v521 parent have since been recovered and their SHA-256 hashes checked locally: v281 `fa6fa874702627861af960e657c9893b5382ae74e11c9acb86e4f00a81e96a98`; v521 `7d97a59a05bf11ef73dc4bafacaca07f7fbfe903108488b6f66fd7e90c85c8f3`. The 30 October independent parent-fidelity report records 344 inherited sheets, 163,920 inherited populated cells, three authorised changes, 220 newly populated cells and no unexpected changes or removals. This does not by itself publish the release: the CSV, SQLite and website must still be promoted together after staging checks.

## Repository baseline

- `main` inspected at `b3f3b7f62ecf55353dfc0001e10c8e533cc0db92`
- Latest workbook on that branch: `data/wargaming_design_lexicon_master_v235.xlsx`
- The site reads `data/terms.csv`; replacing an XLSX alone will not update the site
- The existing SQLite database and CSV exports must be regenerated together from a checked source
- `tools/validate_site.py` checks basic identifiers and required text, not provenance or graph integrity
- `sql/schema.sql` is a schema dump, not a clean database initialisation script

## Staged exporter, 31 October 2026

`tools/export_master.py` now reads the approved workbook without altering it, checks its SHA-256 and references, and generates a separate CSV/SQLite staging directory with a manifest. Seven standalone tests are in `tools/test_export_master.py` and run during validation. Details and commands: [Export pipeline](EXPORT_PIPELINE.md).

A local staging build completed with 3,475 terms, 3,472 active entries, three redirects, 816 sources, 1,611 relationships, 7,163 aliases and 3,948 source links. SQLite foreign keys and integrity checks passed. These are staging results, **not** a replacement of the live repository database or evidence of a completed v281/v521 comparison.

The static browser's CSV path and deployment packaging have been corrected, but repository Pages configuration remains separate from successful data validation.

## Release requirements

1. Recover the exact frozen v281 reference and v521 parent, verify their hashes, and compare frozen IDs/order and inherited content.
2. Verify all source keys and roles, redirects, aliases, relationship endpoints, inverse edges, taxonomy, staging tables and formula errors.
3. Export v522 into a documented relational model, preserving stable WG IDs and distinguishing active records from redirects.
4. Build CSV and SQLite outputs from the same validated data, then compare counts, IDs, provenance and relationships against the workbook.
5. Validate search index, browser rendering, CSV parsing and a representative set of term details before updating release labels.
6. Publish a manifest with input and output SHA-256 values, counts, date and unresolved exceptions.

No research-only mechanic should become a canonical WG entry without admissible source evidence and duplicate checks.

## Workbook cover-sheet discrepancy

The `START HERE` worksheet has an updated v522 heading but its summary counts have not caught up with the authoritative data sheets:

| Field | `START HERE` | Verified data |
| --- | ---: | ---: |
| Current WG IDs | 3,460 | 3,475 |
| Active concepts | 3,457 | 3,472 |
| Registered sources | 809 | 816 |
| Controlled relationships | 1,533 | 1,611 |

These are stale descriptive cells, not evidence that entries are missing from the underlying sheets. Do not correct them by changing canonical data. Refresh the cover-page summary only after the master and inherited version comparisons are authorised and complete.

## Known review queues

31 self-aliases, 610 one-way symmetric links, 2,483 active graph orphans, 16 unmapped occurrences, 103 discoveries without candidates, and historical provenance investigations remain open. These are review items, not grounds for indiscriminate automatic fixes.

The old release files are retained until a complete replacement is independently verified.
