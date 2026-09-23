# Data model

The canonical entity is `terms`.

- `aliases` -> alternative names for a term.
- `systems` + `term_systems` -> many-to-many game/ruleset occurrence.
- `sources` + `term_sources` -> provenance.
- `tags` + `term_tags` -> normalised discovery tags.
- `relationships` -> semantic links between canonical terms.
- `research_batches` -> project research history.
- `term_search` -> SQLite FTS5 full-text index.
- `publication_audit` -> publication-oriented classification based on scope.

Definitions are concise paraphrases intended to describe mechanical concepts rather than reproduce source rules.
