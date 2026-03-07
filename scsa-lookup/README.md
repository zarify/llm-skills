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
├── raw/                      # Source documents (read-only)
│   ├── curriculum/           # 51 DOCX/PDF files (S&S, Achievement, YLD, ABLEWA)
│   ├── general-capabilites/  # 6 PDF files
│   ├── glossary/             # 4 DOCX files
│   ├── principles/           # 2 TXT files
│   └── judging-standards/    # 113 DOCX files
└── scripts/                  # Python extraction & loading pipeline
    ├── requirements.txt      # Python dependencies
    ├── init_db.py            # Database schema creation + seed data
    ├── load_db.py            # Master loader (runs all parsers → DB)
    ├── extract_docx.py       # DOCX extraction framework
    ├── extract_pdf.py        # PDF extraction framework
    ├── extract_txt.py        # TXT extraction framework
    └── parsers/              # Per-document-type parsers
        ├── scope_sequence.py
        ├── achievement_standards.py
        ├── year_level_descriptions.py
        ├── general_capabilities.py
        ├── glossary.py
        ├── judging_standards.py
        ├── principles.py
        └── ablewa.py
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

## Rebuilding the Database

```bash
cd scsa/

# Install Python dependencies (first time only)
pip install -r scripts/requirements.txt

# Install Node.js dependencies (first time only)
npm install

# Rebuild the entire database from raw documents
python scripts/load_db.py --reset
```

The `--reset` flag reinitialises the schema before loading. Without it, existing data is cleared and reloaded.

## Adding New Documents

1. Place new DOCX/PDF/TXT files in the appropriate `raw/` subdirectory
2. If the document type has an existing parser, it will be picked up automatically on next `load_db.py` run
3. If it's a new document format, create a parser in `scripts/parsers/`
4. Run `python scripts/load_db.py --reset` to rebuild

## Parser Details

Each parser follows the pattern:
- Takes a file path or directory as input
- Returns a list of dicts matching the target DB table schema
- Can be run standalone for testing: `python scripts/parsers/<parser>.py <file>`

### Known Limitations

- **Literacy capability** has a different PDF structure from other capabilities and uses text-based extraction (less precise than table-based)
- **Personal and Social capability** has split tables ("Levels 1a–3" and "Levels 4–6") that create extra element entries
- **Arts S&S** have two versions per subject (mandated + full); deduplication prefers mandated
- **Judging standards** from 2017 files are flagged as `is_best_effort` — may not align with 2025/2026 curriculum
- **Languages** only cover Aboriginal language revival programs (not mainstream languages)
- **ABLEWA Arts** table format differs from other ABLEWA files (subjects as columns, not rows)

## Technology Stack

- **Python 3.11+** — Extraction and parsing
  - `python-docx` — DOCX reading
  - `pdfplumber` — PDF reading
  - `sqlite3` (stdlib) — Database operations
- **Node.js** — CLI interface
  - `better-sqlite3` — SQLite queries
