---
name: lessons-acara-lookup
description: Tool for looking up curriculum content descriptors and elaborations from the Australian Curriculum (ACARA) machine-readable documentation
---

# Australian Curriculum Lookup Skill

This skill provides utilities to extract curriculum information from ACARA JSONLD files for lesson planning and curriculum coverage checking.

## Files

- `curriculum-helper.cjs` - JavaScript helper for extracting curriculum data
- `curriculum/` - JSONLD curriculum files from ACARA

## Available Curriculum Files

### Learning Areas
- `Technologies.jsonld` - Technologies learning area (includes Digital Technologies)

### Cross-Curricular Capabilities
- `Digital-literacy.jsonld`
- `Critical-and-creative-thinking.jsonld`
- `Ethical-understanding.jsonld`
- `Intercultural-understanding.jsonld`
- `Literacy.jsonld`
- `Numeracy.jsonld`
- `Personal-and-social-capability.jsonld`

## Usage

### Search for content descriptors by keyword

```bash
node curriculum-helper.cjs search Technologies.jsonld "binary" "Year 7"
```

Returns content descriptors matching the search term, optionally filtered by year level.

### Get content descriptors for a year level

```bash
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7"
```

Lists all content descriptors for the specified year level.

### Get full descriptor details with elaborations

```bash
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8K04
```

Returns complete details for a content descriptor including:
- Code (e.g., AC9TDI8K04)
- Description/title
- Year levels
- All elaborations
- Skills embodied
- Achievement levels

### Get cross-curricular capability indicators

```bash
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
```

Returns indicators from cross-curricular capabilities for a year level.

## Use in Lesson Planning

When creating lesson content, use this tool to:

1. **Search for relevant descriptors** by topic keywords
2. **Get full descriptor details** to understand requirements and see elaborations
3. **Check curriculum coverage** by listing all descriptors for target year levels
4. **Cross-reference capabilities** to ensure holistic learning

### Example Workflow

```bash
# Find privacy-related content for Year 7-8
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"

# Get full details including elaborations
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8P09

# Check Digital Literacy capability requirements
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
```

## Integration with Lesson Creation

Reference curriculum codes in lesson content metadata and improvements documents to:
- Track which descriptors are addressed
- Ensure comprehensive elaboration coverage
- Document cross-curricular capability links
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
- Reference `skillsEmbodied` (cross-curricular capabilities)

### Indicators (Cross-Curricular Capabilities)  
- Have a `statementLabel` of "Indicator"
- Include `proficiencyLevel` (progression levels)
- Different structure from learning area content

The helper abstracts these differences for easy access.
