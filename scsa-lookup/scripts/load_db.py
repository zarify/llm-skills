#!/usr/bin/env python3
"""
load_db.py — Load all parsed curriculum data into scsa.db

Usage: python scripts/load_db.py [--reset]

Runs all parsers and loads results into the SQLite database.
Use --reset to reinitialise the database first.
"""

import json
import os
import re
import sqlite3
import sys
import glob
from datetime import datetime

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from parsers.scope_sequence import parse_all_scope_sequence
from parsers.achievement_standards import parse_all_achievement_standards
from parsers.year_level_descriptions import parse_year_level_descriptions
from parsers.glossary import parse_glossary
from parsers.principles import parse_principles
from parsers.judging_standards import parse_judging_standards
from parsers.ablewa import parse_all_ablewa
from parsers.general_capabilities import parse_all_capabilities


DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'scsa.db')
RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'raw')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def log_extraction(conn, source_doc, records_count, parser_name):
    conn.execute(
        "INSERT INTO extraction_log (source_document, extraction_timestamp, extractor_version, records_extracted, notes) VALUES (?, ?, ?, ?, ?)",
        (source_doc, datetime.now().isoformat(), '1.0.0', records_count, f'Parser: {parser_name}')
    )


def load_scope_sequence(conn):
    """Load scope & sequence content descriptors."""
    print("\n📚 Loading Scope & Sequence...")
    records = parse_all_scope_sequence(RAW_DIR)

    # Deduplicate: Arts have mandated + full S&S files; prefer mandated
    seen = {}  # key -> index in deduped
    deduped = []
    for r in records:
        key = (r['learning_area_id'], r['year_level_id'], r['content_description'][:80])
        if key not in seen:
            seen[key] = len(deduped)
            deduped.append(r)
        elif 'mandated' in r.get('source_document', '').lower():
            # Replace with mandated version
            deduped[seen[key]] = r

    count = 0
    for r in deduped:
        if r['learning_area_id'] == 'unknown':
            continue
        try:
            conn.execute(
                """INSERT INTO content_descriptors
                   (learning_area_id, year_level_id, strand, sub_strand, content_description, source_document, is_mandated)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (r['learning_area_id'], r['year_level_id'], r.get('strand'),
                 r.get('sub_strand'), r['content_description'],
                 r['source_document'], 1 if 'mandated' in r.get('source_document', '').lower() else 0)
            )
            count += 1
        except sqlite3.IntegrityError as e:
            print(f"  ⚠ Skip: {e}", file=sys.stderr)

    conn.commit()
    log_extraction(conn, 'scope_sequence/*', count, 'scope_sequence')
    conn.commit()
    print(f"  ✅ {count} content descriptors loaded (from {len(records)} raw, {len(records)-len(deduped)} duplicates removed)")
    return count


def load_achievement_standards(conn):
    """Load achievement standards."""
    print("\n📋 Loading Achievement Standards...")
    records = parse_all_achievement_standards(RAW_DIR)
    count = 0
    for r in records:
        conn.execute(
            """INSERT INTO achievement_standards
               (learning_area_id, year_level_id, standard_text, source_document)
               VALUES (?, ?, ?, ?)""",
            (r['learning_area_id'], r['year_level_id'], r['standard_text'], r['source_document'])
        )
        count += 1
    conn.commit()
    log_extraction(conn, 'achievement_standards/*', count, 'achievement_standards')
    conn.commit()
    print(f"  ✅ {count} achievement standards loaded")
    return count


def load_year_level_descriptions(conn):
    """Load year level descriptions."""
    print("\n📝 Loading Year Level Descriptions...")
    curriculum_dir = os.path.join(RAW_DIR, 'curriculum')
    count = 0
    for fname in sorted(os.listdir(curriculum_dir)):
        if 'year-level' not in fname.lower() and 'year_level' not in fname.lower():
            continue
        if 'ablewa' in fname.lower():
            continue
        if not fname.lower().endswith('.docx'):
            continue
        fpath = os.path.join(curriculum_dir, fname)
        records = parse_year_level_descriptions(fpath)
        for r in records:
            conn.execute(
                """INSERT INTO year_level_descriptions
                   (learning_area_id, year_level_id, description_text, source_document)
                   VALUES (?, ?, ?, ?)""",
                (r['learning_area_id'], r['year_level_id'], r['description_text'], r['source_document'])
            )
            count += 1
    conn.commit()
    log_extraction(conn, 'year_level_descriptions/*', count, 'year_level_descriptions')
    conn.commit()
    print(f"  ✅ {count} year level descriptions loaded")
    return count


def load_glossary(conn):
    """Load glossary terms."""
    print("\n📖 Loading Glossary Terms...")
    glossary_dir = os.path.join(RAW_DIR, 'glossary')
    count = 0
    for fname in sorted(os.listdir(glossary_dir)):
        if not fname.lower().endswith('.docx'):
            continue
        fpath = os.path.join(glossary_dir, fname)
        records = parse_glossary(fpath)
        for r in records:
            conn.execute(
                """INSERT INTO glossary_terms
                   (learning_area_id, term, definition, source_document)
                   VALUES (?, ?, ?, ?)""",
                (r['learning_area_id'], r['term'], r['definition'], r['source_document'])
            )
            count += 1
    conn.commit()
    log_extraction(conn, 'glossary/*', count, 'glossary')
    conn.commit()
    print(f"  ✅ {count} glossary terms loaded")
    return count


def load_judging_standards(conn):
    """Load judging standards."""
    print("\n⚖️ Loading Judging Standards...")
    js_dir = os.path.join(RAW_DIR, 'judging-standards')
    count = 0
    errors = 0
    for fname in sorted(os.listdir(js_dir)):
        if not fname.lower().endswith('.docx'):
            continue
        fpath = os.path.join(js_dir, fname)
        try:
            records = parse_judging_standards(fpath)
            for r in records:
                conn.execute(
                    """INSERT INTO judging_standards
                       (learning_area_id, year_level_id, strand, grade, descriptor_text, source_document, is_best_effort)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (r['learning_area_id'], r['year_level_id'], r.get('strand'),
                     r['grade'], r['descriptor_text'], r['source_document'],
                     1 if r.get('is_best_effort') else 0)
                )
                count += 1
        except Exception as e:
            errors += 1
            print(f"  ⚠ Error parsing {fname}: {e}", file=sys.stderr)
    conn.commit()
    log_extraction(conn, 'judging_standards/*', count, 'judging_standards')
    conn.commit()
    print(f"  ✅ {count} judging standards loaded ({errors} file errors)")
    return count


def load_principles(conn):
    """Load teaching and assessment principles."""
    print("\n📐 Loading Principles...")
    principles_dir = os.path.join(RAW_DIR, 'principles')
    count = 0
    for fname in sorted(os.listdir(principles_dir)):
        if not fname.endswith('.txt'):
            continue
        fpath = os.path.join(principles_dir, fname)
        records = parse_principles(fpath)
        for r in records:
            conn.execute(
                """INSERT INTO principles
                   (category, principle_number, title, description, reflection_questions, guidance, source_document)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (r['category'], r.get('principle_number'), r['title'], r['description'],
                 json.dumps(r.get('reflection_questions', [])) if r.get('reflection_questions') else None,
                 r.get('guidance'), r['source_document'])
            )
            count += 1
    conn.commit()
    log_extraction(conn, 'principles/*', count, 'principles')
    conn.commit()
    print(f"  ✅ {count} principles loaded")
    return count


def load_ablewa(conn):
    """Load ABLEWA content."""
    print("\n♿ Loading ABLEWA Content...")
    records = parse_all_ablewa(RAW_DIR)
    count = 0
    for r in records:
        conn.execute(
            """INSERT INTO ablewa_content
               (learning_area_id, level, strand, content_description, source_document)
               VALUES (?, ?, ?, ?, ?)""",
            (r['learning_area_id'], r['level'], r.get('strand'),
             r['content_description'], r['source_document'])
        )
        count += 1
    conn.commit()
    log_extraction(conn, 'ablewa/*', count, 'ablewa')
    conn.commit()
    print(f"  ✅ {count} ABLEWA records loaded")
    return count


def load_general_capabilities(conn):
    """Load general capabilities and their indicators."""
    print("\n🎯 Loading General Capabilities...")
    caps = parse_all_capabilities(RAW_DIR)
    elem_count = 0
    ind_count = 0

    for cap in caps:
        # Upsert capability
        conn.execute(
            """INSERT OR REPLACE INTO general_capabilities (id, name, description, source_document)
               VALUES (?, ?, ?, ?)""",
            (cap['capability_id'], cap['capability_name'], cap.get('description'), cap['source_document'])
        )

        # Insert elements and sub-elements
        for elem in cap['elements']:
            conn.execute(
                """INSERT INTO capability_elements (capability_id, element_name, description)
                   VALUES (?, ?, ?)""",
                (cap['capability_id'], elem['element_name'], None)
            )
            elem_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            elem_count += 1

            for sub in elem['sub_elements']:
                if sub != elem['element_name']:
                    conn.execute(
                        """INSERT INTO capability_elements (capability_id, element_name, sub_element_name, description)
                           VALUES (?, ?, ?, ?)""",
                        (cap['capability_id'], elem['element_name'], sub, None)
                    )

        # Insert indicators
        for ind in cap['indicators']:
            # Find element_id
            row = conn.execute(
                "SELECT id FROM capability_elements WHERE capability_id = ? AND element_name = ? AND sub_element_name IS NULL LIMIT 1",
                (ind['capability_id'], ind['element_name'])
            ).fetchone()
            if not row:
                row = conn.execute(
                    "SELECT id FROM capability_elements WHERE capability_id = ? AND element_name = ? LIMIT 1",
                    (ind['capability_id'], ind['element_name'])
                ).fetchone()
            if not row:
                continue
            element_id = row[0]

            conn.execute(
                """INSERT INTO capability_indicators
                   (element_id, year_level_id, level_name, indicator_text)
                   VALUES (?, ?, ?, ?)""",
                (element_id, ind['year_level_id'], ind['level_name'], ind['indicator_text'])
            )
            ind_count += 1

    conn.commit()
    log_extraction(conn, 'general_capabilities/*', ind_count, 'general_capabilities')
    conn.commit()
    print(f"  ✅ {len(caps)} capabilities, {elem_count} elements, {ind_count} indicators loaded")
    return ind_count


def rebuild_fts(conn):
    """Rebuild FTS indexes."""
    print("\n🔍 Rebuilding FTS indexes...")
    conn.execute("INSERT INTO content_fts(content_fts) VALUES('rebuild')")
    conn.execute("INSERT INTO achievement_fts(achievement_fts) VALUES('rebuild')")
    conn.execute("INSERT INTO glossary_fts(glossary_fts) VALUES('rebuild')")
    conn.commit()
    print("  ✅ FTS indexes rebuilt")


def print_summary(conn):
    """Print database summary."""
    print("\n" + "=" * 60)
    print("📊 Database Summary")
    print("=" * 60)
    tables = [
        ('content_descriptors', 'Content Descriptors'),
        ('achievement_standards', 'Achievement Standards'),
        ('year_level_descriptions', 'Year Level Descriptions'),
        ('glossary_terms', 'Glossary Terms'),
        ('judging_standards', 'Judging Standards'),
        ('principles', 'Principles'),
        ('ablewa_content', 'ABLEWA Content'),
        ('general_capabilities', 'General Capabilities'),
        ('capability_elements', 'Capability Elements'),
        ('capability_indicators', 'Capability Indicators'),
    ]
    total = 0
    for table, label in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {label:30s} {count:6d}")
        total += count
    print(f"  {'─' * 37}")
    print(f"  {'TOTAL':30s} {total:6d}")
    print(f"\n  Database size: {os.path.getsize(DB_PATH) / 1024:.0f} KB")


def main():
    reset = '--reset' in sys.argv

    if reset:
        print("🔄 Resetting database...")
        from init_db import init_db, DB_PATH as INIT_DB_PATH
        init_db(INIT_DB_PATH)

    conn = get_db()

    # Clear content tables (keep reference data)
    content_tables = [
        'content_descriptors', 'achievement_standards', 'year_level_descriptions',
        'glossary_terms', 'judging_standards', 'principles', 'ablewa_content',
        'capability_indicators', 'capability_elements', 'general_capabilities',
        'extraction_log'
    ]
    for table in content_tables:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()

    print("🚀 Loading all curriculum data into scsa.db")
    print("=" * 60)

    totals = {}
    totals['scope_sequence'] = load_scope_sequence(conn)
    totals['achievement_standards'] = load_achievement_standards(conn)
    totals['year_level_descriptions'] = load_year_level_descriptions(conn)
    totals['glossary'] = load_glossary(conn)
    totals['judging_standards'] = load_judging_standards(conn)
    totals['principles'] = load_principles(conn)
    totals['ablewa'] = load_ablewa(conn)
    totals['general_capabilities'] = load_general_capabilities(conn)

    rebuild_fts(conn)
    print_summary(conn)
    conn.close()

    print("\n✅ Database load complete!")


if __name__ == '__main__':
    main()
