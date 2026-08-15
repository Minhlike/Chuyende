# Research Agent Long-Term Memory Schema Reference

> **Version:** 1.0.0  
> **Database:** SQLite 3 (ACID, WAL mode, FTS5)  
> **Repository:** `src/research_agent/storage/repository.py`

---

## 1. Relational Tables

### 1.1 `memory_records` (General M0..M5 Memory Entities)
```sql
CREATE TABLE IF NOT EXISTS memory_records (
    memory_id                   TEXT PRIMARY KEY,
    tier                        TEXT NOT NULL,
    record_type                 TEXT NOT NULL,
    promotion_state             TEXT NOT NULL,
    topic                       TEXT NOT NULL,
    summary                     TEXT NOT NULL,
    content                     TEXT,
    reference_type              TEXT,
    reference_id                TEXT,
    associated_entity_ids_json  TEXT,
    ownership                   TEXT NOT NULL,
    epistemic_status            TEXT NOT NULL,
    is_generated_summary        INTEGER NOT NULL DEFAULT 0,
    supersedes_id               TEXT,
    superseded_by_id            TEXT,
    is_stale                    INTEGER NOT NULL DEFAULT 0,
    review_required             INTEGER NOT NULL DEFAULT 0,
    last_verified_at            TEXT,
    privacy                     TEXT NOT NULL DEFAULT 'INTERNAL',
    actor                       TEXT NOT NULL DEFAULT 'RESEARCH_AGENT',
    session_id                  TEXT,
    confidence_category         TEXT DEFAULT 'HIGH',
    confidence_basis            TEXT,
    tags_json                   TEXT,
    importance                  INTEGER NOT NULL DEFAULT 3,
    metadata_json               TEXT,
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT NOT NULL
);
```

### 1.2 `decision_records` (M4 Architecture & Research Decisions)
```sql
CREATE TABLE IF NOT EXISTS decision_records (
    decision_id                 TEXT PRIMARY KEY,
    title                       TEXT NOT NULL,
    status                      TEXT NOT NULL,
    context                     TEXT NOT NULL,
    decision                    TEXT NOT NULL,
    rationale                   TEXT NOT NULL,
    alternatives_considered_json TEXT,
    evidence_ids_json           TEXT,
    consequences                TEXT NOT NULL,
    target_affected_entities_json TEXT,
    related_nodes_json          TEXT,
    related_claims_json         TEXT,
    related_experiments_json    TEXT,
    supersedes_id               TEXT,
    superseded_by_id            TEXT,
    diff_summary                TEXT,
    actor                       TEXT NOT NULL DEFAULT 'HUMAN_ARCHITECT_OR_AGENT',
    made_at                     TEXT NOT NULL,
    metadata_json               TEXT,
    created_at                  TEXT NOT NULL
);
```

### 1.3 `episodes` (M3 Episodic & Negative Result Logging)
```sql
CREATE TABLE IF NOT EXISTS episodes (
    episode_id                  TEXT PRIMARY KEY,
    session_id                  TEXT,
    timestamp                   TEXT NOT NULL,
    actor                       TEXT NOT NULL,
    action                      TEXT NOT NULL,
    object_reference            TEXT,
    outcome                     TEXT NOT NULL,
    status                      TEXT NOT NULL,
    related_node_code           TEXT,
    related_rq_id               TEXT,
    related_hyp_id              TEXT,
    related_artifact_ids_json   TEXT,
    provenance_details_json     TEXT,
    tags_json                   TEXT,
    is_failure                  INTEGER NOT NULL DEFAULT 0,
    failure_reason              TEXT,
    created_at                  TEXT NOT NULL
);
```

### 1.4 `open_questions` (First-Class Research Gaps)
```sql
CREATE TABLE IF NOT EXISTS open_questions (
    question_id                 TEXT PRIMARY KEY,
    question                    TEXT NOT NULL,
    related_rq_id               TEXT,
    related_hyp_id              TEXT,
    related_node_code           TEXT,
    why_open                    TEXT NOT NULL,
    required_evidence           TEXT NOT NULL,
    proposed_experiment         TEXT,
    priority                    TEXT NOT NULL DEFAULT 'HIGH',
    status                      TEXT NOT NULL DEFAULT 'OPEN',
    resolution_notes            TEXT,
    resolved_by_id              TEXT,
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT NOT NULL
);
```

### 1.5 `lessons_learned` (Empirical Research Lessons)
```sql
CREATE TABLE IF NOT EXISTS lessons_learned (
    lesson_id                   TEXT PRIMARY KEY,
    title                       TEXT NOT NULL,
    statement                   TEXT NOT NULL,
    originating_episode_id      TEXT,
    experiment_run_id           TEXT,
    evidence_ids_json           TEXT,
    scope                       TEXT,
    actionable_recommendations_json TEXT,
    created_at                  TEXT NOT NULL
);
```

### 1.6 `research_sessions` (Session Tracking & Handoffs)
```sql
CREATE TABLE IF NOT EXISTS research_sessions (
    session_id                  TEXT PRIMARY KEY,
    start_time                  TEXT NOT NULL,
    end_time                    TEXT,
    actor                       TEXT NOT NULL,
    objective                   TEXT NOT NULL,
    active_roadmap_nodes_json   TEXT,
    actions_summary_json        TEXT,
    decisions_made_json         TEXT,
    unresolved_items_json       TEXT,
    handoff_summary             TEXT,
    git_commit_hash             TEXT,
    created_at                  TEXT NOT NULL,
    updated_at                  TEXT NOT NULL
);
```

### 1.7 `status_transitions` (Immutable Evolution History)
```sql
CREATE TABLE IF NOT EXISTS status_transitions (
    transition_id               TEXT PRIMARY KEY,
    entity_type                 TEXT NOT NULL,
    entity_id                   TEXT NOT NULL,
    from_status                 TEXT NOT NULL,
    to_status                   TEXT NOT NULL,
    cause                       TEXT NOT NULL,
    evidence_id                 TEXT,
    decision_id                 TEXT,
    actor                       TEXT NOT NULL DEFAULT 'RESEARCH_AGENT',
    timestamp                   TEXT NOT NULL
);
```

### 1.8 `memory_fts` (FTS5 Lexical Search)
```sql
CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
    entity_id UNINDEXED,
    entity_type,
    title,
    body,
    tags
);
```

---

## 2. Derived Semantic Vector Index Format

- **File Path:** `runtime/indexes/derived_vectors.json`
- **Schema:**
```json
{
  "version": "1.0.0",
  "provider": "LOCAL_BM25_TFIDF",
  "dimension": 128,
  "vectors": {
    "CLM-000008": {
      "entity_type": "CLAIM",
      "vector": [0.012, -0.045, ...],
      "updated_at": "2026-08-16T03:30:00Z"
    }
  }
}
```
