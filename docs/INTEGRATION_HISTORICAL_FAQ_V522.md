# v522 historical FAQ integration

**Status:** the historical research has been integrated into a *separate, versioned* SQLite/CSV staging release. The original canonical workbook remains v522, unchanged. The earlier live database and website have not been overwritten.

## Verified counts

| Dataset | Original | Research-integrated |
| --- | ---: | ---: |
| Canonical WG terms | 3,475 | 3,475 |
| Registered publisher sources | 816 | 819 |
| Rule occurrence rows | 575 | 601 |
| Original WG-mapped occurrences | 575 | 575 |
| New historical research observations | 0 | 26 (held, unmapped) |
| Historical crosswalks and corrections | 0 | 27 |
| Relationships | 1,611 | 1,611 |
| WG-to-source links | 3,948 | 3,948 |
| Review queue records | 70 | 102 |

The new source keys are `DZC-BFE-2019-FAQ`, `DW-2012-FAQ13` and `DW-2013-FAQ14`. The older Dust FAQ has an explicit superseded source role. The updated document is labelled as a FAQ revision of the same 2012 game, not a separate edition.

The 26 new occurrence rows are marked `RESEARCH_HOLD_UNMAPPED`, with **no canonical WG identifier**. The 27th research record is a correction of the earlier FAQ's blanket special-action restriction. It is retained independently rather than counted as another game mechanic.

Each crosswalk's suggested WG links remain labelled **nearest-only**. New links to the canonical source/provenance table would falsely imply a proven equivalence.

## Rebuild

Use Python 3.11+ with the approved, locally generated v522 staging release and the three CSV files in [the historical FAQ research folder](../../research/historical-faq-crosswalks-20261101/).

```sh
python tools/integrate_historical_faq.py \
  /path/to/staged-v522 \
  research/historical-faq-crosswalks-20261101 \
  /path/to/new-integrated-release

python tools/verify_historical_faq.py \
  /path/to/new-integrated-release \
  /path/to/wargaming_design_lexicon_v376_v522_fantasy_depth_verified.xlsx \
  /path/to/wargaming-lexicon-v281-canonical.xlsx \
  /path/to/staged-v522
```

Both tools refuse to overwrite or alter the approved inputs. The verification checks the original master and frozen reference hashes, staged file checksums, preservation of the canonical CSV files, SQLite constraints and the held classifications. The repository also has an end-to-end synthetic importer test under `tools/test_integrate_historical_faq.py`.

### Independent data checks (1 November 2026)

The integrated local production release was checked against the original v522 staging outputs. Its SQLite database passed `PRAGMA integrity_check` and `PRAGMA foreign_key_check`. All 3,475 terms, 1,611 relationships, 7,163 aliases, 3,948 term-source links and existing full-text index records were retained.

The 819 sources, 601 occurrence rows, 27 crosswalks, 65 **research-only** nearest-WG associations, three edition-labelled source records and five provenance holds were reconciled. The 27 crosswalks generated 27 research review records; the five provenance holds generated five additional review records.

Full production integration archive SHA-256: `b09b93d5e23425f3f361eb772c1eafbb8848abbb3c3e3d5410cce1c8a6f18525` (the archive was produced locally and is available as a separate ChatGPT download, not as a file committed to GitHub). The local archive contains its own corresponding build and independent verification scripts; its SQLite schema stores the crosswalk fields as columns, whereas the repository importer keeps those fields together as a JSON payload. Both approaches preserve the historical review status and prohibit unverified canonical mappings.

## Release boundaries

- v522 SHA-256: `c12cafd92fe71c1bae433e6b2cecf5c1fcb3d05b1efb3d764db3f32e5f8d1d4b`.
- Frozen canonical v281 SHA-256: `fa6fa874702627861af960e657c9893b5382ae74e11c9acb86e4f00a81e96a98`.
- All 3,023 frozen WG IDs remain in their original order.
- Exact v521 parent: **not accessible for a fresh inherited-cell comparison**.
- BFE 2019 publisher FAQ is not evidence for later Dropzone editions or unrelated WG-1380/WG-1381 procedures.
- Dust Warfare FAQ 1.3 and 1.4 must remain separate provenance versions; the later rule on repeating special actions supersedes the earlier interpretation.
- The 31 self-aliases, 610 one-way symmetric relationships, 2,483 active orphans and other inherited research review counts have not been cleared by this integration.

**A new canonical workbook version or live database replacement requires the missing historical comparison and case-by-case adjudication of held research entries.** This integrated release does not claim either.
