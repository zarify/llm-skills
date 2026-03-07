#!/usr/bin/env python3
"""
Parser for SCSA glossary DOCX files.

Extracts glossary term/definition pairs from SCSA glossary documents.
Uses Heading 2 as alphabetical group headers, Heading 3 as terms,
and subsequent Normal paragraphs as definitions.
"""

import os
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_docx import extract_docx

LEARNING_AREA_MAP = {
    "Technologies-glossary": "technologies",
    "Mathematics-glossary": "mathematics",
    "English-Glossary": "english",
    "Health-and-Physical-Education-Glossary": "hpe",
}


def _detect_learning_area(filename: str) -> str:
    """Map a glossary filename to its learning area ID."""
    for pattern, area_id in LEARNING_AREA_MAP.items():
        if pattern in filename:
            return area_id
    return "unknown"


def parse_glossary(filepath: str) -> list[dict]:
    """
    Parse a SCSA glossary DOCX file into term/definition records.

    Args:
        filepath: Path to the glossary DOCX file.

    Returns:
        List of dicts with keys: learning_area_id, term, definition, source_document.
    """
    data = extract_docx(filepath)
    filename = os.path.basename(filepath)
    learning_area_id = _detect_learning_area(filename)

    elements = data["body_elements"]
    results = []
    current_term = None
    definition_parts: list[str] = []
    in_glossary = False

    def _flush():
        if current_term and definition_parts:
            results.append({
                "learning_area_id": learning_area_id,
                "term": current_term,
                "definition": "\n\n".join(definition_parts),
                "source_document": filename,
            })

    for el in elements:
        if el["type"] != "paragraph":
            continue

        style = el["style"]
        text = el["text"].strip()

        if not text:
            continue

        if style == "Heading 2":
            # Alphabetical group header — marks start of glossary content
            _flush()
            current_term = None
            definition_parts = []
            in_glossary = True
            continue

        if not in_glossary:
            continue

        if style == "Heading 3":
            _flush()
            current_term = text
            definition_parts = []
        elif style == "Normal" and current_term:
            definition_parts.append(text)

    _flush()
    return results


def main():
    parser = argparse.ArgumentParser(description="Parse SCSA glossary DOCX files")
    parser.add_argument("filepath", help="Path to glossary DOCX file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = parse_glossary(args.filepath)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Parsed {len(results)} glossary terms from {os.path.basename(args.filepath)}")
        for r in results:
            print(f"  [{r['learning_area_id']}] {r['term']}: {r['definition'][:80]}...")


if __name__ == "__main__":
    main()
