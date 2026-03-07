#!/usr/bin/env python3
"""
Build ACARA cross-reference table for SCSA content descriptors.

Maps SCSA content descriptors to their closest ACARA (Australian Curriculum v9)
equivalents using text similarity within matched learning-area + year-level pairs.
"""

import json
import os
import re
import sqlite3
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SCSA_DB = SCRIPT_DIR.parent / "scsa.db"
ACARA_DIR = SCRIPT_DIR.parent.parent / "acara" / "curriculum"

# ---------------------------------------------------------------------------
# JSONLD namespace shortcuts
# ---------------------------------------------------------------------------
NS_NOTATION = "http://purl.org/ASN/schema/core/statementNotation"
NS_LABEL = "http://purl.org/ASN/schema/core/statementLabel"
NS_DESC = "http://purl.org/dc/terms/description"
NS_TITLE = "http://purl.org/dc/terms/title"
NS_YEAR = "https://www.esa.edu.au/nominalYearLevel"

# ---------------------------------------------------------------------------
# Mapping tables
# ---------------------------------------------------------------------------

# SCSA learning_area_id → (ACARA file, optional notation prefix filter)
AREA_MAP: dict[str, list[tuple[str, str | None]]] = {
    "english":                [("ENG.jsonld", None)],
    "mathematics":            [("MAT.jsonld", None)],
    "science":                [("SCI.jsonld", None)],
    "hpe":                    [("HPE.jsonld", None)],
    "hass":                   [("HASS.jsonld", None)],       # all HASS sub-subjects
    "hass-civics":            [("HASS.jsonld", "AC9HC")],
    "hass-economics":         [("HASS.jsonld", "AC9HE")],
    "hass-geography":         [("HASS.jsonld", "AC9HG")],
    "hass-history":           [("HASS.jsonld", "AC9HH")],
    "tech-digital":           [("TEC.jsonld", "AC9TDI")],
    "tech-design":            [("TEC.jsonld", "AC9TDE")],
    "arts-dance":             [("ART.jsonld", "AC9ADA")],
    "arts-drama":             [("ART.jsonld", "AC9ADR")],
    "arts-media":             [("ART.jsonld", "AC9AMA")],
    "arts-music":             [("ART.jsonld", "AC9AMU")],
    "arts-visual":            [("ART.jsonld", "AC9AVA")],
    "lang-aboriginal-template": [("LAN.jsonld", None)],
}

# SCSA year_level_id → ACARA nominalYearLevel value
YEAR_MAP: dict[str, str] = {"PP": "Foundation Year"}
for i in range(1, 11):
    YEAR_MAP[f"Y{i}"] = f"Year {i}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ld_value(node: dict, key: str) -> str:
    """Extract the first @value from a JSON-LD property list."""
    values = node.get(key, [])
    for v in values:
        if isinstance(v, dict) and "@value" in v:
            return v["@value"]
    return ""


_EXAMPLE_RE = re.compile(
    r"\s*[\n\r]?\s*For example[:\s].*", re.DOTALL | re.IGNORECASE
)
_NORM_RE = re.compile(r"[^a-z0-9 ]+")
_WS_RE = re.compile(r"\s+")

def strip_examples(text: str) -> str:
    """Remove 'For example:' and everything after it."""
    return _EXAMPLE_RE.sub("", text).strip()

def normalise(text: str) -> str:
    """Lowercase, strip examples/punctuation, collapse whitespace."""
    text = strip_examples(text)
    text = text.lower()
    text = _NORM_RE.sub(" ", text)
    text = _WS_RE.sub(" ", text).strip()
    return text


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def classify(score: float) -> str:
    if score >= 1.0:
        return "exact"
    if score > 0.80:
        return "partial"
    if score > 0.60:
        return "related"
    return "wa-specific"

# ---------------------------------------------------------------------------
# ACARA loader (cached per file)
# ---------------------------------------------------------------------------

_acara_cache: dict[str, list[dict]] = {}

def load_acara_descriptors(filename: str) -> list[dict]:
    """Load content descriptors (not elaborations) from an ACARA JSONLD file.

    Returns list of dicts: {code, description, year_level, raw_description}
    """
    if filename in _acara_cache:
        return _acara_cache[filename]

    path = ACARA_DIR / filename
    if not path.exists():
        print(f"  ⚠ ACARA file not found: {path}")
        _acara_cache[filename] = []
        return []

    with open(path) as f:
        data = json.load(f)

    graph = data[0]["@graph"] if isinstance(data, list) else data["@graph"]

    descriptors: list[dict] = []
    for item in graph:
        label = ld_value(item, NS_LABEL)
        if "Content Description" not in label:
            continue

        code = ld_value(item, NS_NOTATION)
        if not code or "_E" in code:  # skip elaborations by notation too
            continue

        desc = ld_value(item, NS_DESC) or ld_value(item, NS_TITLE)
        year = ld_value(item, NS_YEAR)

        descriptors.append({
            "code": code,
            "description": desc,
            "year_level": year,
            "norm": normalise(desc),
        })

    _acara_cache[filename] = descriptors
    return descriptors

# ---------------------------------------------------------------------------
# Main matching logic
# ---------------------------------------------------------------------------

def find_best_match(
    scsa_text_norm: str,
    candidates: list[dict],
) -> tuple[dict | None, float]:
    """Find the best-matching ACARA descriptor for a normalised SCSA text."""
    best: dict | None = None
    best_score = 0.0
    for cand in candidates:
        score = similarity(scsa_text_norm, cand["norm"])
        if score > best_score:
            best_score = score
            best = cand
    return best, best_score


def build_crossref() -> None:
    if not SCSA_DB.exists():
        sys.exit(f"SCSA database not found: {SCSA_DB}")

    conn = sqlite3.connect(str(SCSA_DB))
    conn.row_factory = sqlite3.Row

    # Recreate target table with desired schema
    conn.execute("DROP TABLE IF EXISTS acara_crossref")
    conn.execute("""
        CREATE TABLE acara_crossref (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scsa_content_id INTEGER REFERENCES content_descriptors(id),
            acara_code TEXT NOT NULL,
            acara_description TEXT,
            match_type TEXT CHECK(match_type IN ('exact','partial','related','wa-specific')),
            confidence REAL,
            notes TEXT
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crossref_scsa ON acara_crossref(scsa_content_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_crossref_acara ON acara_crossref(acara_code)")
    conn.commit()

    # Load SCSA descriptors
    rows = conn.execute(
        "SELECT id, learning_area_id, year_level_id, content_description "
        "FROM content_descriptors ORDER BY learning_area_id, year_level_id"
    ).fetchall()
    print(f"Loaded {len(rows)} SCSA content descriptors")

    # Pre-index ACARA descriptors by (file, year_level) for speed
    acara_index: dict[str, dict[str, list[dict]]] = {}  # file → year → [descriptors]

    stats: dict[str, int] = defaultdict(int)
    area_stats: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total = len(rows)
    inserts: list[tuple] = []

    for i, row in enumerate(rows, 1):
        scsa_id = row["id"]
        area = row["learning_area_id"]
        year_id = row["year_level_id"]
        scsa_text = row["content_description"]
        scsa_norm = normalise(scsa_text)

        acara_year = YEAR_MAP.get(year_id)
        if not acara_year:
            # Unknown year level – mark wa-specific
            inserts.append((scsa_id, "N/A", None, "wa-specific", 0.0,
                            f"Unmapped year level: {year_id}"))
            stats["wa-specific"] += 1
            area_stats[area]["wa-specific"] += 1
            continue

        mappings = AREA_MAP.get(area)
        if not mappings:
            inserts.append((scsa_id, "N/A", None, "wa-specific", 0.0,
                            f"No ACARA mapping for learning area: {area}"))
            stats["wa-specific"] += 1
            area_stats[area]["wa-specific"] += 1
            continue

        # Gather candidates from all mapped files/prefixes for this year
        candidates: list[dict] = []
        for filename, prefix in mappings:
            all_descs = load_acara_descriptors(filename)
            for d in all_descs:
                if d["year_level"] != acara_year:
                    continue
                if prefix and not d["code"].startswith(prefix):
                    continue
                candidates.append(d)

        if not candidates:
            inserts.append((scsa_id, "N/A", None, "wa-specific", 0.0,
                            f"No ACARA candidates for {area}/{year_id}"))
            stats["wa-specific"] += 1
            area_stats[area]["wa-specific"] += 1
            continue

        best, score = find_best_match(scsa_norm, candidates)
        if best is None:
            match_type = "wa-specific"
            inserts.append((scsa_id, "N/A", None, match_type, 0.0, None))
        else:
            match_type = classify(score)
            inserts.append((
                scsa_id,
                best["code"],
                best["description"],
                match_type,
                round(score, 4),
                None,
            ))

        stats[match_type] += 1
        area_stats[area][match_type] += 1

        if i % 200 == 0 or i == total:
            print(f"  Processed {i}/{total} descriptors …")

    # Bulk insert
    conn.executemany(
        "INSERT INTO acara_crossref "
        "(scsa_content_id, acara_code, acara_description, match_type, confidence, notes) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        inserts,
    )
    conn.commit()
    conn.close()

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("CROSS-REFERENCE SUMMARY")
    print("=" * 60)

    print(f"\nTotal SCSA descriptors processed: {total}")
    print(f"Total cross-references inserted:  {len(inserts)}")
    print("\nBy match type:")
    for mt in ("exact", "partial", "related", "wa-specific"):
        print(f"  {mt:14s}: {stats.get(mt, 0):>5d}")

    print("\nBy learning area:")
    for area in sorted(area_stats):
        counts = area_stats[area]
        total_area = sum(counts.values())
        parts = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  {area:26s}: {total_area:>4d}  ({parts})")


if __name__ == "__main__":
    build_crossref()
