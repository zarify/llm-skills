# Using Curriculum Lookup for Lesson Content Creation

Quick reference for using the curriculum helper when authoring lesson content.

## Before Creating Lessons

### 1. Identify Relevant Descriptors

```bash
# Search by topic
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"
node curriculum-helper.cjs search Technologies.jsonld "binary" "Year 7"
node curriculum-helper.cjs search Technologies.jsonld "algorithm" "Year 7"

# List all for the year level
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7" | grep AC9TDI
```

### 2. Get Full Details

```bash
# Get descriptor with all elaborations
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8K04

# Output shows:
# - What students need to learn (description)
# - How they might demonstrate it (elaborations)
# - Cross-curricular links (skillsEmbodied)
```

### 3. Check Cross-Curricular Requirements

```bash
# Get relevant capability indicators
node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 7"
node curriculum-helper.cjs capability-indicators Critical-and-creative-thinking.jsonld "Year 7"
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
# Digital systems
node curriculum-helper.cjs search Technologies.jsonld "digital system" "Year 7"

# Data and information
node curriculum-helper.cjs search Technologies.jsonld "data" "Year 7"

# Algorithms and programming
node curriculum-helper.cjs search Technologies.jsonld "algorithm" "Year 7"

# Privacy and security
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"
```

### By Year Band

```bash
# Single year
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7"

# Multiple years (in code)
const descriptors = getContentDescriptorsByYear('Technologies.jsonld', ['Year 7', 'Year 8']);
```

### Filtering Results

```bash
# Just Digital Technologies descriptors
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7" | jq '.[] | select(.code | startswith("AC9TDI"))'

# Just Design and Technologies descriptors  
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7" | jq '.[] | select(.code | startswith("AC9TDE"))'

# Count descriptors
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7" | jq '. | length'
```

## Integration Workflow

### Step 1: Topic Research
```bash
# What does ACARA say about this topic?
node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"
```

### Step 2: Understand Requirements
```bash
# Get the full descriptor
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI6P09

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
node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8K04

# Check its skillsEmbodied for related capabilities
# Look up those capability codes in the capability files
```

### Coverage Checking

```bash
# Get all Year 7-8 Digital Technologies descriptors
node curriculum-helper.cjs list-by-year Technologies.jsonld "Year 7" | \
  jq '.[] | select(.code | startswith("AC9TDI")) | .code'

# Creates checklist of all codes to address
```

### Elaboration Mining

Elaborations are gold for:
- Real-world examples
- Teaching strategies
- Assessment ideas
- Age-appropriate scenarios

Always read ALL elaborations when planning lessons.

## Example: Privacy Lesson Planning

```bash
# 1. Find privacy descriptors
$ node curriculum-helper.cjs search Technologies.jsonld "privacy" "Year 7"
# Returns: AC9TDI6P09, AC9TDI8P09

# 2. Get Year 5-6 version for scaffolding
$ node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI6P09
# Shows passphrases, 2FA, device security

# 3. Get Year 7-8 version
$ node curriculum-helper.cjs get-descriptor Technologies.jsonld AC9TDI8P09  
# Different focus - might not be about privacy!

# 4. Check Digital Literacy links
$ node curriculum-helper.cjs capability-indicators Digital-literacy.jsonld "Year 5"
# Shows DLDSWB4_1, DLDSWB4_2 (privacy indicators)

# 5. Document in lesson plan
```

Result: Informed lesson sequence that:
- Addresses correct descriptors for year level
- Includes elaboration examples
- Links to capability progressions
- Scaffolds from prior year understanding

## Capability Codes Reference

When you see `skillsEmbodied` IDs like:
- `http://vocabulary.curriculum.edu.au/MRAC/2024/04/GC/DL/...` = Digital Literacy
- `.../GC/CCT/...` = Critical and Creative Thinking
- `.../GC/N/...` = Numeracy
- `.../GC/L/...` = Literacy
- `.../GC/EU/...` = Ethical Understanding
- `.../GC/ICU/...` = Intercultural Understanding
- `.../GC/PSC/...` = Personal and Social Capability

Look these up in the corresponding capability file.
