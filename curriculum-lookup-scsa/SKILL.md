---
name: lessons-scsa-lookup
description: Tool for looking up curriculum content descriptors and elaborations from the Western Australian (SCSA) Digital Technologies curriculum
---

# Western Australian Curriculum Lookup Skill (SCSA)

This skill provides utilities to extract curriculum information from the WA SCSA Digital Technologies curriculum for lesson planning and curriculum coverage checking.

## Files

- `wa-curriculum-helper.cjs` - JavaScript helper for extracting curriculum data
- `curriculum/` - Enhanced JSON curriculum file from SCSA

## Available Curriculum Files

### Learning Areas
- `digital-technologies.json` - Complete Digital Technologies curriculum (Pre-primary to Year 10)

## Data Features

The WA curriculum JSON includes:

- **149 curriculum codes** (e.g., WA7DIGDR1, WAPDIGDS1, WA10DIGAD2)
- **167 elaborations** - Teaching examples and guidance
- **Capability tags** - Cross-curricular capability mappings (Digital literacy, Numeracy, etc.)
- **Achievement standards** - Year-level learning expectations
- **Design thinking skills** - Structured by subsections (Project management, Investigating, Designing, etc.)

## Usage

### Get descriptor by code

```bash
node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1
```

Returns complete details for a content descriptor including:
- Code (e.g., WA7DIGDR1)
- Description
- Elaborations (teaching examples)
- Capabilities (cross-curricular links)
- Strand and year level

### List all content descriptors for a year level

```bash
node wa-curriculum-helper.cjs list-by-year "Year 7"
```

Lists all content descriptors for the specified year level.

### Search for content descriptors by keyword

```bash
node wa-curriculum-helper.cjs search "binary" "Year 7"
```

Returns content descriptors matching the search term in descriptions or elaborations, optionally filtered by year level.

### Get content for a specific strand

```bash
node wa-curriculum-helper.cjs get-strand "Year 7" "Digital systems"
```

Returns all content descriptors for a specific strand in a year level.

### Get achievement standard

```bash
node wa-curriculum-helper.cjs achievement-standard "Year 7"
```

Returns the achievement standard for a year level.

### List all curriculum codes for a year

```bash
node wa-curriculum-helper.cjs list-codes "Year 7"
```

Returns an array of all curriculum codes for the specified year level.

### Find descriptors by capability

```bash
node wa-curriculum-helper.cjs by-capability "Numeracy" "Year 7"
```

Returns all descriptors tagged with a specific cross-curricular capability.

## Use in Lesson Planning

When creating lesson content, use this tool to:

1. **Search for relevant descriptors** by topic keywords
2. **Get full descriptor details** to understand requirements and see elaborations
3. **Check curriculum coverage** by listing all descriptors for target year levels
4. **Cross-reference capabilities** to ensure holistic learning
5. **Track specific codes** in lesson plans for reporting and accountability

### Example Workflow

```bash
# Find binary-related content for Year 7
node wa-curriculum-helper.cjs search "binary" "Year 7"

# Get full details including elaborations
node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1

# List all Year 7 codes for comprehensive planning
node wa-curriculum-helper.cjs list-codes "Year 7"

# Find all Numeracy-linked descriptors
node wa-curriculum-helper.cjs by-capability "Numeracy" "Year 7"
```

## Integration with Lesson Creation

Reference curriculum codes in lesson content metadata and planning documents to:
- Track which descriptors are addressed
- Ensure comprehensive elaboration coverage
- Document cross-curricular capability links
- Support curriculum reporting and planning
- Align assessments with achievement standards

## Year Level Coverage

- **Pre-primary** - 10 codes, 18 elaborations
- **Year 1** - 10 codes, 15 elaborations
- **Year 2** - 11 codes, 12 elaborations
- **Year 3** - 11 codes, 11 elaborations
- **Year 4** - 12 codes, 11 elaborations
- **Year 5** - 12 codes, 11 elaborations
- **Year 6** - 12 codes, 15 elaborations
- **Year 7** - 16 codes, 15 elaborations
- **Year 8** - 18 codes, 16 elaborations
- **Year 9** - 19 codes, 23 elaborations
- **Year 10** - 18 codes, 20 elaborations

**Total**: 149 curriculum codes, 167 elaborations

## Curriculum Strands

### All Year Levels
- **Digital systems** - Hardware, software, networks
- **Data representation** - How data is stored and represented
- **Privacy and security** - Digital safety and data protection
- **Digital implementation** - Algorithms and programming
- **Design thinking skills** - Project management, investigating, designing, producing, evaluating

### Years 7-10 Only
- **Acquiring, managing and analysing data** - Data collection and analysis

## Cross-Curricular Capabilities

Descriptors are tagged with relevant capabilities:
- **Digital literacy** - Digital tool usage and online safety
- **Numeracy** - Mathematical concepts in technology
- **Critical and creative thinking** - Problem-solving and innovation
- **Personal and social capability** - Collaboration and ethical use
- **Ethical understanding** - Responsible technology use
- **Literacy** - Communication and interpretation

## Data Structure

Each content descriptor includes:

```json
{
  "code": "WA7DIGDR1",
  "description": "Digital systems use binary to represent data in text",
  "elaborations": [
    "binary is used to represent electrical signals...",
    "whole numbers can be represented in binary...",
    ...
  ],
  "capabilities": ["Digital literacy", "Numeracy"]
}
```

### Design Thinking Skills Structure

Design thinking is organized hierarchically:
```
Design thinking skills/
├── Project management
├── Investigating and defining
├── Designing
├── Producing and implementing
└── Evaluating
```

Each subsection contains content descriptors with codes, descriptions, and elaborations.

## Comparison with ACARA Format

The WA curriculum JSON provides equivalent functionality to ACARA JSONLD:
- ✅ Unique curriculum codes
- ✅ Elaborations (teaching examples)
- ✅ Capability cross-references
- ✅ Searchable content
- ✅ Year-level organization
- ✅ Achievement standards

Differences:
- Simpler JSON format (vs. JSON-LD semantic graph)
- State-specific (WA only vs. national)
- Digital Technologies only (vs. full Technologies learning area)

## Example Use Cases

### Lesson Planning
```bash
# Find all Year 8 data representation content
node wa-curriculum-helper.cjs get-strand "Year 8" "Data representation"

# Get specific descriptor for lesson alignment
node wa-curriculum-helper.cjs get-descriptor WA8DIGDR1
```

### Curriculum Mapping
```bash
# List all codes for a unit planner
node wa-curriculum-helper.cjs list-codes "Year 9"

# Find all privacy-related content across years
node wa-curriculum-helper.cjs search "privacy"
```

### Assessment Design
```bash
# Get achievement standard for rubric creation
node wa-curriculum-helper.cjs achievement-standard "Year 10"

# Find elaborations for assessment task examples
node wa-curriculum-helper.cjs get-descriptor WA10DIGDI4
```

### Cross-Curricular Planning
```bash
# Find all Numeracy links in Year 7
node wa-curriculum-helper.cjs by-capability "Numeracy" "Year 7"

# Search for literacy integration opportunities
node wa-curriculum-helper.cjs by-capability "Literacy" "Year 8"
```

## Tips for Effective Use

1. **Use codes in documentation** - Reference WA curriculum codes (e.g., WA7DIGDR1) in lesson plans for traceability
2. **Leverage elaborations** - Use the provided teaching examples to guide instruction
3. **Map capabilities** - Check capability tags to ensure integrated learning
4. **Check progressions** - Compare descriptors across year levels to understand skill development
5. **Align assessments** - Use achievement standards to inform assessment criteria

## Support and Maintenance

This curriculum data is extracted from official SCSA documentation (2026 implementation). For updates or questions about the curriculum content itself, refer to the School Curriculum and Standards Authority (SCSA) website.

For issues with this skill or helper utility, check the parent directory for documentation and update scripts.
