# Using Curriculum Lookup for Lesson Content Creation

Quick reference for using the curriculum helper when authoring lesson content across **all Australian Curriculum learning areas**.

## Discover Available Files

```bash
# See all available curriculum files grouped by category
node curriculum-helper.cjs list-files
```

This returns learning areas (TEC, ENG, MAT, SCI, HASS, HPE, ART, LAN), general capabilities (DL, CCT, EU, IU, L, N, PSC), and cross-curriculum priorities (AA, A_TSI, S).

## Before Creating Lessons

### 1. Identify Relevant Descriptors

```bash
# Search by topic within a specific learning area
node curriculum-helper.cjs search TEC.jsonld "privacy" "Year 7"
node curriculum-helper.cjs search SCI.jsonld "energy" "Year 8"
node curriculum-helper.cjs search MAT.jsonld "algebra" "Year 9"
node curriculum-helper.cjs search ENG.jsonld "persuasive" "Year 7"
node curriculum-helper.cjs search HASS.jsonld "democracy" "Year 6"

# Search across ALL learning areas at once
node curriculum-helper.cjs search-all "sustainability" "Year 7"
node curriculum-helper.cjs search-all "algorithm" "Year 7"
node curriculum-helper.cjs search-all "data" "Year 9"

# List all descriptors for a year level
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7" | grep AC9TDI
node curriculum-helper.cjs list-by-year SCI.jsonld "Year 8"
```

### 2. Get Full Details

```bash
# Get descriptor with all elaborations
node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8K04

# Output shows:
# - What students need to learn (description)
# - How they might demonstrate it (elaborations)
# - Cross-curricular links (skillsEmbodied)

# Works for any learning area
node curriculum-helper.cjs get-descriptor SCI.jsonld AC9S8U04
node curriculum-helper.cjs get-descriptor ENG.jsonld AC9E7LY06
```

### 3. Check Cross-Curricular Requirements

```bash
# Get relevant capability indicators
node curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"
node curriculum-helper.cjs capability-indicators CCT.jsonld "Year 7"
node curriculum-helper.cjs capability-indicators N.jsonld "Year 5"
node curriculum-helper.cjs capability-indicators L.jsonld "Year 9"
```

### 4. Check Cross-Curriculum Priorities

```bash
# Get organising ideas from cross-curriculum priorities
node curriculum-helper.cjs get-priorities S.jsonld
node curriculum-helper.cjs get-priorities A_TSI.jsonld
node curriculum-helper.cjs get-priorities AA.jsonld
```

## During Lesson Content Creation

### In Content Files

Reference descriptors in lesson content where appropriate:

```markdown
# Binary Number Systems

### What we'll learn
* Understand how digital systems represent whole numbers in binary
* Count in binary from 0 to 31
* Recognise that one byte = 8 bits (0-255)

<!-- Aligns with AC9TDI8K04 -->
```

### In lesson-improvements.md

Document curriculum coverage and suggestions:

```markdown
## Curriculum Coverage

### Content Descriptors Addressed
- **AC9TDI8K04**: explain how and why digital systems represent integers in binary
  - ✓ Elaboration 1: Counting in binary from 0 to 31, understanding bytes
  - ✓ Elaboration 2: Converting characters to Unicode then binary
  - ⚠ Elaboration 3: Circuit operations (AND/OR gates) - needs interactive component

### Cross-Curricular Capabilities
- **DLCA5_1** (Digital Literacy): Use planning tools for project work
- **N/ca0b07c5** (Numeracy): Number patterns and operations

### Gaps and Extensions
- Circuit simulation component needed for Elaboration 3
- Extension activity: Hexadecimal conversion (prepares for Year 9-10)
```

## Common Search Patterns

### By Topic Area

```bash
# Technologies — Digital systems, algorithms, privacy
node curriculum-helper.cjs search TEC.jsonld "digital system" "Year 7"
node curriculum-helper.cjs search TEC.jsonld "algorithm" "Year 7"

# Science — forces, ecosystems, chemical reactions
node curriculum-helper.cjs search SCI.jsonld "force" "Year 7"
node curriculum-helper.cjs search SCI.jsonld "ecosystem" "Year 9"

# Mathematics — fractions, probability, geometry
node curriculum-helper.cjs search MAT.jsonld "fraction" "Year 5"
node curriculum-helper.cjs search MAT.jsonld "probability" "Year 8"

# English — narrative, comprehension, grammar
node curriculum-helper.cjs search ENG.jsonld "narrative" "Year 6"
node curriculum-helper.cjs search ENG.jsonld "comprehension" "Year 3"

# HASS — geography, history, civics
node curriculum-helper.cjs search HASS.jsonld "geography" "Year 7"

# Health & PE, Arts, Languages
node curriculum-helper.cjs search HPE.jsonld "nutrition" "Year 7"
node curriculum-helper.cjs search ART.jsonld "composition" "Year 5"
node curriculum-helper.cjs search LAN.jsonld "vocabulary" "Year 4"
```

### Cross-Learning-Area Search

```bash
# Find a concept across every learning area at once
node curriculum-helper.cjs search-all "sustainability" "Year 7"
node curriculum-helper.cjs search-all "data" "Year 9"
node curriculum-helper.cjs search-all "pattern" "Year 5"
```

### By Year Band

```bash
# Single year
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7"
node curriculum-helper.cjs list-by-year SCI.jsonld "Year 9"
```

### Filtering Results

```bash
# Just Digital Technologies descriptors within Technologies
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7" | jq '.[] | select(.code | startswith("AC9TDI"))'

# Just Design and Technologies descriptors
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7" | jq '.[] | select(.code | startswith("AC9TDE"))'

# Filter Science by a strand prefix
node curriculum-helper.cjs list-by-year SCI.jsonld "Year 8" | jq '.[] | select(.code | startswith("AC9S8U"))'

# Count descriptors for a year level
node curriculum-helper.cjs list-by-year MAT.jsonld "Year 7" | jq '. | length'
```

## Integration Workflow

### Step 1: Topic Research
```bash
# What does ACARA say about this topic?
node curriculum-helper.cjs search TEC.jsonld "privacy" "Year 7"

# Or search across all subjects if the topic is cross-curricular
node curriculum-helper.cjs search-all "sustainability" "Year 7"
```

### Step 2: Understand Requirements
```bash
# Get the full descriptor
node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI6P09

# Note:
# - Main learning outcome (description)
# - Specific examples (elaborations)
# - Cross-curricular links
```

### Step 3: Plan Coverage
Create checklist in `lesson-improvements.md`:

```markdown
### AC9TDI6P09: Privacy and Security Strategies

Elaborations to address:
- [ ] 1. Multiple accounts with different passphrases
- [ ] 2. Two-factor authentication
- [ ] 3. Device security (lock screens, updates)

Lessons:
- 01-digital-footprints.md - introduces concept
- 02-cafe-analogy.md - explains data collection
- 06-managing-footprints.md - addresses all elaborations
```

### Step 4: Create Content
Write lessons addressing each elaboration with:
- Age-appropriate explanations
- Real-world examples from elaborations
- Interactive checks for understanding
- Australian context

### Step 5: Document Coverage
In `lesson-improvements.md`, document:
- Which descriptors are fully/partially addressed
- Which elaborations are covered
- Cross-curricular capability links
- Gaps requiring future components/content

## Tips

### Finding Related Content

Descriptors often reference each other:

```bash
# Find a descriptor
node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8K04

# Check its skillsEmbodied for related capabilities
# Look up those capability codes in the capability files (DL, CCT, N, L, etc.)
```

### Coverage Checking

```bash
# Get all Year 7-8 Digital Technologies descriptors
node curriculum-helper.cjs list-by-year TEC.jsonld "Year 7" | \
  jq '.[] | select(.code | startswith("AC9TDI")) | .code'

# Get all Year 8 Science descriptors
node curriculum-helper.cjs list-by-year SCI.jsonld "Year 8" | \
  jq '[.[] | .code]'
```

### Elaboration Mining

Elaborations are gold for:
- Real-world examples
- Teaching strategies
- Assessment ideas
- Age-appropriate scenarios

Always read ALL elaborations when planning lessons.

## Example: Privacy Lesson Planning (Technologies)

```bash
# 1. Find privacy descriptors
$ node curriculum-helper.cjs search TEC.jsonld "privacy" "Year 7"
# Returns: AC9TDI6P09, AC9TDI8P09

# 2. Get Year 5-6 version for scaffolding
$ node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI6P09
# Shows passphrases, 2FA, device security

# 3. Get Year 7-8 version
$ node curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8P09
# Different focus - might not be about privacy!

# 4. Check Digital Literacy links
$ node curriculum-helper.cjs capability-indicators DL.jsonld "Year 5"
# Shows DLDSWB4_1, DLDSWB4_2 (privacy indicators)

# 5. Check cross-curriculum priorities
$ node curriculum-helper.cjs get-priorities S.jsonld
# Review Sustainability organising ideas for context

# 6. Document in lesson plan
```

## Example: Science Energy Lesson Planning

```bash
# 1. Find energy descriptors in Science
$ node curriculum-helper.cjs search SCI.jsonld "energy" "Year 8"

# 2. Check if energy appears in other learning areas too
$ node curriculum-helper.cjs search-all "energy" "Year 8"
# May find links in Technologies, HASS, HPE

# 3. Get full descriptor details
$ node curriculum-helper.cjs get-descriptor SCI.jsonld AC9S8U04

# 4. Check Numeracy links (calculations, measurement)
$ node curriculum-helper.cjs capability-indicators N.jsonld "Year 8"

# 5. Check Critical and Creative Thinking links
$ node curriculum-helper.cjs capability-indicators CCT.jsonld "Year 8"
```

Result: Informed lesson sequence that:
- Addresses correct descriptors for year level
- Includes elaboration examples
- Links to capability progressions
- Scaffolds from prior year understanding

## Capability Codes Reference

When you see `skillsEmbodied` IDs like:
- `http://vocabulary.curriculum.edu.au/MRAC/2024/04/GC/DL/...` → **DL.jsonld** (Digital Literacy)
- `.../GC/CCT/...` → **CCT.jsonld** (Critical and Creative Thinking)
- `.../GC/N/...` → **N.jsonld** (Numeracy)
- `.../GC/L/...` → **L.jsonld** (Literacy)
- `.../GC/EU/...` → **EU.jsonld** (Ethical Understanding)
- `.../GC/IU/...` → **IU.jsonld** (Intercultural Understanding)
- `.../GC/PSC/...` → **PSC.jsonld** (Personal and Social Capability)

Look these up in the corresponding capability file.

## Learning Area File Reference

| File | Learning Area |
|------|--------------|
| `TEC.jsonld` | Technologies (Digital Technologies + Design and Technologies) |
| `ENG.jsonld` | English |
| `MAT.jsonld` | Mathematics |
| `SCI.jsonld` | Science |
| `HASS.jsonld` | Humanities and Social Sciences |
| `HPE.jsonld` | Health and Physical Education |
| `ART.jsonld` | The Arts |
| `LAN.jsonld` | Languages |

## Cross-Curriculum Priority File Reference

| File | Priority |
|------|----------|
| `S.jsonld` | Sustainability |
| `A_TSI.jsonld` | Aboriginal and Torres Strait Islander Histories and Cultures |
| `AA.jsonld` | Asia and Australia's Engagement with Asia |
