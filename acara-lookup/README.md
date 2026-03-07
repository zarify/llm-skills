# Australian Curriculum Lookup Tool

JavaScript utilities for extracting ACARA curriculum content descriptors and elaborations from JSONLD files. Covers **all** Australian Curriculum learning areas, general capabilities, and cross-curriculum priorities.

## Quick Start

```bash
# List all available curriculum files
node curriculum-helper.cjs list-files

# Search for "algorithm" across ALL learning areas
node curriculum-helper.cjs search-all "algorithm" "Year 7"

# Search within a specific learning area
node curriculum-helper.cjs search TEC.jsonld "privacy" "Year 7"

# Get full descriptor with elaborations
node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8K04

# List all Year 7 content descriptors for a learning area
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7"

# Get Digital Literacy capability indicators
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"

# Get cross-curriculum priority organising ideas
node curriculum-helper.cjs get-priorities S.jsonld
```

## Files

- **curriculum-helper.cjs** — Main helper script (CLI and module)
- **example-usage.cjs** — Comprehensive usage examples
- **SKILL.md** — Claude skill documentation
- **curriculum/** — ACARA JSONLD curriculum files (18 files)

## Available Commands

### list-files
List all available curriculum files, grouped by category.

```bash
node curriculum-helper.cjs list-files
```

### search-all
Search for content descriptors across **all** learning area files.

```bash
node curriculum-helper.cjs search-all <search-term> [year-level]
```

**Example:**
```bash
node curriculum-helper.cjs search-all "sustainability" "Year 5"
```

### search
Search for content descriptors within a single file by keyword, optionally filtered by year level.

```bash
node curriculum-helper.cjs search <filename> <search-term> [year-level]
```

**Example:**
```bash
node curriculum-helper.cjs search TEC.jsonld "binary" "Year 7"
```

### get-descriptor
Get complete details of a content descriptor including all elaborations.

```bash
node curriculum-helper.cjs get-descriptor <filename> <code>
```

**Example:**
```bash
node curriculum-helper.cjs get-descriptor SCI.jsonld AC9S7U04
```

Output includes:
- Descriptor code and description
- Year levels covered
- All elaborations (detailed examples)
- Skills embodied (cross-curricular links)
- Achievement levels

### list-by-year
List all content descriptors for a specific year level.

```bash
node curriculum-helper.cjs list-by-year <filename> <year-level>
```

**Example:**
```bash
node curriculum-helper.cjs list-by-year MAT.jsonld "Year 7"
```

### capability-indicators
Get general capability indicators for a year level.

```bash
node curriculum-helper.cjs capability-indicators <filename> <year-level>
```

**Example:**
```bash
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"
```

### get-priorities
Get cross-curriculum priority organising ideas.

```bash
node curriculum-helper.cjs get-priorities <filename>
```

**Example:**
```bash
node curriculum-helper.cjs get-priorities A_TSI.jsonld
```

## Using as a Module

```javascript
const {
  searchContent,
  searchAll,
  getDescriptorDetails,
  getContentDescriptorsByYear,
  getCapabilityIndicators,
  getPriorityOrganisingIdeas,
  listFiles,
  CURRICULUM_FILES,
} = require('./curriculum-helper.cjs');

// Search across all learning areas
const allResults = searchAll('sustainability', 'Year 5');
allResults.forEach(r => {
  console.log(`[${r.file}] ${r.code}: ${r.description}`);
});

// Search within a single file
const results = searchContent('TEC.jsonld', 'binary', 'Year 7');

// Get full descriptor details
const descriptor = getDescriptorDetails('TEC.jsonld', 'AC9TDI8K04');
console.log(descriptor.description);
descriptor.elaborations.forEach(elab => {
  console.log(`- ${elab.description}`);
});

// List all for a year
const year7Content = getContentDescriptorsByYear('ENG.jsonld', 'Year 7');

// Get capability indicators
const dlIndicators = getCapabilityIndicators('DL.jsonld', 'Year 7');

// Get cross-curriculum priority organising ideas
const ideas = getPriorityOrganisingIdeas('S.jsonld');

// List all available files
const files = listFiles();
```

See `example-usage.cjs` for comprehensive examples.

## Available Curriculum Files

### Learning Areas (8 files)
| File | Learning Area | Code prefix examples |
|------|--------------|---------------------|
| **TEC.jsonld** | Technologies | AC9TDI* (Digital Technologies), AC9TDE* (Design and Technologies) |
| **ENG.jsonld** | English | AC9E* |
| **MAT.jsonld** | Mathematics | AC9M* |
| **SCI.jsonld** | Science | AC9S* |
| **HASS.jsonld** | Humanities and Social Sciences | AC9HS* |
| **HPE.jsonld** | Health and Physical Education | AC9HP* |
| **ART.jsonld** | The Arts | AC9A* |
| **LAN.jsonld** | Languages | AC9L* |

### General Capabilities (7 files)
| File | Capability |
|------|-----------|
| **DL.jsonld** | Digital Literacy |
| **CCT.jsonld** | Critical and Creative Thinking |
| **EU.jsonld** | Ethical Understanding |
| **IU.jsonld** | Intercultural Understanding |
| **L.jsonld** | Literacy |
| **N.jsonld** | Numeracy |
| **PSC.jsonld** | Personal and Social Capability |

### Cross-Curriculum Priorities (3 files)
| File | Priority |
|------|---------|
| **AA.jsonld** | Asia and Australia's Engagement with Asia |
| **A_TSI.jsonld** | Aboriginal and Torres Strait Islander Histories and Cultures |
| **S.jsonld** | Sustainability |

## Data Structure

### Content Descriptors (Learning Areas)
Each content descriptor includes:
- **code** — ACARA code (e.g., AC9TDI8K04, AC9E7LE01, AC9M7N01)
- **description** — What students should learn
- **yearLevels** — Year levels covered
- **elaborations** — Detailed examples and applications
- **skillsEmbodied** — Cross-curricular capability links

### Elaborations
Provide specific examples of how students might demonstrate understanding:
- Concrete scenarios
- Teaching strategies
- Assessment opportunities

### Capability Indicators (General Capabilities)
Different structure with:
- **proficiencyLevel** — Progression level
- **indicators** — Observable behaviors/skills

### Organising Ideas (Cross-Curriculum Priorities)
Each organising idea includes:
- **code** — Notation code
- **title** — Short title
- **description** — What the organising idea covers

## Year Levels

- Foundation (Prep/Kindy)
- Year 1 – Year 10

Many descriptors span multiple years (e.g., Year 7-8, Year 5-6).

## Use Cases

### Lesson Planning
1. Search for relevant descriptors by topic
2. Get elaborations for teaching ideas
3. Check cross-curricular capability links
4. Document curriculum coverage

### Curriculum Coverage
- List all descriptors for target year levels
- Track which have been addressed in lessons
- Ensure comprehensive coverage across modules

### Assessment Design
- Use elaborations as assessment criteria
- Align tasks to specific descriptors
- Document curriculum alignment

## Example Workflow

```bash
# Planning a cross-curricular sustainability lesson for Year 7-8

# 1. See what files are available
node curriculum-helper.cjs list-files

# 2. Search across all learning areas for relevant descriptors
node curriculum-helper.cjs search-all "sustainability" "Year 7"
# Returns matches from SCI, HASS, TEC, etc.

# 3. Get full details from Science
node curriculum-helper.cjs get-descriptor SCI.jsonld AC9S7U04
# Shows elaborations, year levels, cross-curricular links

# 4. Check sustainability organising ideas
node curriculum-helper.cjs get-priorities S.jsonld
# Shows organising ideas for the Sustainability priority

# 5. Check Digital Literacy requirements
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"

# 6. Get Technologies descriptors for the lesson
node curriculum-helper.cjs search TEC.jsonld "data" "Year 7"

# 7. Document curriculum coverage across learning areas
```

## API Reference

### Functions

#### `searchAll(searchTerm, yearLevels?)`
Search for content descriptors across all learning area files. Returns results tagged with `file` and `learningArea`.

#### `searchContent(filename, searchTerm, yearLevels?)`
Search for descriptors matching keywords within a single file.

#### `getDescriptorDetails(filename, descriptorCode)`
Get full descriptor with elaborations.

#### `getContentDescriptorsByYear(filename, yearLevels)`
List all descriptors for year level(s).

#### `getCapabilityIndicators(filename, yearLevels)`
Get general capability indicators.

#### `getElaborations(filename, descriptorId)`
Get elaborations for a descriptor.

#### `getPriorityOrganisingIdeas(filename)`
Get organising ideas from a cross-curriculum priority file (AA.jsonld, A_TSI.jsonld, or S.jsonld).

#### `listFiles()`
List all available curriculum files grouped by category (learning-area, general-capability, cross-curriculum-priority).

### Utility Functions

#### `getValue(item, property)`
Extract value from JSONLD property.

#### `getValues(item, property)`
Extract all values from JSONLD property array.

#### `getYearLevels(item)`
Get human-readable year levels for an item.

### Constants

#### `CURRICULUM_FILES`
Object mapping each filename to its display name and category.

## Notes

- All output is valid JSON for easy parsing
- Pipe to `jq` for filtering: `node curriculum-helper.cjs search-all "algorithm" | jq '.[] | .code'`
- Use with `grep` for quick searches: `node curriculum-helper.cjs list-by-year MAT.jsonld "Year 7" | grep -i "fraction"`
- Code prefixes indicate the learning area: AC9TDI (Digital Technologies), AC9E (English), AC9M (Mathematics), AC9S (Science), AC9HS (HASS), AC9HP (HPE), AC9A (The Arts), AC9L (Languages)

## Source

Curriculum data from [Australian Curriculum, Assessment and Reporting Authority (ACARA)](https://www.australiancurriculum.edu.au/)

Machine-readable curriculum data: https://www.australiancurriculum.edu.au/resources/curriculum-rdf/
