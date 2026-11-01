# wargaming-design-lexicon
Tabletop gaming lexium database
---
# Miniature & Tabletop Wargaming Design Lexicon

A lightweight, searchable terminology database for miniature and tabletop wargame design.

> **Release status:** the repository browser, CSV exports and SQLite database are an older published snapshot. The v522 research master has a separate validated staging exporter, but it is **not** the live database. See [v522 migration status](docs/V522_MIGRATION_STATUS.md) for the evidence and remaining checks.

## Release

GitHub release 1.0, migrated from research master v15 on 23 September 2026.

- 1,100 canonical term records
- 2,058 aliases
- 210 named game/ruleset references
- 78 provenance records
- 1,440 term-to-source links
- SQLite FTS5 full-text search
- CSV exports for use without SQLite

## What is stored

The project stores terminology, short original paraphrases of mechanical meaning, aliases, design roles,
typical value/unit types, system associations and source provenance. It is intended as a design lexicon,
not a replacement for any game's rules.

The database does not intentionally reproduce substantial rulebook text, complete procedures, scenarios,
lore, tables or other long-form source material.

Game-specific labels are retained where useful for comparative research and are identified by scope.
Names of games, publishers and distinctive terminology remain associated with their respective owners.

## Quick start

Open `data/wargaming_lexicon.sqlite` with any SQLite client.

```sql
SELECT term_id, canonical_term, definition
FROM term_search
WHERE term_search MATCH 'suppression';
```

Browse one design family:

```sql
SELECT term_id, canonical_term, subcategory
FROM terms
WHERE category = 'Command & control'
ORDER BY canonical_term;
```

Inspect provenance:

```sql
SELECT t.canonical_term, s.game_system, s.publisher_steward, s.url
FROM terms t
JOIN term_sources ts ON ts.term_id = t.term_id
JOIN sources s ON s.source_key = ts.source_key
WHERE t.term_id = 'WG-0001';
```

## Repository layout

- `data/wargaming_lexicon.sqlite` - primary lightweight database
- `data/terms.csv` - canonical terminology
- `data/aliases.csv` - aliases
- `data/sources.csv` - source register
- `data/term_sources.csv` - provenance links
- `data/publication_audit.csv` - generic/game-specific publication classification
- `sql/schema.sql` - database schema
- `docs/DATA_MODEL.md` - relational model
- `docs/CONTENT_AND_PROVENANCE.md` - publication and source-handling notes

## Historical FAQ research supplement (1 November 2026)

[The separate Dust Warfare and Battle for Earth crosswalk](research/historical-faq-crosswalks-20261101/README.md) records 27 research-only findings, three publisher documents and five provenance holds. All nearest WG references have been checked against v522. No WG IDs, source rows or graph edges have been added to the published database.

The research is not an edition update. The official 2019 Battle for Earth FAQ must not be treated as later Dropzone Commander rules, and the 2013 Dust Warfare FAQ changes the earlier interpretation of repeated special actions.

## Historical FAQ integration (1 November 2026)

[The integrated research release](docs/INTEGRATION_HISTORICAL_FAQ_V522.md) adds three historically scoped publisher source records and 26 unmapped rule observations to a separate v522 staging database. A 27th finding records the Dust Warfare FAQ supersession. The 3,475 WG records, 1,611 relationships and 3,948 term-source links are unchanged.

The repository includes [the importer](tools/integrate_historical_faq.py), [the independent verifier](tools/verify_historical_faq.py) and its end-to-end fixture tests. **The live SQLite file and CSV exports are still the earlier publication**, and the v522 research master has not been renamed or overwritten.

## Stable IDs

`WG-####` IDs are intended to be stable. Three duplicate IDs discovered during the v15 migration were
repaired as `WG-1098`, `WG-1099` and `WG-1100` for Detected Submarine, Undetected Submarine and Radar Detection.

## Contributions

When adding a term, prefer an official or legally accessible public source. Add a concise original
paraphrase rather than copying rules text. Check canonical terms and aliases before creating a new entry.
Record provenance in `sources` and `term_sources`.

## Legal note

This is a research and design-reference database. Game and publisher names may be trade marks of their
respective owners. Inclusion indicates provenance or comparative reference, not affiliation or endorsement.
See `docs/CONTENT_AND_PROVENANCE.md`.

## v21 update

The current merged research master contains 1,241 canonical records. Research batches v16 through v21 have been consolidated into the repository data, with the v21 workbook retained in `data/wargaming_design_lexicon_v21.xlsx` and recent append batches under `releases/research-batches/`.

The repository is released under the MIT License. Source game and publisher names, trade marks, and the underlying third-party rules material remain the property of their respective owners. The lexicon uses concise original paraphrases and provenance links rather than reproducing substantial rules text.

---

Ok this isa  work in progrress  and should be used as such
