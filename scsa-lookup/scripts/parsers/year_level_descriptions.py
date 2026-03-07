#!/usr/bin/env python3
"""
Parser for SCSA year level description DOCX files.

Extracts year level description text from SCSA curriculum documents that
contain per-year-level prose describing the teaching/learning focus.
"""

import os
import re
import sys
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from extract_docx import extract_docx

LEARNING_AREA_MAP = [
    (r"Technologies.*Digital.*Year", "tech-digital"),
    (r"Technologies.*Design.*Year", "tech-design"),
    (r"The-Arts[_-]Dance", "arts-dance"),
    (r"The-Arts[_-]Drama", "arts-drama"),
    (r"The-Arts[_-]Media", "arts-media"),
    (r"The-Arts[_-]Music", "arts-music"),
    (r"The-Arts[_-]Visual", "arts-visual"),
    (r"Humanities.*Year", "hass"),
    (r"English.*Year", "english"),
    (r"HPE.*Year", "hpe"),
    (r"Mathematics.*Year", "mathematics"),
    (r"Science.*Year", "science"),
]

YEAR_LEVEL_HEADINGS = {"Heading 1", "SCSA Heading 1"}

YEAR_LEVEL_PATTERN = re.compile(
    r"^(Pre-primary|Year\s+(\d{1,2}))$", re.IGNORECASE
)


def _detect_learning_area(filename: str) -> str:
    """Map a year level description filename to its learning area ID."""
    for pattern, area_id in LEARNING_AREA_MAP:
        if re.search(pattern, filename, re.IGNORECASE):
            return area_id
    return "unknown"


def _year_level_id(text: str) -> str | None:
    """Convert a heading like 'Pre-primary' or 'Year 7' to an ID like 'PP' or 'Y7'."""
    m = YEAR_LEVEL_PATTERN.match(text.strip())
    if not m:
        return None
    if m.group(1).lower().startswith("pre"):
        return "PP"
    return f"Y{m.group(2)}"


def parse_year_level_descriptions(filepath: str) -> list[dict]:
    """
    Parse a SCSA year level description DOCX file.

    Walks through body elements tracking current year level from headings,
    collecting description text paragraphs between year level headings.

    Returns:
        List of dicts with keys: learning_area_id, year_level_id,
        description_text, source_document.
    """
    data = extract_docx(filepath)
    filename = os.path.basename(filepath)
    learning_area_id = _detect_learning_area(filename)

    results = []
    current_year = None
    description_parts: list[str] = []

    def _flush():
        if current_year and description_parts:
            results.append({
                "learning_area_id": learning_area_id,
                "year_level_id": current_year,
                "description_text": "\n\n".join(description_parts),
                "source_document": filename,
            })

    for el in data["body_elements"]:
        if el["type"] != "paragraph":
            continue

        style = el["style"]
        text = el["text"].strip()
        if not text:
            continue

        if style in YEAR_LEVEL_HEADINGS:
            year_id = _year_level_id(text)
            if year_id:
                _flush()
                current_year = year_id
                description_parts = []
            elif current_year:
                # Non-year-level heading (e.g. "Overview") ends current section
                _flush()
                current_year = None
                description_parts = []
            continue

        if current_year:
            description_parts.append(text)

    _flush()
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Parse SCSA year level description DOCX files"
    )
    parser.add_argument("filepath", help="Path to year level description DOCX file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = parse_year_level_descriptions(args.filepath)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(f"Parsed {len(results)} year level descriptions from {os.path.basename(args.filepath)}")
        for r in results:
            snippet = r["description_text"][:80].replace("\n", " ")
            print(f"  [{r['learning_area_id']}] {r['year_level_id']}: {snippet}...")


if __name__ == "__main__":
    main()
