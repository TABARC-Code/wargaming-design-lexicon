# Historical FAQ research: Dust Warfare and Dropzone Commander

Research appendix to the unchanged **v522** master, 1 November 2026.

The 27 staged records contain 11 historical *Dropzone Commander: Battle for Earth* FAQ crosswalks, 15 *Dust Warfare* FAQ v1.4 crosswalks and one separately recorded v1.3-to-v1.4 supersession correction. **None is a newly admitted WG mechanic.**

This directory intentionally sits outside `data/`: the repository's published CSV/SQLite dataset is older, and publishing a research finding is not the same as validating a canonical database change.

## Included files

- `research_crosswalk.csv`: all 27 publisher-grounded paraphrases, 1-based PDF pages, nearest existing WG identifiers, assessments, evidence URLs and follow-up decisions.
- `staged_sources.csv`: three provisional publisher-hosted documents, edition roles and limitations.
- `held_provenance.csv`: five unresolved scope/attribution issues, including WG-1380, WG-1381, WG-1238, the BFE revision inconsistency and the Dust FAQ supersession.
- `audit.json`: verified workbook hashes, record counts and limits.

## Source boundaries

*Dropzone Commander: Battle for Earth* historical FAQ:
- Publisher index: https://ttcombat.com/pages/dropzone-commander-faqs-errata
- Original PDF: https://cdn.shopify.com/s/files/1/0965/1274/files/Dropzone_BFE_FAQ_v1.0.pdf?427=
- Filename v1.0, printed V1.1, internal current-edition list v1.0 dated 19 September 2019. Treat the document as a historically hosted publisher FAQ, **not** proof of an independently released v1.1 or the rules of 2025/2026 editions.

*Dust Warfare* 2012 rule system:
- Publisher document archive: https://www.fantasyflightgames.com/more/product-document-archive/
- FAQ v1.3, 10 October 2012: https://www.fantasyflightgames.com/ffg_content/Dust-Warfare/Support/FAQ/Dust_Warfare_FAQ_1.3_low%20res.pdf
- FAQ v1.4, 2 April 2013: https://images-cdn.fantasyflightgames.com/ffg_content/Dust-Warfare/Support/FAQ/Dust_Warfare_FAQ_1.4%20low%20res.pdf
- The v1.4 FAQ explicitly allows two *special* actions (for example Heal/Repair). The v1.3 blanket no-repeat statement must not be treated as still authoritative; consecutive ordinary Move/Attack actions remain restricted. FAQ revisions are **not** separate game editions and not *Dust Tactics* mechanics.

Publisher PDF text was inspected in earlier historical audits and/or publisher web results; PDF bytes were not locally downloaded or hashed. The references are publisher documents, with their historical roles recorded.

## Record admission

The crosswalks are research-only. Before promoting any row to a canonical source link, occurrence, discovery or WG entry, compare the full procedure with the cited existing WG and its edition, verify provenance and distinguish source occurrence from a genuinely separate design mechanic.

Existing `DZC-BFE` and `DZC-BFE-RB` reference third-party documents, not the publisher-hosted 2019 FAQ. The FAQ does **not** prove WG-1380 Focal Point or WG-1381 In Readiness. The WG-1238 World at War 85 source mismatch remains a separate held issue.

The original v281 canonical workbook SHA-256 and v522 master SHA-256 were checked again. All 3,023 frozen WG identifiers retain their original order. The exact v521 parent was unavailable, so no fresh inherited-cell comparison is claimed.

## Canonical impact

| Field | Before | After |
| --- | ---: | ---: |
| WG records | 3,475 | 3,475 |
| Sources | 816 | 816 |
| Relationships | 1,611 | 1,611 |
| Rule occurrences | 575 | 575 |
| Discoveries | 616 | 616 |
| Candidates | 514 | 514 |

No version increment. Do not treat this folder as a published current-edition rules reference.
