# Historical FAQ source and occurrence integration, v522 staging

This directory contains independently reconciled CSV exports from the *unchanged* v522 research master, with three historically scoped publisher FAQ sources and 26 unmapped research occurrences added. The 27th crosswalk is the Dust Warfare v1.3-to-v1.4 correction.

These files are **not** a replacement for the live `data/` directory or a new canonical workbook version. The original GitHub database remains an earlier release.

## Files

- `sources.csv`: all 819 source registrations, including the three historical publisher FAQs.
- `rule_occurrences.csv`: all 601 occurrences, including 26 new observations marked `RESEARCH_HOLD_UNMAPPED`. Their canonical WG ID fields are intentionally blank.
- `review_queue.csv`: all 102 review entries, 70 original and 32 new.
- `historical_faq_crosswalks.csv`: the 26 nearest-WG comparisons and one supersession correction.
- `historical_source_roles.csv`: edition, revision, publisher and provenance qualifications.
- `provenance_holds.csv`: five unresolved publisher and edition attribution issues.
- `manifest.json`: SHA-256 for every CSV here, full release counts and limitations.

The independently reconciled SQLite database, all other unchanged v522 CSV exports, a separate Excel integration register, the original reference workbooks and the build scripts are provided in the downloadable integration archive accompanying the development work. Those binary artifacts have **not** been committed to GitHub.

The [integration guide](../../docs/INTEGRATION_HISTORICAL_FAQ_V522.md), [builder](../../tools/integrate_historical_faq.py) and [verifier](../../tools/verify_historical_faq.py) describe the local rebuild. All new content is from the original historical source crosswalk under [research](../../research/historical-faq-crosswalks-20261101/).

## Evidence and release constraints

Publisher references:
- TTCombat's [Battle for Earth FAQ and errata index](https://ttcombat.com/pages/dropzone-commander-faqs-errata), historical document with a v1.0 filename, V1.1 printed header and September 2019 internal date
- [Fantasy Flight Games archive](https://www.fantasyflightgames.com/more/product-document-archive/), Dust Warfare FAQ revisions 1.3 (2012) and 1.4 (2013)

A nearest WG reference is a lead for comparison, not proof that the two procedures are equivalent. The current source-to-WG table therefore remains at 3,948 links; no new canonical WG IDs or graph edges have been created.

The v521 parent workbook remains unavailable for a fresh inherited-cell verification. The existing self-alias, symmetric-edge and graph-orphan queues remain open. Publication of a new canonical master is still withheld.
