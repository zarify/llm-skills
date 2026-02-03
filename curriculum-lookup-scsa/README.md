# Western Australian Curriculum Lookup Skill (SCSA)

A Claude AI skill for querying the Western Australian Digital Technologies curriculum (SCSA, 2026 implementation).

## Features

- **149 curriculum codes** - Precise curriculum referencing
- **167 elaborations** - Teaching examples and guidance
- **Capability mapping** - Cross-curricular connections
- **Full text search** - Find content by keywords
- **Year-level organization** - Pre-primary to Year 10

## Quick Start

```bash
# Get a specific descriptor
node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1

# Search for content
node wa-curriculum-helper.cjs search "binary" "Year 7"

# List all codes for a year
node wa-curriculum-helper.cjs list-codes "Year 7"

# See all available commands
node wa-curriculum-helper.cjs
```

## Files

- **SKILL.md** - Complete skill documentation
- **wa-curriculum-helper.cjs** - Command-line helper utility
- **example-usage.cjs** - Usage examples as a Node.js script
- **curriculum/** - Curriculum data files
  - `digital-technologies.json` - Enhanced WA curriculum (Pre-primary to Year 10)

## Example Output

```json
{
  "code": "WA7DIGDR1",
  "description": "Digital systems use binary to represent data in text",
  "elaborations": [
    "binary is used to represent electrical signals...",
    "whole numbers can be represented in binary...",
    "digital systems represent text as a sequence...",
    "digital systems represent data in binary..."
  ],
  "capabilities": ["Digital literacy", "Numeracy"],
  "strand": "Data representation",
  "yearLevel": "Year 7"
}
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `get-descriptor <code>` | Get full descriptor details | `get-descriptor WA7DIGDR1` |
| `list-by-year <year>` | List all descriptors for year | `list-by-year "Year 7"` |
| `search <term> [year]` | Search by keyword | `search "binary" "Year 7"` |
| `get-strand <year> <strand>` | Get strand content | `get-strand "Year 7" "Digital systems"` |
| `achievement-standard <year>` | Get achievement standard | `achievement-standard "Year 7"` |
| `list-codes <year>` | List all codes for year | `list-codes "Year 7"` |
| `by-capability <cap> [year]` | Find by capability | `by-capability "Numeracy" "Year 7"` |

## Use Cases

### Lesson Planning
- Find relevant curriculum content by topic
- Get teaching examples from elaborations
- Reference specific curriculum codes in plans
- Ensure capability coverage

### Assessment Design
- Align assessments with achievement standards
- Use elaborations for task examples
- Track curriculum coverage

### Curriculum Mapping
- Generate year-level overviews
- Map progression across years
- Identify capability connections

### Reporting
- Reference specific curriculum codes
- Document curriculum coverage
- Support evidence collection

## Data Structure

The curriculum JSON is organized as:

```
Digital Technologies
├── Pre-primary (10 codes)
├── Year 1 (10 codes)
├── ...
└── Year 10 (18 codes)
    ├── Digital systems
    ├── Data representation
    ├── Privacy and security
    ├── Digital implementation
    ├── Acquiring, managing and analysing data
    └── Design thinking skills
        ├── Project management
        ├── Investigating and defining
        ├── Designing
        ├── Producing and implementing
        └── Evaluating
```

## Curriculum Coverage

| Year | Codes | Elaborations | Key Strands |
|------|-------|--------------|-------------|
| Pre-primary | 10 | 18 | All 5 strands + design thinking |
| Year 1-2 | 10-11 | 12-15 | All 5 strands + design thinking |
| Year 3-6 | 11-12 | 11-15 | All 5 strands + design thinking |
| Year 7-10 | 16-19 | 15-23 | All 6 strands + design thinking |

**Total**: 149 codes, 167 elaborations

## Cross-Curricular Capabilities

- Digital literacy
- Numeracy
- Critical and creative thinking
- Personal and social capability
- Ethical understanding
- Literacy

## Data Source

Curriculum data extracted from official SCSA Digital Technologies curriculum PDF (2026 implementation). Enhanced extraction includes:

- All curriculum codes (e.g., WA7DIGDR1)
- Content descriptions
- Elaborations (teaching examples)
- Capability cross-references
- Achievement standards

## Programmatic Access

Import the helper as a module:

```javascript
const helper = require('./wa-curriculum-helper.cjs');

// Get descriptor
const descriptor = helper.getDescriptorByCode('WA7DIGDR1');

// Search content
const results = helper.searchContent('binary', 'Year 7');

// List codes
const codes = helper.listCodesByYear('Year 7');

// Get by capability
const numeracyContent = helper.getByCapability('Numeracy', 'Year 7');
```

See `example-usage.cjs` for more examples.

## Comparison with ACARA Skill

This skill provides equivalent functionality to the ACARA curriculum lookup skill, adapted for the Western Australian curriculum:

| Feature | ACARA | WA SCSA |
|---------|-------|---------|
| Curriculum codes | ✅ AC9TDI8K04 | ✅ WA7DIGDR1 |
| Elaborations | ✅ | ✅ |
| Search by code | ✅ | ✅ |
| Search by keyword | ✅ | ✅ |
| Capability mapping | ✅ | ✅ |
| Helper utility | ✅ | ✅ |
| Coverage | National, K-10 | WA only, PP-10 |
| Format | JSON-LD | Enhanced JSON |

## Updates

To update the curriculum data:

1. Obtain latest SCSA curriculum PDF
2. Run enhanced extraction script
3. Replace `curriculum/digital-technologies.json`

See parent directory for extraction tools.

## License

Curriculum content © School Curriculum and Standards Authority (SCSA), Western Australia.

Helper utilities and skill implementation are provided for educational use.
