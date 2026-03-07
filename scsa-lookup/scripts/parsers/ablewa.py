#!/usr/bin/env python3
"""
ABLEWA (Abilities Based Learning Education WA) Scope and Sequence Parser

Extracts curriculum content from ABLEWA DOCX files.
ABLEWA uses Stages A–D instead of year levels.
Tables have strands as row labels and stages as columns.
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_docx import extract_docx


AREA_PATTERNS = [
    (r'English_ABLEWA', 'english'),
    (r'Humanities.*Social.*ABLEWA', 'hass'),
    (r'Mathematics_ABLEWA', 'mathematics'),
    (r'Science_ABLEWA', 'science'),
    (r'Technologies_ABLEWA', 'technologies'),
    (r'The_Arts_ABLEWA|Arts_ABLEWA', 'the-arts'),
]


def identify_learning_area(filename: str) -> str:
    for pattern, area_id in AREA_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return area_id
    return 'unknown'


def parse_ablewa(filepath: str) -> list:
    """Parse an ABLEWA scope and sequence DOCX file.

    Returns list of dicts with:
      - learning_area_id
      - level (Stage A, Stage B, Stage C, Stage D)
      - strand (from table header row or heading context)
      - content_description
      - source_document
    """
    data = extract_docx(filepath)
    filename = data['filename']
    learning_area_id = identify_learning_area(filename)
    body_elements = data['body_elements']

    records = []
    current_mode = None  # e.g., "Mode | Reading and Viewing"

    for elem in body_elements:
        if elem['type'] == 'paragraph':
            style = elem.get('style', '')
            text = elem['text'].strip()
            if 'Heading' in style and text:
                current_mode = text

        elif elem['type'] == 'table':
            rows = elem['rows']
            if len(rows) < 3:
                continue

            # Determine if this is a content table or achievement standard table
            header_row0 = rows[0]
            header_row1 = rows[1] if len(rows) > 1 else []

            # Achievement standard tables have different structure — skip for now
            if any('achievement' in c.lower() for c in header_row0):
                continue

            # Content tables: row 0 is strand name (merged), row 1 has stage headers
            strand_name = header_row0[0].strip() if header_row0 else None

            # Find stage columns from row 1
            stage_columns = {}
            for ci, cell in enumerate(header_row1):
                clean = cell.strip()
                if re.match(r'Stage\s+[A-D]', clean, re.IGNORECASE):
                    stage_columns[ci] = clean

            if not stage_columns:
                # Try row 0 as stage headers directly
                for ci, cell in enumerate(header_row0):
                    clean = cell.strip()
                    if re.match(r'Stage\s+[A-D]', clean, re.IGNORECASE):
                        stage_columns[ci] = clean
                if stage_columns:
                    # Strand is from the mode heading
                    strand_name = current_mode

            if not stage_columns:
                # Check for "Stage X" embedded in row 0 text (e.g., "The Arts: Stage A")
                # All columns share the same stage; subjects are in row 1
                for cell in header_row0:
                    m = re.search(r'Stage\s+([A-D])', cell.strip(), re.IGNORECASE)
                    if m:
                        stage_label = f"Stage {m.group(1).upper()}"
                        # Build subject columns from row 1 (skip col 0 which is the sub-strand label)
                        subject_cols = {}
                        for sci, scell in enumerate(header_row1):
                            subj = scell.strip()
                            if subj:
                                subject_cols[sci] = subj

                        # Parse rows: col 0 = sub-strand, other cols = content per subject
                        for ri in range(2, len(rows)):
                            row = rows[ri]
                            sub_strand = row[0].strip() if row else ''
                            for sci, subject in subject_cols.items():
                                if sci >= len(row):
                                    continue
                                text = row[sci].strip()
                                if not text:
                                    continue
                                full_strand = f"{subject} > {sub_strand}" if sub_strand else subject
                                records.append({
                                    'learning_area_id': learning_area_id,
                                    'level': stage_label,
                                    'strand': full_strand,
                                    'content_description': text,
                                    'source_document': filename,
                                })
                        break  # Already processed this table
                continue  # Skip normal processing for this table format

            if not stage_columns:
                continue

            # Parse content rows
            start_row = 2 if len(header_row1) > 0 and stage_columns else 1
            for ri in range(start_row, len(rows)):
                row = rows[ri]
                # Column 0 is usually the sub-strand label
                sub_strand = row[0].strip() if row else ''

                for ci, stage in stage_columns.items():
                    if ci >= len(row):
                        continue
                    text = row[ci].strip()
                    if not text:
                        continue

                    full_strand = strand_name
                    if current_mode and strand_name:
                        full_strand = f"{current_mode} > {strand_name}"
                    elif current_mode:
                        full_strand = current_mode

                    if sub_strand and sub_strand != text:
                        full_strand = f"{full_strand} > {sub_strand}" if full_strand else sub_strand

                    records.append({
                        'learning_area_id': learning_area_id,
                        'level': stage,
                        'strand': full_strand,
                        'content_description': text,
                        'source_document': filename,
                    })

    return records


def parse_all_ablewa(raw_dir: str) -> list:
    """Parse all ABLEWA files in the curriculum directory."""
    all_records = []
    curriculum_dir = os.path.join(raw_dir, 'curriculum')

    for fname in sorted(os.listdir(curriculum_dir)):
        if 'ABLEWA' not in fname:
            continue
        fpath = os.path.join(curriculum_dir, fname)
        if not fname.lower().endswith('.docx'):
            continue
        try:
            records = parse_ablewa(fpath)
            all_records.extend(records)
            print(f"  {fname}: {len(records)} records", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR {fname}: {e}", file=sys.stderr)

    return all_records


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: ablewa.py <file.docx | raw_dir>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        results = parse_all_ablewa(path)
    else:
        results = parse_ablewa(path)

    print(json.dumps(results, indent=2, ensure_ascii=False))
