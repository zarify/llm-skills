#!/usr/bin/env python3
"""
SCSA Curriculum Database Schema Initialisation

Creates the SQLite database with all tables and seed data for the
Western Australian (SCSA) curriculum lookup skill.
"""

import sqlite3
import os
import sys

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scsa.db')


def create_schema(conn: sqlite3.Connection):
    """Create all tables."""
    cur = conn.cursor()

    cur.executescript("""
    -- Learning areas and their sub-areas
    CREATE TABLE IF NOT EXISTS learning_areas (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        parent_id TEXT,
        category TEXT NOT NULL,  -- 'learning-area', 'general-capability'
        implementation_year INTEGER,
        implementation_status TEXT,  -- 'implemented', 'familiarisation', 'coming-soon'
        FOREIGN KEY (parent_id) REFERENCES learning_areas(id)
    );

    -- Year levels
    CREATE TABLE IF NOT EXISTS year_levels (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        sort_order INTEGER NOT NULL
    );

    -- Curriculum content items (from scope and sequence documents)
    CREATE TABLE IF NOT EXISTS content_descriptors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        year_level_id TEXT NOT NULL,
        strand TEXT,
        sub_strand TEXT,
        content_description TEXT NOT NULL,
        elaborations TEXT,            -- JSON array
        image_context TEXT,           -- AI-generated context from embedded images
        image_context_source TEXT,    -- source image filename(s)
        source_document TEXT NOT NULL,
        is_mandated INTEGER DEFAULT 1,
        has_generated_context INTEGER DEFAULT 0,
        verification_status TEXT DEFAULT 'unverified',
        verification_notes TEXT,
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id),
        FOREIGN KEY (year_level_id) REFERENCES year_levels(id)
    );

    -- Achievement standards
    CREATE TABLE IF NOT EXISTS achievement_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        year_level_id TEXT NOT NULL,
        standard_text TEXT NOT NULL,
        source_document TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        verification_notes TEXT,
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id),
        FOREIGN KEY (year_level_id) REFERENCES year_levels(id)
    );

    -- Year level descriptions
    CREATE TABLE IF NOT EXISTS year_level_descriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        year_level_id TEXT NOT NULL,
        description_text TEXT NOT NULL,
        source_document TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        verification_notes TEXT,
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id),
        FOREIGN KEY (year_level_id) REFERENCES year_levels(id)
    );

    -- General capabilities
    CREATE TABLE IF NOT EXISTS general_capabilities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        source_document TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified'
    );

    CREATE TABLE IF NOT EXISTS capability_elements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        capability_id TEXT NOT NULL,
        element_name TEXT NOT NULL,
        sub_element_name TEXT,
        description TEXT,
        FOREIGN KEY (capability_id) REFERENCES general_capabilities(id)
    );

    CREATE TABLE IF NOT EXISTS capability_indicators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        element_id INTEGER NOT NULL,
        year_level_id TEXT NOT NULL,
        level_name TEXT,
        indicator_text TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY (element_id) REFERENCES capability_elements(id),
        FOREIGN KEY (year_level_id) REFERENCES year_levels(id)
    );

    -- Glossary terms
    CREATE TABLE IF NOT EXISTS glossary_terms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        term TEXT NOT NULL,
        definition TEXT NOT NULL,
        source_document TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id)
    );

    -- Judging standards / assessment pointers
    CREATE TABLE IF NOT EXISTS judging_standards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        year_level_id TEXT NOT NULL,
        strand TEXT,
        grade TEXT NOT NULL,  -- 'A', 'B', 'C', 'D', 'E'
        descriptor_text TEXT NOT NULL,
        source_document TEXT NOT NULL,
        is_best_effort INTEGER DEFAULT 0,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id),
        FOREIGN KEY (year_level_id) REFERENCES year_levels(id)
    );

    -- Teaching and assessment principles
    CREATE TABLE IF NOT EXISTS principles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,  -- 'assessment', 'teaching-and-learning'
        principle_number INTEGER,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        reflection_questions TEXT,  -- JSON array
        guidance TEXT,
        source_document TEXT NOT NULL
    );

    -- ABLEWA scope and sequence
    CREATE TABLE IF NOT EXISTS ablewa_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        learning_area_id TEXT NOT NULL,
        level TEXT NOT NULL,
        strand TEXT,
        content_description TEXT NOT NULL,
        source_document TEXT NOT NULL,
        verification_status TEXT DEFAULT 'unverified',
        FOREIGN KEY (learning_area_id) REFERENCES learning_areas(id)
    );

    -- SCSA <-> ACARA cross-reference mapping
    CREATE TABLE IF NOT EXISTS acara_crossref (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scsa_content_id INTEGER,
        acara_code TEXT,
        acara_file TEXT,
        match_type TEXT,     -- 'exact', 'partial', 'related', 'wa-specific'
        confidence REAL,     -- 0.0-1.0
        notes TEXT,
        FOREIGN KEY (scsa_content_id) REFERENCES content_descriptors(id)
    );

    -- AI-generated image context (clearly separated from original SCSA data)
    CREATE TABLE IF NOT EXISTS image_context (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_document TEXT NOT NULL,
        image_index INTEGER NOT NULL,
        image_path TEXT,
        context_text TEXT NOT NULL,
        model_used TEXT NOT NULL,
        related_table TEXT,
        related_record_id INTEGER,
        generated_at TEXT NOT NULL,
        is_generated INTEGER DEFAULT 1
    );

    -- Extraction metadata / audit trail
    CREATE TABLE IF NOT EXISTS extraction_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_document TEXT NOT NULL,
        extraction_timestamp TEXT NOT NULL,
        extractor_version TEXT,
        model_used TEXT,
        records_extracted INTEGER,
        verification_model TEXT,
        verification_result TEXT,
        discrepancies TEXT,  -- JSON array
        notes TEXT
    );

    -- Full-text search indexes
    CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5(
        content_description,
        elaborations,
        content='content_descriptors',
        content_rowid='id'
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS achievement_fts USING fts5(
        standard_text,
        content='achievement_standards',
        content_rowid='id'
    );

    CREATE VIRTUAL TABLE IF NOT EXISTS glossary_fts USING fts5(
        term,
        definition,
        content='glossary_terms',
        content_rowid='id'
    );

    -- Triggers to keep FTS indexes in sync
    CREATE TRIGGER IF NOT EXISTS content_fts_insert AFTER INSERT ON content_descriptors BEGIN
        INSERT INTO content_fts(rowid, content_description, elaborations)
        VALUES (new.id, new.content_description, new.elaborations);
    END;

    CREATE TRIGGER IF NOT EXISTS content_fts_delete AFTER DELETE ON content_descriptors BEGIN
        INSERT INTO content_fts(content_fts, rowid, content_description, elaborations)
        VALUES ('delete', old.id, old.content_description, old.elaborations);
    END;

    CREATE TRIGGER IF NOT EXISTS content_fts_update AFTER UPDATE ON content_descriptors BEGIN
        INSERT INTO content_fts(content_fts, rowid, content_description, elaborations)
        VALUES ('delete', old.id, old.content_description, old.elaborations);
        INSERT INTO content_fts(rowid, content_description, elaborations)
        VALUES (new.id, new.content_description, new.elaborations);
    END;

    CREATE TRIGGER IF NOT EXISTS achievement_fts_insert AFTER INSERT ON achievement_standards BEGIN
        INSERT INTO achievement_fts(rowid, standard_text) VALUES (new.id, new.standard_text);
    END;

    CREATE TRIGGER IF NOT EXISTS achievement_fts_delete AFTER DELETE ON achievement_standards BEGIN
        INSERT INTO achievement_fts(achievement_fts, rowid, standard_text)
        VALUES ('delete', old.id, old.standard_text);
    END;

    CREATE TRIGGER IF NOT EXISTS achievement_fts_update AFTER UPDATE ON achievement_standards BEGIN
        INSERT INTO achievement_fts(achievement_fts, rowid, standard_text)
        VALUES ('delete', old.id, old.standard_text);
        INSERT INTO achievement_fts(rowid, standard_text) VALUES (new.id, new.standard_text);
    END;

    CREATE TRIGGER IF NOT EXISTS glossary_fts_insert AFTER INSERT ON glossary_terms BEGIN
        INSERT INTO glossary_fts(rowid, term, definition) VALUES (new.id, new.term, new.definition);
    END;

    CREATE TRIGGER IF NOT EXISTS glossary_fts_delete AFTER DELETE ON glossary_terms BEGIN
        INSERT INTO glossary_fts(glossary_fts, rowid, term, definition)
        VALUES ('delete', old.id, old.term, old.definition);
    END;

    CREATE TRIGGER IF NOT EXISTS glossary_fts_update AFTER UPDATE ON glossary_terms BEGIN
        INSERT INTO glossary_fts(glossary_fts, rowid, term, definition)
        VALUES ('delete', old.id, old.term, old.definition);
        INSERT INTO glossary_fts(rowid, term, definition) VALUES (new.id, new.term, new.definition);
    END;

    -- Useful indexes
    CREATE INDEX IF NOT EXISTS idx_content_area_year
        ON content_descriptors(learning_area_id, year_level_id);
    CREATE INDEX IF NOT EXISTS idx_achievement_area_year
        ON achievement_standards(learning_area_id, year_level_id);
    CREATE INDEX IF NOT EXISTS idx_yld_area_year
        ON year_level_descriptions(learning_area_id, year_level_id);
    CREATE INDEX IF NOT EXISTS idx_judging_area_year
        ON judging_standards(learning_area_id, year_level_id);
    CREATE INDEX IF NOT EXISTS idx_capability_indicators_element
        ON capability_indicators(element_id, year_level_id);
    CREATE INDEX IF NOT EXISTS idx_glossary_area
        ON glossary_terms(learning_area_id);
    CREATE INDEX IF NOT EXISTS idx_ablewa_area
        ON ablewa_content(learning_area_id);
    CREATE INDEX IF NOT EXISTS idx_crossref_scsa
        ON acara_crossref(scsa_content_id);
    CREATE INDEX IF NOT EXISTS idx_crossref_acara
        ON acara_crossref(acara_code);
    CREATE INDEX IF NOT EXISTS idx_image_context_doc
        ON image_context(source_document);
    """)


def seed_year_levels(conn: sqlite3.Connection):
    """Populate year_levels reference table."""
    cur = conn.cursor()
    levels = [
        ('PP', 'Pre-primary', 0),
        ('Y1', 'Year 1', 1),
        ('Y2', 'Year 2', 2),
        ('Y3', 'Year 3', 3),
        ('Y4', 'Year 4', 4),
        ('Y5', 'Year 5', 5),
        ('Y6', 'Year 6', 6),
        ('Y7', 'Year 7', 7),
        ('Y8', 'Year 8', 8),
        ('Y9', 'Year 9', 9),
        ('Y10', 'Year 10', 10),
    ]
    cur.executemany(
        "INSERT OR IGNORE INTO year_levels (id, name, sort_order) VALUES (?, ?, ?)",
        levels
    )


def seed_learning_areas(conn: sqlite3.Connection):
    """Populate learning_areas reference table."""
    cur = conn.cursor()
    areas = [
        # Top-level learning areas
        ('english', 'English', None, 'learning-area', 2025, 'implemented'),
        ('hpe', 'Health and Physical Education', None, 'learning-area', 2025, 'implemented'),
        ('hass', 'Humanities and Social Sciences', None, 'learning-area', 2026, 'implemented'),
        ('mathematics', 'Mathematics', None, 'learning-area', 2026, 'implemented'),
        ('science', 'Science', None, 'learning-area', 2026, 'implemented'),
        ('technologies', 'Technologies', None, 'learning-area', 2026, 'implemented'),
        ('the-arts', 'The Arts', None, 'learning-area', 2026, 'familiarisation'),
        ('languages', 'Languages', None, 'learning-area', 2023, 'implemented'),

        # Technologies sub-areas
        ('tech-design', 'Design and Technologies', 'technologies', 'learning-area', 2026, 'implemented'),
        ('tech-digital', 'Digital Technologies', 'technologies', 'learning-area', 2026, 'implemented'),

        # The Arts sub-areas
        ('arts-dance', 'Dance', 'the-arts', 'learning-area', 2026, 'familiarisation'),
        ('arts-drama', 'Drama', 'the-arts', 'learning-area', 2026, 'familiarisation'),
        ('arts-media', 'Media Arts', 'the-arts', 'learning-area', 2026, 'familiarisation'),
        ('arts-music', 'Music', 'the-arts', 'learning-area', 2026, 'familiarisation'),
        ('arts-visual', 'Visual Arts', 'the-arts', 'learning-area', 2026, 'familiarisation'),

        # HASS sub-areas (used in judging standards)
        ('hass-civics', 'Civics and Citizenship', 'hass', 'learning-area', 2026, 'implemented'),
        ('hass-economics', 'Economics and Business', 'hass', 'learning-area', 2026, 'implemented'),
        ('hass-geography', 'Geography', 'hass', 'learning-area', 2026, 'implemented'),
        ('hass-history', 'History', 'hass', 'learning-area', 2026, 'implemented'),

        # Languages sub-areas
        ('lang-aboriginal-template', 'Aboriginal Languages (Template)', 'languages', 'learning-area', 2023, 'implemented'),
        ('lang-wajarri', 'Wajarri Language Revival', 'languages', 'learning-area', 2023, 'implemented'),
        ('lang-noongar', 'Noongar Language Revival', 'languages', 'learning-area', 2023, 'implemented'),

        # General capabilities
        ('gc-critical-creative', 'Critical and Creative Thinking', None, 'general-capability', None, 'implemented'),
        ('gc-digital-literacy', 'Digital Literacy', None, 'general-capability', None, 'implemented'),
        ('gc-ethical', 'Ethical Understanding', None, 'general-capability', None, 'implemented'),
        ('gc-intercultural', 'Intercultural Understanding', None, 'general-capability', None, 'implemented'),
        ('gc-literacy', 'Literacy', None, 'general-capability', None, 'implemented'),
        ('gc-numeracy', 'Numeracy', None, 'general-capability', None, 'coming-soon'),
        ('gc-personal-social', 'Personal and Social Capability', None, 'general-capability', None, 'implemented'),
    ]
    cur.executemany(
        """INSERT OR IGNORE INTO learning_areas
           (id, name, parent_id, category, implementation_year, implementation_status)
           VALUES (?, ?, ?, ?, ?, ?)""",
        areas
    )


def init_db(db_path: str = DB_PATH):
    """Initialise the database: create schema and seed reference data."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    create_schema(conn)
    seed_year_levels(conn)
    seed_learning_areas(conn)

    conn.commit()
    conn.close()
    print(f"Database initialised at {db_path}")


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else DB_PATH
    init_db(path)
