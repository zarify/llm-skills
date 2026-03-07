---
name: acara-lookup
description: Tool for looking up curriculum content descriptors and elaborations from the Australian Curriculum (ACARA) machine-readable documentation
---

# Australian Curriculum Lookup Skill

This skill provides utilities to extract curriculum information from ACARA JSONLD files for lesson planning and curriculum coverage checking. It covers all Australian Curriculum learning areas, general capabilities, and cross-curriculum priorities.

## Files

- `curriculum-helper.cjs` — JavaScript helper for extracting curriculum data
- `curriculum/` — JSONLD curriculum files from ACARA (18 files)

## Available Curriculum Files

Filenames use native ACARA abbreviations.

### Learning Areas
- `TEC.jsonld` — Technologies (includes Digital Technologies)
- `ENG.jsonld` — English
- `MAT.jsonld` — Mathematics
- `SCI.jsonld` — Science
- `HASS.jsonld` — Humanities and Social Sciences
- `HPE.jsonld` — Health and Physical Education
- `ART.jsonld` — The Arts
- `LAN.jsonld` — Languages

### General Capabilities
- `DL.jsonld` — Digital Literacy
- `CCT.jsonld` — Critical and Creative Thinking
- `EU.jsonld` — Ethical Understanding
- `IU.jsonld` — Intercultural Understanding
- `L.jsonld` — Literacy
- `N.jsonld` — Numeracy
- `PSC.jsonld` — Personal and Social Capability

### Cross-Curriculum Priorities
- `AA.jsonld` — Asia and Australia's Engagement with Asia
- `A_TSI.jsonld` — Aboriginal and Torres Strait Islander Histories and Cultures
- `S.jsonld` — Sustainability

## Usage

### List available curriculum files

```bash
node curriculum-helper.cjs list-files
```

Lists all available curriculum files grouped by category (Learning Areas, General Capabilities, Cross-Curriculum Priorities).

### Search for content descriptors by keyword

```bash
node curriculum-helper.cjs search SCI.jsonld "energy" "Year 8"
```

Returns content descriptors matching the search term in a specific file, optionally filtered by year level.

### Search across all learning areas

```bash
node curriculum-helper.cjs search-all "algorithm" "Year 7"
```

Searches across ALL learning area files for matching content descriptors, optionally filtered by year level.

### Get content descriptors for a year level

```bash
node curriculum-helper.cjs list-by-year MAT.jsonld "Year 5"
```

Lists all content descriptors for the specified year level.

### Get full descriptor details with elaborations

```bash
node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8K04
```

Returns complete details for a content descriptor including:
- Code (e.g., AC9TDI8K04)
- Description/title
- Year levels
- All elaborations
- Skills embodied
- Achievement levels

### Get general capability indicators

```bash
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"
```

Returns indicators from general capabilities for a year level.

### Get cross-curriculum priority organising ideas

```bash
node curriculum-helper.cjs get-priorities S.jsonld
```

Returns the organising ideas for a cross-curriculum priority file.

## Use in Lesson Planning

When creating lesson content, use this tool to:

1. **Search for relevant descriptors** by topic keywords (single file or across all learning areas)
2. **Get full descriptor details** to understand requirements and see elaborations
3. **Check curriculum coverage** by listing all descriptors for target year levels
4. **Cross-reference capabilities** to ensure holistic learning
5. **Incorporate cross-curriculum priorities** using organising ideas

### Example Workflow

```bash
# Search across all learning areas for sustainability content in Year 5-6
node curriculum-helper.cjs search-all "sustainability" "Year 5"

# Get full details including elaborations for a Science descriptor
node curriculum-helper.cjs get-descriptor SCI.jsonld AC9S6U04

# Check Digital Literacy capability requirements for Year 5
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 5"

# Get Sustainability organising ideas for cross-curriculum links
node curriculum-helper.cjs get-priorities S.jsonld
```

## Integration with Lesson Creation

Reference curriculum codes in lesson content metadata and improvements documents to:
- Track which descriptors are addressed
- Ensure comprehensive elaboration coverage
- Document general capability links
- Incorporate cross-curriculum priority organising ideas
- Support curriculum reporting and planning

## Year Level Mapping

- Foundation (Prep/Kindy)
- Year 1 through Year 10

Content descriptors often span multiple years (e.g., Year 7-8, Year 5-6).

## Data Structure Notes

### Content Descriptors (Learning Areas)
- Have a `statementLabel` of "Content Description"
- Include `educationLevel` for year levels
- Have child `elaborations` via `hasChild` relationships
- Reference `skillsEmbodied` (general capabilities)
- Files: TEC, ENG, MAT, SCI, HASS, HPE, ART, LAN

### Indicators (General Capabilities)
- Have a `statementLabel` of "Indicator"
- Include `proficiencyLevel` (progression levels)
- Different structure from learning area content
- Files: DL, CCT, EU, IU, L, N, PSC

### Organising Ideas (Cross-Curriculum Priorities)
- Have a `statementLabel` of "Organising Idea"
- Contain high-level organising ideas
- Files: AA, A_TSI, S

The helper abstracts these differences for easy access.
