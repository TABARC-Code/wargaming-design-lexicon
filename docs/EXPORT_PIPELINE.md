# Building a staged lexicon release

The source workbook is the record of research. CSV and SQLite are generated outputs. The currently published repository dataset must not be replaced until the staged output has been reconciled and the missing historical comparisons resolved.

## Requirements

Python 3.11+ with its standard library and a local copy of the approved workbook. No third-party spreadsheet package is needed for the exporter.

## Validate without writing

```sh
python tools/export_master.py /path/to/wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx \
  --expected-sha256 c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b \
  --expect-v522
```

## Build a separate release

```sh
python tools/export_master.py /path/to/wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx \
  --expected-sha256 c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b \
  --expect-v522 \
  --out-dir /path/to/staged-v522
```

The output directory must not exist. The script refuses to overwrite an earlier export. The supplied workbook must match the exact expected SHA-256; the input is never modified.

## Reconcile the staged output

Run the independent check against the *same* approved workbook and staging directory:

```sh
python tools/verify_staged.py /path/to/wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx \
  /path/to/staged-v522 \
  --expected-sha256 c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b
```

This compares every exported CSV record with the workbook, checks the SHA-256 manifest, SQLite integrity and foreign keys, reconciles table rows and full-text index contents, and verifies the research archive payloads. It reads the staged release without changing it.

## Exported data

| File | Contents |
| --- | --- |
| `terms.csv` | Every WG ID, including legacy redirects, with canonical terms, original descriptions, status and source fields |
| `sources.csv` | Registered sources and their provenance fields |
| `aliases.csv` | Term-to-alias links; repeated identical aliases within a record are collapsed |
| `term_sources.csv` | Term-to-source links |
| `relationships.csv` | Relationship endpoints, types, rationale, evidence and version |
| `rule_occurrences.csv` | Rule occurrences, still separate from approved WG mechanics |
| `discoveries.csv` | Research discoveries, not promoted automatically |
| `candidates.csv` | Research candidates, not promoted automatically |
| `review_queue.csv` | Outstanding reviews |
| `wargaming_lexicon.sqlite` | Normalised relational tables, full-text index and archived research records |
| `manifest.json` | Workbook hash, counts, export checksums and verification limitations |

The source workbook also contains numerous versioned audit and research-history worksheets. These remain in the original workbook. The staged relational release exports the eight named core and research worksheets, not a complete archival substitute for all 348 worksheets.

## Validation gates

The tool rejects a mismatched workbook hash; missing/duplicate or malformed WG IDs; absent definitions; unregistered term source keys; invalid or duplicate relationship endpoints; missing canonical statuses; unresolved redirect targets; unexpected formulas in exported sheets; and foreign-key or row-count mismatches in SQLite.

The v522 count gate checks 3,475 WG records, 3,472 active and three redirects, 816 sources, 1,611 relationships, 575 occurrences, 616 discoveries and 514 candidates.

Checks intentionally do **not** claim that all historical evidence is complete or that every recorded relationship is bi-directional. Known self-aliases, symmetric-link review items and graph orphans stay visible.

Run standalone unit tests with:

```sh
python -m unittest discover -s tools -p 'test_*.py'
```

## Publication requirements

1. Recover and compare the original v281 frozen reference and exact v521 parent.
2. Reconcile legacy IDs and inherited content.
3. Review open graph, alias and provenance issues, recording accepted exceptions.
4. Reconcile staged CSV/SQLite fields and IDs with the approved source workbook.
5. Check search, the browser and any published static asset package.
6. Only then replace live data and update the README release label.

**GitHub Pages:** the browser expects a `terms.csv` file beside `site/app.js`. The deployment workflow packages the current `data/terms.csv` into the site artifact. GitHub Pages must be enabled for the repository before deployment can succeed. Set Pages **Build and deployment** source to **GitHub Actions**, then add the repository Actions variable `PUBLISH_LEXICON_SITE` with the value `true`. Deployment is deliberately skipped until that variable is set, so a disabled Pages service does not turn a passing validation job into a failed workflow. A passing validation job alone does not publish the site.
