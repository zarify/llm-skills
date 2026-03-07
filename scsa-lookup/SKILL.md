---
name: scsa-lookup
description: Tool for looking up curriculum content descriptors and elaborations from the Western Australian (SCSA) curriculum across all learning areas PP-10
---

# Western Australian Curriculum (SCSA) Lookup Skill

This skill provides utilities to query the School Curriculum and Standards Authority (SCSA) Western Australian curriculum data for lesson planning, curriculum alignment, gap analysis, assessment design, and student work evaluation. It covers all WA curriculum learning areas from Pre-primary to Year 10, general capabilities, ABLEWA content, judging standards, and glossaries.

## Files

- `scsa-helper.cjs` — JavaScript CLI helper for querying the curriculum database
- `scsa.db` — SQLite database containing all extracted curriculum data
- `scripts/` — Python extraction and loading scripts (for updating data)

## Data Coverage

### Learning Areas (Pre-primary to Year 10)
- **English** — Language, Literature, Literacy strands (Implementation 2025)
- **Health & Physical Education** — Personal, social and community health; Movement and physical activity (Implementation 2025)
- **Humanities and Social Sciences** — History, Geography, Civics & Citizenship, Economics & Business (Implementation 2026)
- **Mathematics** — Number, Algebra, Measurement, Space, Statistics, Probability (Implementation 2026)
- **Science** — Biological, Chemical, Earth and space, Physical sciences (Implementation 2026)
- **Technologies — Design & Technologies** (Implementation 2026)
- **Technologies — Digital Technologies** (Implementation 2026)
- **The Arts** — Dance, Drama, Media Arts, Music, Visual Arts (Familiarisation 2026)
- **Languages** — Aboriginal Languages Revival Template, Wajarri, Noongar

### General Capabilities (6 of 7 available)
- Critical and Creative Thinking
- Digital Literacy
- Ethical Understanding
- Intercultural Understanding
- Literacy
- Personal and Social Capability
- ~~Numeracy~~ (listed as "coming soon" by SCSA)

### Additional Content
- **ABLEWA** — Abilities Based Learning Education WA (Stages A–D) for English, HASS, Mathematics, Science, Technologies, The Arts
- **Judging Standards** — Grade descriptors (A–E) for most learning areas × year levels
- **Glossaries** — Subject-specific terminology for English, Mathematics, Technologies, HPE
- **Principles** — Teaching & learning principles and assessment principles with reflective questions

## Usage

### List all learning areas

```bash
node scsa-helper.cjs list-areas
```

### Search for content descriptors

```bash
node scsa-helper.cjs search "algorithm" --year Y7 --area tech-digital
node scsa-helper.cjs search "fractions" --year Y5
```

### Search across ALL content (descriptors, achievement standards, glossary)

```bash
node scsa-helper.cjs search-all "sustainability" --year Y8
```

### Get content descriptors for a learning area and year level

```bash
node scsa-helper.cjs get-content mathematics Y7
node scsa-helper.cjs get-content english PP
```

### Get achievement standards

```bash
node scsa-helper.cjs get-achievement science Y9
```

### Get year level descriptions

```bash
node scsa-helper.cjs get-description tech-digital Y8
```

### Get general capability indicators

```bash
node scsa-helper.cjs get-capability gc-digital-literacy --year Y7
node scsa-helper.cjs get-capability gc-critical-creative
```

### Get judging standards (grade descriptors A–E)

```bash
node scsa-helper.cjs get-judging mathematics Y5
node scsa-helper.cjs get-judging english Y8
```

### Look up glossary terms

```bash
node scsa-helper.cjs get-glossary mathematics --term "algorithm"
node scsa-helper.cjs get-glossary technologies
```

### Get teaching/assessment principles

```bash
node scsa-helper.cjs get-principles --category assessment
node scsa-helper.cjs get-principles
```

### Get ABLEWA content

```bash
node scsa-helper.cjs get-ablewa english --level "Stage A"
node scsa-helper.cjs get-ablewa mathematics
```

### Show ACARA cross-references

```bash
node scsa-helper.cjs crossref tech-digital Y8
```

### Database statistics

```bash
node scsa-helper.cjs stats
```

## Learning Area IDs

| ID | Learning Area |
|---|---|
| `english` | English |
| `hpe` | Health and Physical Education |
| `hass` | Humanities and Social Sciences |
| `mathematics` | Mathematics |
| `science` | Science |
| `tech-design` | Technologies — Design & Technologies |
| `tech-digital` | Technologies — Digital Technologies |
| `arts-dance` | The Arts — Dance |
| `arts-drama` | The Arts — Drama |
| `arts-media` | The Arts — Media Arts |
| `arts-music` | The Arts — Music |
| `arts-visual` | The Arts — Visual Arts |
| `lang-aboriginal-template` | Languages — Aboriginal Template |

## Year Level IDs

| ID | Level |
|---|---|
| `PP` | Pre-primary |
| `Y1`–`Y10` | Year 1 through Year 10 |

## General Capability IDs

| ID | Capability |
|---|---|
| `gc-critical-creative` | Critical and Creative Thinking |
| `gc-digital-literacy` | Digital Literacy |
| `gc-ethical` | Ethical Understanding |
| `gc-intercultural` | Intercultural Understanding |
| `gc-literacy` | Literacy |
| `gc-personal-social` | Personal and Social Capability |

## Use in Lesson Planning

1. **Search for relevant descriptors** by topic keywords across learning areas
2. **Get content for a year level** to understand the scope of teaching required
3. **Check achievement standards** to understand expected student outcomes
4. **Use judging standards** to differentiate activities for A–E achievement levels
5. **Cross-reference general capabilities** to embed capability development in lessons
6. **Use glossaries** to ensure age-appropriate, curriculum-aligned terminology
7. **Reference ABLEWA** for inclusive planning for students with disability
8. **Apply teaching/assessment principles** as a reflective framework

### Example: Planning a Year 7 Mathematics Lesson

```bash
# Get all Year 7 content descriptors for Mathematics
node scsa-helper.cjs get-content mathematics Y7

# Check what students should achieve
node scsa-helper.cjs get-achievement mathematics Y7

# Get judging standards for differentiating
node scsa-helper.cjs get-judging mathematics Y7

# Find cross-curricular digital literacy links
node scsa-helper.cjs get-capability gc-digital-literacy --year Y7

# Look up relevant vocabulary
node scsa-helper.cjs get-glossary mathematics --term "index"

# Compare with national ACARA curriculum
node scsa-helper.cjs crossref mathematics Y7
```

### Example: Assessment Rubric Design

```bash
# Get achievement standard for the year level
node scsa-helper.cjs get-achievement english Y9

# Get A-E grade descriptors
node scsa-helper.cjs get-judging english Y9

# Review assessment principles
node scsa-helper.cjs get-principles --category assessment
```

## Data Quality Notes

- Content has been adversarially verified using multiple AI models (Gemini Pro 3.1, GPT 5.4) against source documents
- **Judging standards marked as `is_best_effort`** may not fully align with the latest syllabus (some files date to 2017)
- General capability levels (L1–L6) map approximately to year level bands: L1=PP, L2=Y1-2, L3=Y3-4, L4=Y5-6, L5=Y7-8, L6=Y9-10
- ABLEWA uses Stages A–D (not year levels) as its progression framework. Note: The Arts ABLEWA is missing Stage B in the source document
- ABLEWA is not available for HPE (no source document published by SCSA)
- The Numeracy general capability is not yet available from SCSA
- Glossaries are only available for English, HPE, Mathematics, and Technologies
- The Arts learning areas include both mandated-only and full scope & sequence descriptors (mandated content is flagged with `is_mandated=1`)

## WA Curriculum vs National Curriculum

The SCSA WA curriculum is based on the Australian Curriculum (ACARA) but includes WA-specific adaptations. Use the `crossref` command to compare:

| Match Type | Count | Meaning |
|---|---|---|
| `exact` | 170 | Identical wording to ACARA descriptor |
| `partial` | 124 | Substantially similar (>80% match) |
| `related` | 147 | Related content (>60% match) |
| `wa-specific` | 1,867 | WA-adapted or unique content |

Key differences:
- WA uses "Pre-primary" instead of "Foundation"
- English has strongest national alignment (164 exact matches)
- Mathematics, Science, and The Arts are substantially WA-adapted
- Languages (Aboriginal) are entirely WA-specific
- Implementation timelines differ (staggered 2025–2026 rollout)
- ABLEWA is a WA-specific resource for students with disability

## Updating the Database

When new SCSA documents are released:

1. Place raw documents in the appropriate `raw/` subdirectory
2. Run the extraction pipeline: `cd scsa && python scripts/load_db.py --reset`
3. The database will be rebuilt with all available data

Individual parsers can also be run standalone — see `scripts/parsers/` for details.
