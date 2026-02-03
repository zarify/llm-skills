# Australian Curriculum Lookup Tool

JavaScript utilities for extracting ACARA curriculum content descriptors and elaborations from JSONLD files.

## Quick Start

```bash
# Search for privacy-related content in Year 7
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"

# Get full descriptor with elaborations
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8K04

# List all Year 7 content descriptors
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7"

# Get Digital Literacy capability indicators
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
```

## Files

- **curriculum-helper.cjs** - Main helper script (CLI and module)
- **example-usage.cjs** - Comprehensive usage examples
- **SKILL.md** - Claude skill documentation
- **curriculum/** - ACARA JSONLD curriculum files

## Available Commands

### search
Search for content descriptors by keyword, optionally filtered by year level.

```bash
node curriculum-helper.cjs search <filename> <search-term> [year-level]
```

**Example:**
```bash
node curriculum-helper.cjs search Technologies.jsonld "binary" "Year 7"
```

### get-descriptor
Get complete details of a content descriptor including all elaborations.

```bash
node curriculum-helper.cjs get-descriptor <filename> <code>
```

**Example:**
```bash
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8K04
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
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7"
```

### capability-indicators
Get cross-curricular capability indicators for a year level.

```bash
node curriculum-helper.cjs capability-indicators <filename> <year-level>
```

**Example:**
```bash
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
```

## Using as a Module

```javascript
const {
  searchContent,
  getDescriptorDetails,
  getContentDescriptorsByYear,
  getCapabilityIndicators,
} = require('./curriculum-helper.cjs');

// Search for content
const results = searchContent('Technologies.jsonld', 'binary', 'Year 7');

// Get full descriptor details
const descriptor = getDescriptorDetails('Technologies.jsonld', 'AC9TDI8K04');
console.log(descriptor.description);
descriptor.elaborations.forEach(elab => {
  console.log(`- ${elab.description}`);
});

// List all for a year
const year7Content = getContentDescriptorsByYear('Technologies.jsonld', 'Year 7');

// Get capability indicators
const dlIndicators = getCapabilityIndicators('Digital-literacy.jsonld', 'Year 7');
```

See `example-usage.cjs` for comprehensive examples.

## Available Curriculum Files

### Learning Areas
- **Technologies.jsonld** - Full Technologies learning area
  - Digital Technologies (AC9TDI*)
  - Design and Technologies (AC9TDE*)

### Cross-Curricular Capabilities
- **Digital-literacy.jsonld**
- **Critical-and-creative-thinking.jsonld**
- **Ethical-understanding.jsonld**
- **Intercultural-understanding.jsonld**
- **Literacy.jsonld**
- **Numeracy.jsonld**
- **Personal-and-social-capability.jsonld**

## Data Structure

### Content Descriptors (Learning Areas)
Each content descriptor includes:
- **code** - ACARA code (e.g., AC9TDI8K04)
- **description** - What students should learn
- **yearLevels** - Year levels covered
- **elaborations** - Detailed examples and applications
- **skillsEmbodied** - Cross-curricular capability links

### Elaborations
Provide specific examples of how students might demonstrate understanding:
- Concrete scenarios
- Teaching strategies
- Assessment opportunities

### Capability Indicators (Cross-Curricular)
Different structure with:
- **proficiencyLevel** - Progression level
- **indicators** - Observable behaviors/skills

## Year Levels

- Foundation (Prep/Kindy)
- Year 1 - Year 10

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
# Planning a privacy lesson for Year 7-8

# 1. Find relevant descriptors
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"
# Returns: AC9TDI8P09, AC9TDI6P09, etc.

# 2. Get full details and elaborations
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI6P09
# Shows:
# - 3 elaborations with specific examples
# - Year 5-6 coverage
# - Cross-curricular links

# 3. Check Digital Literacy requirements
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
# Shows DLDSWB5_1: "recognise their digital footprint is valuable..."

# 4. Document in lesson-improvements.md:
# - AC9TDI6P09: Privacy and security strategies
# - Elaboration coverage: passphrases, two-factor auth
# - Cross-curricular: DLDSWB5_1 (Digital Literacy)
```

## API Reference

### Functions

#### `searchContent(filename, searchTerm, yearLevels?)`
Search for descriptors matching keywords.

#### `getDescriptorDetails(filename, descriptorCode)`
Get full descriptor with elaborations.

#### `getContentDescriptorsByYear(filename, yearLevels)`
List all descriptors for year level(s).

#### `getCapabilityIndicators(filename, yearLevels)`
Get cross-curricular indicators.

#### `getElaborations(filename, descriptorId)`
Get elaborations for a descriptor.

### Utility Functions

#### `getValue(item, property)`
Extract value from JSONLD property.

#### `getValues(item, property)`
Extract all values from JSONLD property array.

#### `getYearLevels(item)`
Get human-readable year levels for an item.

## Notes

- All output is valid JSON for easy parsing
- Pipe to `jq` for filtering: `node curriculum-helper.cjs list-by-year ... | jq '.[] | select(.code | startswith("AC9TDI"))'`
- Use with `grep` for quick searches: `node curriculum-helper.cjs list-by-year ... | grep -i "algorithm"`
- Codes starting with AC9TDI = Digital Technologies
- Codes starting with AC9TDE = Design and Technologies

## Source

Curriculum data from [Australian Curriculum, Assessment and Reporting Authority (ACARA)](https://www.australiancurriculum.edu.au/)

Machine-readable curriculum data: https://www.australiancurriculum.edu.au/resources/curriculum-rdf/
