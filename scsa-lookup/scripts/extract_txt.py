#!/usr/bin/env python3
"""
TXT Extraction Framework

Parses plain text files into structured sections.
"""

import json
import os
import re
import sys


def extract_txt(filepath: str) -> dict:
    """Extract and structure a plain text file.

    Identifies section headers (lines that look like titles) and
    groups content into sections.

    Returns a dict with:
      - filename: basename of the file
      - sections: list of {title, text} dicts
      - full_text: the raw text
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        full_text = f.read()

    lines = full_text.split('\n')
    sections = []
    current_title = None
    current_lines = []

    for line in lines:
        stripped = line.strip()
        # Heuristic: a line that is relatively short, non-empty, and does not
        # end with common punctuation is likely a section header.
        # Also match numbered patterns like "Assessment Principle 1:"
        is_header = (
            stripped
            and len(stripped) < 120
            and not stripped.endswith('.')
            and not stripped.endswith(',')
            and not stripped.endswith(';')
            and (
                re.match(r'^[A-Z]', stripped)
                or re.match(r'^\d+\.?\s', stripped)
            )
            and not stripped.startswith('•')
            and not stripped.startswith('-')
            and not stripped.startswith('*')
        )

        if is_header and current_lines:
            text = '\n'.join(current_lines).strip()
            if text or current_title:
                sections.append({
                    'title': current_title,
                    'text': text,
                })
            current_title = stripped
            current_lines = []
        elif is_header and not current_lines:
            if current_title:
                sections.append({
                    'title': current_title,
                    'text': '',
                })
            current_title = stripped
        else:
            current_lines.append(line)

    # Final section
    text = '\n'.join(current_lines).strip()
    if text or current_title:
        sections.append({
            'title': current_title,
            'text': text,
        })

    return {
        'filename': os.path.basename(filepath),
        'sections': sections,
        'full_text': full_text,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_txt.py <file.txt>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_txt(filepath)
    print(json.dumps(result, indent=2, ensure_ascii=False))
