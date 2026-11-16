# v583 relationship reconciliation

Status: UNMERGED. These records are proposed corrections to the later v583 workbook lineage, not changes to the published SQLite or CSV release.

The six endpoint replacements in `relationship-corrections-v669-unmerged.csv` retain their original worksheet row numbers and expected old values. Apply only after verifying the exact source workbook checksum and each expected old tuple. Three predicates are symmetric; both directions must remain present after replacement.

The additional rationale correction is at worksheet row 3185, WG-1908 `contrasts_with` WG-3145. Replace the mistaken reference `Reciprocal of WG-3145 contrasts_with WG-2079` with `Reciprocal of WG-3145 contrasts_with WG-1908`. Preserve the remainder of the rationale.

The previous audit records v583 as 3,486 WG identifiers and 3,851 directed relationships. These figures have not been independently rerun against the exact workbook here. The v583 workbook checksum recorded for recovery is `88417b742523d33800240b393c8f53d176bbe5e55dbcb47ba018ae25a0249b0b`.

Do not update published exports, renumber identifiers, or infer orphan reductions from this patch. Reconcile v522 to v583, validate frozen IDs and redirects, source keys, formulas, graph endpoints, reciprocal predicates and provenance, then regenerate CSV and SQLite together. Preserve the historical FAQ staging separately until its records can be reconciled.
