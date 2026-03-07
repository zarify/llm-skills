#!/usr/bin/env python3
"""
PDF Extraction Framework

Extracts text and tables from PDF files using pdfplumber.
"""

import json
import os
import sys
import pdfplumber


def extract_pdf(filepath: str) -> dict:
    """Extract text and tables from a PDF file.

    Returns a dict with:
      - filename: basename of the file
      - pages: list of page dicts (text + tables)
      - full_text: concatenated text across all pages
    """
    basename = os.path.basename(filepath)
    pages = []
    full_text_parts = []

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages):
            page_text = page.extract_text() or ''
            full_text_parts.append(page_text)

            # Extract tables
            page_tables = []
            for table_idx, table in enumerate(page.extract_tables()):
                # Clean cells
                cleaned = []
                for row in table:
                    cleaned.append([
                        (cell or '').strip() for cell in row
                    ])
                page_tables.append({
                    'index': table_idx,
                    'rows': cleaned,
                    'num_rows': len(cleaned),
                    'num_cols': len(cleaned[0]) if cleaned else 0,
                })

            pages.append({
                'page_number': page_num + 1,
                'text': page_text,
                'tables': page_tables,
            })

    return {
        'filename': basename,
        'pages': pages,
        'full_text': '\n\n'.join(full_text_parts),
        'num_pages': len(pages),
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: extract_pdf.py <file.pdf>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = extract_pdf(filepath)
    print(json.dumps(result, indent=2, ensure_ascii=False))
