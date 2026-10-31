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

## Release requirements

1. Recover the exact frozen v281 reference and v521 parent, verify their hashes, and compare frozen IDs/order and inherited content.
2. Verify all source keys and roles, redirects, aliases, relationship endpoints, inverse edges, taxonomy, staging tables and formula errors.
3. Export v522 into a documented relational model, preserving stable WG IDs and distinguishing active records from redirects.
4. Build CSV and SQLite outputs from the same validated data, then compare counts, IDs, provenance and relationships against the workbook.
5. Validate search index, browser rendering, CSV parsing and a representative set of term details before updating release labels.
6. Publish a manifest with input and output SHA-256 values, counts, date and unresolved exceptions.

No research-only mechanic should become a canonical WG entry without admissible source evidence and duplicate checks.

## Known review queues

31 self-aliases, 610 one-way symmetric links, 2,483 active graph orphans, 16 unmapped occurrences, 103 discoveries without candidates, and historical provenance investigations remain open. These are review items, not grounds for indiscriminate automatic fixes.

The old release files are retained until a complete replacement is independently verified.
