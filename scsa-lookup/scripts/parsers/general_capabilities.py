#!/usr/bin/env python3
"""
General Capabilities PDF Parser

Extracts capability elements, sub-elements, and learning continuum indicators
from SCSA General Capabilities PDF documents.

Structure:
- Each capability has multiple elements (e.g., "Understanding ethical concepts and perspectives")
- Each element has 2-3 sub-elements
- Each sub-element has 6 progression levels (L1-L6)
- L1-L6 map to year level bands: PP, Y1-2, Y3-4, Y5-6, Y7-8, Y9-10
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_pdf import extract_pdf


# Level-to-year-level-band mapping (standard ACARA general capabilities progression)
LEVEL_YEAR_MAP = {
    'L1': ['PP'],
    'L1a': ['PP'],
    'L1b': ['PP'],
    'L1c': ['PP'],
    'L2': ['Y1', 'Y2'],
    'L3': ['Y3', 'Y4'],
    'L4': ['Y5', 'Y6'],
    'L5': ['Y7', 'Y8'],
    'L6': ['Y9', 'Y10'],
}

CAPABILITY_PATTERNS = [
    (r'Critical.*Creative', 'gc-critical-creative', 'Critical and Creative Thinking'),
    (r'Digital.*[Ll]iteracy', 'gc-digital-literacy', 'Digital Literacy'),
    (r'Ethical.*[Uu]nderstanding', 'gc-ethical', 'Ethical Understanding'),
    (r'Intercultural.*[Uu]nderstanding', 'gc-intercultural', 'Intercultural Understanding'),
    (r'(?<!Digital\s)Literacy', 'gc-literacy', 'Literacy'),
    (r'Personal.*Social', 'gc-personal-social', 'Personal and Social Capability'),
]


def identify_capability(filename: str) -> tuple:
    """Returns (capability_id, capability_name) from filename."""
    for pattern, cap_id, cap_name in CAPABILITY_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return cap_id, cap_name
    return 'unknown', 'Unknown'


def extract_element_name_from_text(page_text: str) -> str:
    """Try to extract the element/table title from page text."""
    # Look for "Table N\n<title>" pattern
    m = re.search(r'Table\s+\d+\s*\n\s*(.+?)(?:\n|Sub-elements)', page_text)
    if m:
        return m.group(1).strip()
    # Look for text before "Sub-elements"
    m = re.search(r'^(.+?)\s*Sub-elements', page_text, re.MULTILINE)
    if m:
        name = m.group(1).strip()
        # Clean up common prefixes
        name = re.sub(r'^(General Capabilities|Table\s+\d+)\s*', '', name).strip()
        if name and len(name) < 100:
            return name
    return None


def parse_capability_table(table, element_name: str, capability_id: str,
                           capability_name: str, filename: str) -> list:
    """Parse a single capability progression table.

    Expected structure:
      Row 0: ["Sub-elements", "", ""]
      Row 1: [sub_element_1, sub_element_2, sub_element_3]
      Rows 2-7: L1-L6 indicator text per sub-element
    """
    rows = table['rows']
    num_rows = table['num_rows']
    num_cols = table['num_cols']

    # Validate structure
    if num_rows < 4 or num_cols < 2:
        return []

    # Check if row 0 has "Sub-elements" header
    if not any('sub-element' in str(c).lower() for c in rows[0]):
        return []

    # Extract sub-element names from row 1
    sub_elements = []
    for ci in range(num_cols):
        cell = rows[1][ci] if ci < len(rows[1]) else ''
        name = str(cell).strip().replace('\n', ' ') if cell else ''
        sub_elements.append(name)

    records = []

    # Rows 2 onwards are levels L1-L6
    for ri in range(2, min(num_rows, 8)):
        level_num = ri - 1  # Row 2 = L1, Row 3 = L2, etc.
        level_key = f'L{level_num}'
        year_levels = LEVEL_YEAR_MAP.get(level_key, [])

        for ci in range(num_cols):
            cell = rows[ri][ci] if ci < len(rows[ri]) else ''
            text = str(cell).strip().replace('\n', ' ') if cell else ''
            if not text:
                continue

            sub_element_name = sub_elements[ci] if ci < len(sub_elements) else ''

            for year_level_id in year_levels:
                records.append({
                    'capability_id': capability_id,
                    'capability_name': capability_name,
                    'element_name': element_name or 'Unknown',
                    'sub_element_name': sub_element_name,
                    'level_name': level_key,
                    'year_level_id': year_level_id,
                    'indicator_text': text,
                    'source_document': filename,
                })

    return records


def _normalise_literacy_level(raw: str) -> str:
    """Normalise PDF-garbled level labels like 'LL11cc' → 'L1c', 'LL11b' → 'L1b'."""
    raw = raw.strip()
    # Fix doubled characters from PDF rendering
    raw = re.sub(r'LL(\d)\1', r'L\1', raw)  # LL11 → L1
    raw = re.sub(r'(\d)([a-c])\2', r'\1\2', raw)  # 1cc → 1c
    return raw


def parse_literacy_capability(data: dict, filename: str, capability_id: str,
                              capability_name: str, description: str) -> dict:
    """Parse the Literacy general capability PDF (different structure from others).

    Literacy uses text-based level markers (L1a, L1b, L1c, L2-L6) embedded in page text
    rather than structured sub-element tables.
    """
    # Level marker regex — matches L1a, L1b, L1c, L2-L6 and garbled versions
    level_pattern = re.compile(r'^(LL?\d+[abc]?)\s+', re.MULTILINE)

    all_indicators = []
    elements_seen = {}

    for p in data['pages']:
        text = p['text']
        # Find table title
        title_m = re.search(r'Table\s+\d+\s*\n\s*(.+?)(?:\n)', text)
        if not title_m:
            continue

        element_name = title_m.group(1).strip()
        # Skip TOC entries (contain dots)
        if '...' in element_name:
            continue
        # Clean up parenthetical level ranges from title
        element_name = re.sub(r'\s*\(L[\d\w–-]+\)\s*$', '', element_name).strip()
        if not element_name:
            continue

        # Extract the table content area (after the title, before copyright/footer)
        table_text = text[title_m.end():]
        # Remove common footer text
        table_text = re.sub(r'\d+\s+Literacy\s*$', '', table_text)
        table_text = re.sub(r'Literacy\s+\d+\s*$', '', table_text)
        table_text = re.sub(r'General Capabilities\s*$', '', table_text)

        # Split by level markers
        parts = level_pattern.split(table_text)
        # parts = [pre_text, level1, content1, level2, content2, ...]
        if len(parts) < 3:
            # Try parsing table rows directly (for simpler 7x2 tables)
            tables = p.get('tables', [])
            for t in tables:
                rows = t['rows']
                if t['num_rows'] < 3:
                    continue
                # Check if header has "Descriptions"
                if not any('description' in str(c).lower() for c in rows[0]):
                    continue
                # Rows 1-6 correspond to L1c, L2, L3, L4, L5, L6
                level_seq = ['L1c', 'L2', 'L3', 'L4', 'L5', 'L6']
                desc_col = None
                ex_col = None
                for ci, cell in enumerate(rows[0]):
                    if 'description' in str(cell).lower():
                        desc_col = ci
                    elif 'example' in str(cell).lower():
                        ex_col = ci
                if desc_col is None:
                    continue
                for ri in range(1, min(len(rows), 7)):
                    level_key = level_seq[ri - 1] if ri - 1 < len(level_seq) else f'L{ri}'
                    desc = str(rows[ri][desc_col]).strip() if desc_col < len(rows[ri]) else ''
                    examples = str(rows[ri][ex_col]).strip() if ex_col is not None and ex_col < len(rows[ri]) else ''
                    if not desc:
                        continue
                    indicator_text = desc
                    if examples:
                        indicator_text += f'\nExamples: {examples}'
                    year_levels = LEVEL_YEAR_MAP.get(level_key, [])
                    for yl in year_levels:
                        all_indicators.append({
                            'capability_id': capability_id,
                            'capability_name': capability_name,
                            'element_name': element_name,
                            'sub_element_name': element_name,
                            'level_name': level_key,
                            'year_level_id': yl,
                            'indicator_text': indicator_text,
                            'source_document': filename,
                        })
                if element_name not in elements_seen:
                    elements_seen[element_name] = [element_name]
            continue

        # Process level-content pairs from text
        for i in range(1, len(parts), 2):
            if i + 1 >= len(parts):
                break
            raw_level = parts[i]
            content = parts[i + 1].strip()
            if not content:
                continue

            level_key = _normalise_literacy_level(raw_level)
            # Split into description and examples (examples start with •)
            lines = content.split('\n')
            desc_lines = []
            example_lines = []
            in_examples = False
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('•'):
                    in_examples = True
                if in_examples:
                    example_lines.append(line)
                else:
                    desc_lines.append(line)

            indicator_text = ' '.join(desc_lines)
            if example_lines:
                indicator_text += '\nExamples: ' + ' '.join(example_lines)

            year_levels = LEVEL_YEAR_MAP.get(level_key, [])
            for yl in year_levels:
                all_indicators.append({
                    'capability_id': capability_id,
                    'capability_name': capability_name,
                    'element_name': element_name,
                    'sub_element_name': element_name,
                    'level_name': level_key,
                    'year_level_id': yl,
                    'indicator_text': indicator_text,
                    'source_document': filename,
                })

        if element_name not in elements_seen:
            elements_seen[element_name] = [element_name]

    return {
        'capability_id': capability_id,
        'capability_name': capability_name,
        'description': description,
        'elements': [
            {'element_name': name, 'sub_elements': subs}
            for name, subs in elements_seen.items()
        ],
        'indicators': all_indicators,
        'source_document': filename,
    }


def parse_general_capability(filepath: str) -> dict:
    """Parse a general capability PDF.

    Returns dict with:
      - capability_id, capability_name
      - description (from intro pages)
      - elements: list of element dicts with sub_elements
      - indicators: list of indicator dicts
    """
    data = extract_pdf(filepath)
    filename = data['filename']
    capability_id, capability_name = identify_capability(filename)

    # Extract description from early pages
    description_parts = []
    for p in data['pages'][2:6]:
        text = p['text']
        # Look for "What is..." section
        if 'what is' in text.lower():
            # Extract the paragraph after "What is..."
            m = re.search(r'(?:What is[^?]*\?)\s*(.+?)(?:\n\n|\d+\s+\w+\s+\w+$)', text, re.DOTALL)
            if m:
                description_parts.append(m.group(1).strip())

    description = ' '.join(description_parts) if description_parts else None

    # Literacy has a completely different structure — text-based parsing
    if capability_id == 'gc-literacy':
        return parse_literacy_capability(data, filename, capability_id, capability_name, description)

    # Parse all content tables (8 rows, 2-4 cols, row 0 = "Sub-elements")
    all_indicators = []
    elements_seen = {}

    for p in data['pages']:
        tables = p.get('tables', [])
        page_text = p['text']

        for table in tables:
            if table['num_rows'] < 4:
                continue

            # Check if it's a capability progression table
            first_row = table['rows'][0] if table['rows'] else []
            if not any('sub-element' in str(c).lower() for c in first_row):
                continue

            element_name = extract_element_name_from_text(page_text)

            indicators = parse_capability_table(
                table, element_name, capability_id, capability_name, filename
            )
            all_indicators.extend(indicators)

            # Track unique elements and sub-elements
            if element_name and element_name not in elements_seen:
                sub_elems = []
                for ci in range(table['num_cols']):
                    cell = table['rows'][1][ci] if ci < len(table['rows'][1]) else ''
                    name = str(cell).strip().replace('\n', ' ') if cell else ''
                    if name:
                        sub_elems.append(name)
                elements_seen[element_name] = sub_elems

    return {
        'capability_id': capability_id,
        'capability_name': capability_name,
        'description': description,
        'elements': [
            {'element_name': name, 'sub_elements': subs}
            for name, subs in elements_seen.items()
        ],
        'indicators': all_indicators,
        'source_document': filename,
    }


def parse_all_capabilities(raw_dir: str) -> list:
    """Parse all general capability PDFs. Returns list of capability dicts."""
    cap_dir = os.path.join(raw_dir, 'general-capabilites')
    results = []

    for fname in sorted(os.listdir(cap_dir)):
        if not fname.lower().endswith('.pdf'):
            continue
        fpath = os.path.join(cap_dir, fname)
        try:
            cap = parse_general_capability(fpath)
            n_ind = len(cap['indicators'])
            n_elem = len(cap['elements'])
            print(f"  {fname}: {n_elem} elements, {n_ind} indicators", file=sys.stderr)
            results.append(cap)
        except Exception as e:
            print(f"  ERROR {fname}: {e}", file=sys.stderr)

    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: general_capabilities.py <file.pdf | raw_dir>")
        sys.exit(1)

    path = sys.argv[1]
    if os.path.isdir(path):
        results = parse_all_capabilities(path)
    else:
        results = [parse_general_capability(path)]

    print(json.dumps(results, indent=2, ensure_ascii=False))
