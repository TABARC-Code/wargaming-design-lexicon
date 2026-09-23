CREATE INDEX ix_alias_name ON aliases(alias COLLATE NOCASE)
CREATE INDEX ix_terms_category ON terms(category,subcategory)
CREATE UNIQUE INDEX ux_terms_name ON terms(canonical_term COLLATE NOCASE)
CREATE TABLE aliases(alias_id INTEGER PRIMARY KEY AUTOINCREMENT,term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,alias TEXT NOT NULL COLLATE NOCASE,UNIQUE(term_id,alias))
CREATE TABLE metadata(
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
)
CREATE TABLE relationships(relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,from_term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,relation_type TEXT NOT NULL,to_term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,notes TEXT,UNIQUE(from_term_id,relation_type,to_term_id))
CREATE TABLE research_batches(batch_id INTEGER PRIMARY KEY AUTOINCREMENT,batch_label TEXT NOT NULL UNIQUE,notes TEXT)
CREATE TABLE sources(source_key TEXT PRIMARY KEY,game_system TEXT,publisher_steward TEXT,source_type TEXT,url TEXT,notes TEXT)
CREATE TABLE systems(system_id INTEGER PRIMARY KEY AUTOINCREMENT,system_name TEXT NOT NULL COLLATE NOCASE UNIQUE)
CREATE TABLE tags(tag_id INTEGER PRIMARY KEY AUTOINCREMENT,tag TEXT NOT NULL COLLATE NOCASE UNIQUE)
CREATE VIRTUAL TABLE term_search USING fts5(term_id UNINDEXED,canonical_term,aliases,category,subcategory,definition,mechanical_role,design_notes,search_tags)
CREATE TABLE 'term_search_config'(k PRIMARY KEY, v) WITHOUT ROWID
CREATE TABLE 'term_search_content'(id INTEGER PRIMARY KEY, c0, c1, c2, c3, c4, c5, c6, c7, c8)
CREATE TABLE 'term_search_data'(id INTEGER PRIMARY KEY, block BLOB)
CREATE TABLE 'term_search_docsize'(id INTEGER PRIMARY KEY, sz BLOB)
CREATE TABLE 'term_search_idx'(segid, term, pgno, PRIMARY KEY(segid, term)) WITHOUT ROWID
CREATE TABLE term_sources(term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,source_key TEXT NOT NULL REFERENCES sources(source_key) ON DELETE CASCADE,is_primary INTEGER NOT NULL DEFAULT 0,source_url TEXT,PRIMARY KEY(term_id,source_key))
CREATE TABLE term_systems(term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,system_id INTEGER NOT NULL REFERENCES systems(system_id) ON DELETE CASCADE,PRIMARY KEY(term_id,system_id))
CREATE TABLE term_tags(term_id TEXT NOT NULL REFERENCES terms(term_id) ON DELETE CASCADE,tag_id INTEGER NOT NULL REFERENCES tags(tag_id) ON DELETE CASCADE,PRIMARY KEY(term_id,tag_id))
CREATE TABLE terms(term_id TEXT PRIMARY KEY,canonical_term TEXT NOT NULL COLLATE NOCASE,category TEXT,subcategory TEXT,definition TEXT,mechanical_role TEXT,typical_value_unit TEXT,design_notes TEXT,scope TEXT,added TEXT,search_tags TEXT)
CREATE VIEW publication_audit AS
SELECT
 t.term_id,
 t.canonical_term,
 t.scope,
 CASE
   WHEN lower(coalesce(t.scope,'')) LIKE '%system-specific%' THEN 'game-specific label'
   WHEN lower(coalesce(t.scope,'')) LIKE '%historical%' THEN 'historical/common terminology'
   WHEN lower(coalesce(t.scope,'')) LIKE '%generic%' THEN 'generic design concept'
   ELSE 'review'
 END AS publication_class,
 COUNT(DISTINCT ts.source_key) AS source_count
FROM terms t
LEFT JOIN term_sources ts ON ts.term_id=t.term_id
GROUP BY t.term_id
CREATE VIEW source_coverage AS SELECT so.source_key,so.game_system,so.publisher_steward,so.source_type,so.url,COUNT(ts.term_id) linked_terms FROM sources so LEFT JOIN term_sources ts ON ts.source_key=so.source_key GROUP BY so.source_key
CREATE VIEW term_catalogue AS SELECT t.term_id,t.canonical_term,GROUP_CONCAT(DISTINCT a.alias) aliases,t.category,t.subcategory,t.definition,t.mechanical_role,t.typical_value_unit,t.design_notes,GROUP_CONCAT(DISTINCT s.system_name) systems,t.scope,t.added,t.search_tags FROM terms t LEFT JOIN aliases a ON a.term_id=t.term_id LEFT JOIN term_systems ts ON ts.term_id=t.term_id LEFT JOIN systems s ON s.system_id=ts.system_id GROUP BY t.term_id
