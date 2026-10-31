# v522 migration status

The research master and the repository's published database are currently **different releases**. Do not label the existing CSV, SQLite database or website as v522.

## Research master

- File: `wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx`
- SHA-256: `c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b`
- 348 worksheets; 3,475 WG records (3,472 active, three redirects); 816 sources; 1,611 relationships; 575 occurrences; 616 discoveries; 514 candidates
- Most recent independent structural audit: 31 October 2026; zero reported structural failures

The local file hash was checked again on 31 October 2026. The original frozen v281 workbook and exact v521 parent were not available locally for a fresh comparison. Historical checks do not replace that missing verification.

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
