#!/usr/bin/env python3
"""
Scope and Sequence Parser

Extracts curriculum content descriptors from SCSA scope and sequence DOCX files.
These are the core curriculum documents containing what must be taught at each year level.

Document structure (typical):
- Preamble (title, copyright, TOC)
- Overview / guide sections
- Tables organised by strand/sub-strand with year levels as columns
  - P-6 tables: 7 columns (Pre-primary, Year 1, ..., Year 6)
  - 7-10 tables: 4 columns (Year 7, Year 8, Year 9, Year 10)
- Each cell contains the content descriptor text for that year level + strand
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_docx import extract_docx


# Year level header -> DB year_level_id
YEAR_LEVEL_MAP = {
    'pre-primary': 'PP', 'pre primary': 'PP', 'pp': 'PP',
    'year 1': 'Y1', 'year 2': 'Y2', 'year 3': 'Y3', 'year 4': 'Y4',
    'year 5': 'Y5', 'year 6': 'Y6', 'year 7': 'Y7', 'year 8': 'Y8',
    'year 9': 'Y9', 'year 10': 'Y10',
}

# Filename patterns -> learning_area_id
AREA_PATTERNS = [
    (r'English_Scope', 'english'),
    (r'HPE_Scope', 'hpe'),
    (r'Humanities.*Social.*Sciences.*Scope', 'hass'),
    (r'Mathematics_Scope.*P-6', 'mathematics'),
    (r'Mathematics_Scope.*7-10', 'mathematics'),
    (r'Science.*Scope', 'science'),
    (r'Technologies.*Design.*Scope', 'tech-design'),
    (r'Technologies.*Digital.*Scope', 'tech-digital'),
    (r'The-Arts_Dance.*Scope.*mandated', 'arts-dance'),
    (r'The-Arts_Dance_Scope', 'arts-dance'),
    (r'The-Arts_Drama.*Scope.*mandated', 'arts-drama'),
    (r'The-Arts_Drama_Scope', 'arts-drama'),
    (r'The-Arts_Media.*Scope.*mandated', 'arts-media'),
    (r'The-Arts_Media.*Scope', 'arts-media'),
    (r'The-Arts_Music.*Scope.*mandated', 'arts-music'),
    (r'The-Arts_Music.*Scope', 'arts-music'),
    (r'The-Arts_Visual.*Scope.*mandated', 'arts-visual'),
    (r'The-Arts_Visual.*Scope', 'arts-visual'),
    (r'Languages.*Aboriginal.*Template', 'lang-aboriginal-template'),
    (r'Languages.*Wajarri', 'lang-wajarri'),
    (r'Noongar', 'lang-noongar'),
]


def identify_learning_area(filename: str) -> str:
    """Map a filename to its learning area ID."""
    for pattern, area_id in AREA_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return area_id
    return 'unknown'


def is_mandated_content(filename: str) -> bool:
    """Check if a file is the mandated curriculum content version."""
    return 'mandated' in filename.lower()


def normalise_year_level(text: str) -> str:
    """Convert year level header text to a DB ID.
    Only matches short header-like strings (not content descriptor text)."""
    clean = text.strip()
    # Reject anything too long to be a year level header
    if len(clean) > 30:
        return None
    clean_lower = clean.lower()
    # Direct match
    if clean_lower in YEAR_LEVEL_MAP:
        return YEAR_LEVEL_MAP[clean_lower]
    # Try with common variations — must be a close match, not substring
    for key, val in YEAR_LEVEL_MAP.items():
        if clean_lower == key or clean_lower.startswith(key + ' ') or clean_lower.endswith(' ' + key):
            return val
    return None


def extract_strand_context(body_elements: list, table_index: int) -> dict:
    """Look at paragraphs preceding a table to determine strand/sub-strand context.
    Returns {'strand': ..., 'sub_strand': ...}"""
    strand = None
    sub_strand = None

    # Walk backwards from the table position to find heading context
    table_pos = None
    elem_idx = 0
    for i, elem in enumerate(body_elements):
        if elem['type'] == 'table' and elem.get('index') == table_index:
            table_pos = i
            break

    if table_pos is None:
        return {'strand': strand, 'sub_strand': sub_strand}

    # Look at preceding paragraphs for strand headers
    for i in range(table_pos - 1, max(table_pos - 8, -1), -1):
        elem = body_elements[i]
        if elem['type'] != 'paragraph':
            continue
        style = elem.get('style', '')
        text = elem['text'].strip()

        if not text:
            continue

        # Skip TOC, preamble
        if style.startswith('toc') or style.startswith('SCSA T'):
            continue

        # Heading styles indicate strand/sub-strand
        if 'Heading 1' in style or style == 'SCSA Heading 1':
            strand = text
            break
        elif 'Heading 2' in style or style == 'SCSA Heading 2':
            sub_strand = text
        elif 'Heading 3' in style or style == 'SCSA Heading 3':
            if not sub_strand:
                sub_strand = text
        elif any(kw in text.lower() for kw in ['strand:', 'sub-strand:']):
            # Some docs use explicit labels
            if 'strand:' in text.lower() and 'sub' not in text.lower():
                strand = re.sub(r'(?i)strand:\s*', '', text).strip()
            elif 'sub-strand:' in text.lower() or 'sub strand:' in text.lower():
                sub_strand = re.sub(r'(?i)sub-?strand:\s*', '', text).strip()

    return {'strand': strand, 'sub_strand': sub_strand}


def parse_content_table(table: dict, context: dict, filename: str, learning_area_id: str, is_mandated: bool) -> list:
    """Parse a single content table into content descriptor records.

    Tables have year levels as column headers (row 0) and content descriptors in subsequent rows.
    """
    rows = table['rows']
    if len(rows) < 2:
        return []

    # Identify year level columns from header row
    header = rows[0]
    year_columns = {}  # col_index -> year_level_id
    for ci, cell_text in enumerate(header):
        yl = normalise_year_level(cell_text)
        if yl:
            year_columns[ci] = yl

    if not year_columns:
        return []

    records = []
    for ri in range(1, len(rows)):
        row = rows[ri]
        for ci, year_id in year_columns.items():
            if ci >= len(row):
                continue
            text = row[ci].strip()
            if not text or text.lower() == 'no content':
                continue
            # Skip if it's just a repeat of the header
            if normalise_year_level(text):
                continue

            records.append({
                'learning_area_id': learning_area_id,
                'year_level_id': year_id,
                'strand': context.get('strand'),
                'sub_strand': context.get('sub_strand'),
                'content_description': text,
                'elaborations': None,
                'source_document': filename,
                'is_mandated': is_mandated,
            })

    return records


def parse_scope_sequence(filepath: str) -> list:
    """Parse a scope and sequence DOCX file into content descriptor records."""
    data = extract_docx(filepath)
    filename = data['filename']
    learning_area_id = identify_learning_area(filename)
    mandated = is_mandated_content(filename)
    body_elements = data['body_elements']

    all_records = []

    # Track current strand context from headings
    current_strand = None
    current_sub_strand = None

    for elem in body_elements:
        if elem['type'] == 'paragraph':
            style = elem.get('style', '')
            text = elem['text'].strip()

            # Track heading context for strand identification
            if 'Heading 1' in style or 'SCSA Heading 1' in style:
                # Reset sub-strand when a new strand heading appears
                current_strand = text
                current_sub_strand = None
            elif 'Heading 2' in style or 'SCSA Heading 2' in style:
                current_sub_strand = text
            elif 'Heading 3' in style or 'SCSA Heading 3' in style:
                # Some documents use Heading 3 for strand labels (e.g., DT "Strand: Design thinking skills")
                if text.lower().startswith('strand:'):
                    current_strand = text
                    current_sub_strand = None
                else:
                    current_sub_strand = text

        elif elem['type'] == 'table':
            table = elem
            rows = table['rows']
            if len(rows) < 2:
                continue

            # Check if this is a content table (has year level headers)
            header = rows[0]
            has_year_headers = any(normalise_year_level(c) for c in header)

            if not has_year_headers:
                # Could be a strand overview table (strands as columns)
                # e.g., Science has overview tables listing sub-strands
                continue

            context = {
                'strand': current_strand,
                'sub_strand': current_sub_strand,
            }

            records = parse_content_table(table, context, filename, learning_area_id, mandated)
            all_records.extend(records)

    return all_records


def parse_all_scope_sequence(raw_dir: str) -> list:
    """Parse all scope and sequence files in a directory."""
    all_records = []
    curriculum_dir = os.path.join(raw_dir, 'curriculum')

    for fname in sorted(os.listdir(curriculum_dir)):
        fpath = os.path.join(curriculum_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if 'scope' not in fname.lower() and 'Scope' not in fname:
            continue
        if fname.lower().endswith('.docx'):
            try:
                records = parse_scope_sequence(fpath)
                all_records.extend(records)
                print(f"  {fname}: {len(records)} descriptors", file=sys.stderr)
            except Exception as e:
                print(f"  ERROR {fname}: {e}", file=sys.stderr)

    return all_records


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: scope_sequence.py <file.docx | raw_dir>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        results = parse_all_scope_sequence(path)
    else:
        results = parse_scope_sequence(path)

    print(json.dumps(results, indent=2, ensure_ascii=False))
