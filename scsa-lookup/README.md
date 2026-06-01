# SCSA Curriculum Lookup Skill — Developer Documentation

## Overview

This skill provides a comprehensive interface to the Western Australian (SCSA) curriculum data, stored in a local SQLite database (`scsa.db`). It supports querying content descriptors, achievement standards, year level descriptions, general capabilities, ABLEWA content, judging standards, glossaries, and teaching/assessment principles.

## Architecture

```
scsa/
├── scsa-helper.cjs          # Node.js CLI query tool (main interface)
├── scsa.db                   # SQLite database (~4.3MB, ~9,800 records)
├── SKILL.md                  # Copilot skill definition
├── README.md                 # This file
├── package.json              # Node.js dependencies (better-sqlite3)
├── node_modules/             # Installed dependencies
```

## Database Schema

### Core Tables

| Table | Records | Description |
|---|---|---|
| `content_descriptors` | ~2,339 | Curriculum content from scope & sequence documents |
| `achievement_standards` | 132 | Expected student outcomes per area × year |
| `year_level_descriptions` | 132 | Teaching context per area × year |
| `glossary_terms` | 767 | Subject-specific terminology |
| `judging_standards` | ~4,954 | A–E grade descriptors |
| `principles` | 13 | Teaching and assessment principles |
| `ablewa_content` | 645 | ABLEWA Stages A–D content |
| `general_capabilities` | 6 | Capability definitions |
| `capability_elements` | 92 | Capability structure (elements + sub-elements) |
| `capability_indicators` | 737 | Progression indicators per level |
| `acara_crossref` | 0* | SCSA↔ACARA mapping (*future population) |

### Reference Tables
- `learning_areas` — 29 areas (13 learning areas + 6 capabilities + sub-areas)
- `year_levels` — 11 levels (PP, Y1–Y10)

### FTS Virtual Tables
- `content_fts` — Full-text search on content descriptors
- `achievement_fts` — Full-text search on achievement standards
- `glossary_fts` — Full-text search on glossary terms

### Known Limitations

- **Literacy capability** has a different PDF structure from other capabilities and uses text-based extraction (less precise than table-based)
- **Personal and Social capability** has split tables ("Levels 1a–3" and "Levels 4–6") that create extra element entries
- **Arts S&S** have two versions per subject (mandated + full); deduplication prefers mandated
- **Judging standards** from 2017 files are flagged as `is_best_effort` — may not align with 2025/2026 curriculum
- **Languages** only cover Aboriginal language revival programs (not mainstream languages)
- **ABLEWA Arts** table format differs from other ABLEWA files (subjects as columns, not rows)

## Technology Stack

- **Node.js** — CLI interface
  - `better-sqlite3` — SQLite queries
