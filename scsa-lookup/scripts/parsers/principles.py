#!/usr/bin/env python3
"""Parser for SCSA teaching and learning principles text files.

Extracts structured principle data from:
- raw/principles/assessment-principles.txt (6 assessment principles)
- raw/principles/teaching-and-learning-principles.txt (7 T&L principles)
"""

import json
import os
import re
import sys


def _parse_assessment_principles(text: str, filename: str) -> list[dict]:
    """Parse assessment principles from structured text."""
    heading_re = r"Assessment Principle (\d+):\s*(.+)"
    matches = list(re.finditer(heading_re, text))

    principles = []
    for i, match in enumerate(matches):
        num = int(match.group(1))
        title = match.group(2).strip()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section = text[start:end].strip()

        # Split description from reflection content at "Reflecting on" heading
        reflecting_match = re.search(r"^Reflecting on .+", section, re.MULTILINE)
        if reflecting_match:
            description = section[: reflecting_match.start()].strip()
            reflection_section = section[reflecting_match.start() :].strip()
        else:
            description = section
            reflection_section = ""

        reflection_questions: list[str] = []
        guidance = ""

        if reflection_section:
            # Split reflection section into blocks at Consider / Ensure headings
            blocks = re.split(
                r"^(?=Consider |Ensur(?:e|ing) )",
                reflection_section,
                flags=re.MULTILINE,
            )

            for block in blocks:
                if block.startswith("Consider"):
                    # Collect indented bullet lines as reflection questions
                    for line in block.split("\n"):
                        if (line.startswith("    ") or line.startswith("\t")) and line.strip():
                            reflection_questions.append(line.strip())
                elif re.match(r"^Ensur(?:e|ing) ", block):
                    guidance = block.strip()

        principles.append(
            {
                "category": "assessment",
                "principle_number": num,
                "title": title,
                "description": description,
                "reflection_questions": reflection_questions,
                "guidance": guidance,
                "source_document": filename,
            }
        )

    return principles


# Known T&L principle titles in document order
_TL_TITLES = [
    "Opportunity to learn",
    "Connection and challenge",
    "Action and reflection",
    "Motivation and purpose",
    "Inclusivity and difference",
    "Independence and collaboration",
    "Supportive environment",
]


def _parse_teaching_learning_principles(text: str, filename: str) -> list[dict]:
    """Parse teaching and learning principles from text."""
    lines = text.split("\n")

    # Locate each known title by exact line match
    title_indices: list[tuple[int, str]] = []
    for title in _TL_TITLES:
        for i, line in enumerate(lines):
            if line.strip() == title:
                title_indices.append((i, title))
                break

    principles = []
    for idx, (line_idx, title) in enumerate(title_indices):
        next_idx = title_indices[idx + 1][0] if idx + 1 < len(title_indices) else len(lines)
        content_lines = lines[line_idx + 1 : next_idx]

        # Group non-blank runs into paragraphs
        paragraphs: list[str] = []
        current: list[str] = []
        for line in content_lines:
            if line.strip() == "":
                if current:
                    paragraphs.append(" ".join(current))
                    current = []
            else:
                current.append(line.strip())
        if current:
            paragraphs.append(" ".join(current))

        # First paragraph is the short description; rest is extended guidance
        description = paragraphs[0] if paragraphs else ""
        guidance = "\n\n".join(paragraphs[1:]) if len(paragraphs) > 1 else ""

        principles.append(
            {
                "category": "teaching-and-learning",
                "principle_number": idx + 1,
                "title": title,
                "description": description,
                "reflection_questions": [],
                "guidance": guidance,
                "source_document": filename,
            }
        )

    return principles


def parse_principles(filepath: str) -> list[dict]:
    """Parse principles from a SCSA principles text file.

    Auto-detects file type (assessment vs teaching-and-learning) from content.

    Args:
        filepath: Path to the principles text file.

    Returns:
        List of principle dicts with keys: category, principle_number,
        title, description, reflection_questions, guidance, source_document.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    filename = os.path.basename(filepath)

    if re.search(r"Assessment Principle \d+:", text):
        return _parse_assessment_principles(text, filename)
    return _parse_teaching_learning_principles(text, filename)


def main() -> None:
    """CLI entry point: parse principles file(s) and output JSON."""
    if len(sys.argv) < 2:
        print("Usage: python principles.py <filepath> [<filepath> ...]", file=sys.stderr)
        sys.exit(1)

    all_principles: list[dict] = []
    for filepath in sys.argv[1:]:
        all_principles.extend(parse_principles(filepath))

    print(json.dumps(all_principles, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
