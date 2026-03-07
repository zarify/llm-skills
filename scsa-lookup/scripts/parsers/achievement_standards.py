#!/usr/bin/env python3
"""
Achievement Standards Parser

Extracts achievement standard text from SCSA achievement standard DOCX files.

Document structure (all files use paragraph-based format):
- Preamble (title, copyright, optional TOC)
- Overview heading + overview paragraphs
- For each year level: a Heading 1 (e.g., "Pre-primary", "Year 1") followed by
  one or more Normal paragraphs containing the achievement standard prose
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_docx import extract_docx


YEAR_LEVEL_MAP = {
    'pre-primary': 'PP', 'pre primary': 'PP', 'pp': 'PP',
    'year 1': 'Y1', 'year 2': 'Y2', 'year 3': 'Y3', 'year 4': 'Y4',
    'year 5': 'Y5', 'year 6': 'Y6', 'year 7': 'Y7', 'year 8': 'Y8',
    'year 9': 'Y9', 'year 10': 'Y10',
}

AREA_PATTERNS = [
    (r'English_Achievement', 'english'),
    (r'HPE_Achievement', 'hpe'),
    (r'Humanities.*Social.*Achievement', 'hass'),
    (r'Mathematics_Achievement', 'mathematics'),
    (r'Science.*Achievement', 'science'),
    (r'Technologies.*Design.*Achievement', 'tech-design'),
    (r'Technologies.*Digital.*Achievement', 'tech-digital'),
    (r'The-Arts_Dance.*Achievement', 'arts-dance'),
    (r'The-Arts_Drama.*Achievement', 'arts-drama'),
    (r'The-Arts_Media.*Achievement', 'arts-media'),
    (r'The-Arts_Music.*Achievement', 'arts-music'),
    (r'The-Arts_Visual.*Achievement', 'arts-visual'),
]

# Preamble/boilerplate markers to skip
SKIP_HEADINGS = {'overview', 'contents'}
SKIP_STYLE_PREFIXES = ('toc ', 'SCSA TOC', 'SCSA Title')


def identify_learning_area(filename: str) -> str:
    """Map a filename to its learning area ID."""
    for pattern, area_id in AREA_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return area_id
    return 'unknown'


def normalise_year_level(text: str) -> str | None:
    """Convert year level heading text to a DB ID (e.g. 'PP', 'Y1').
    Returns None if the text is not a year level heading."""
    clean = text.strip()
    if len(clean) > 30:
        return None
    key = clean.lower()
    if key in YEAR_LEVEL_MAP:
        return YEAR_LEVEL_MAP[key]
    for k, v in YEAR_LEVEL_MAP.items():
        if key == k or key.startswith(k + ' ') or key.endswith(' ' + k):
            return v
    return None


def _is_heading(style: str) -> bool:
    """Return True if the style represents a Heading 1."""
    return 'Heading 1' in style or 'SCSA Heading 1' in style


def _is_preamble(style: str, text: str) -> bool:
    """Return True if this element is preamble/boilerplate to skip."""
    if any(style.startswith(p) for p in SKIP_STYLE_PREFIXES):
        return True
    return False


def parse_achievement_standards(filepath: str) -> list[dict]:
    """Parse an achievement standard DOCX file into records.

    Returns a list of dicts with keys:
      learning_area_id, year_level_id, standard_text, source_document
    """
    data = extract_docx(filepath)
    filename = data['filename']
    learning_area_id = identify_learning_area(filename)
    body_elements = data['body_elements']

    records = []
    current_year = None
    paragraphs: list[str] = []

    def _flush():
        nonlocal current_year, paragraphs
        if current_year and paragraphs:
            records.append({
                'learning_area_id': learning_area_id,
                'year_level_id': current_year,
                'standard_text': '\n'.join(paragraphs),
                'source_document': filename,
            })
        paragraphs = []

    for elem in body_elements:
        if elem['type'] != 'paragraph':
            continue

        style = elem.get('style', '')
        text = elem['text'].strip()

        if not text:
            continue

        if _is_preamble(style, text):
            continue

        if _is_heading(style):
            year_id = normalise_year_level(text)
            if year_id:
                _flush()
                current_year = year_id
            elif text.lower() in SKIP_HEADINGS:
                # Overview section — flush any prior year and ignore
                _flush()
                current_year = None
            continue

        # Collect content paragraphs under a year level heading
        if current_year:
            # Skip the standalone "By the end of the year:" lead-in,
            # but keep paragraphs where it's the start of the actual standard text
            if re.match(r'^By the end of (the year|Pre-primary|Year \d+)[:\s]*$', text):
                continue
            paragraphs.append(text)

    # Flush final year level
    _flush()

    return records


def parse_all_achievement_standards(raw_dir: str) -> list[dict]:
    """Parse all achievement standard files in a directory."""
    all_records = []
    curriculum_dir = os.path.join(raw_dir, 'curriculum')

    for fname in sorted(os.listdir(curriculum_dir)):
        fpath = os.path.join(curriculum_dir, fname)
        if not os.path.isfile(fpath):
            continue
        if not fname.lower().endswith('.docx'):
            continue
        if 'Achievement' not in fname and 'achievement' not in fname:
            continue
        if 'ABLEWA' in fname:
            continue

        try:
            records = parse_achievement_standards(fpath)
            all_records.extend(records)
            print(f"  {fname}: {len(records)} standards", file=sys.stderr)
        except Exception as e:
            print(f"  ERROR {fname}: {e}", file=sys.stderr)

    return all_records


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: achievement_standards.py <file.docx | raw_dir>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        results = parse_all_achievement_standards(path)
    else:
        results = parse_achievement_standards(path)

    print(json.dumps(results, indent=2, ensure_ascii=False))
