# WA SCSA Curriculum Skill - Quick Reference

## One-Line Commands

```bash
# Get descriptor by code
node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1

# Search for content
node wa-curriculum-helper.cjs search "binary" "Year 7"

# List all codes
node wa-curriculum-helper.cjs list-codes "Year 7"

# Get strand
node wa-curriculum-helper.cjs get-strand "Year 7" "Digital systems"

# Achievement standard
node wa-curriculum-helper.cjs achievement-standard "Year 7"

# By capability
node wa-curriculum-helper.cjs by-capability "Numeracy" "Year 7"

# List all year content
node wa-curriculum-helper.cjs list-by-year "Year 7"
```

## Common Patterns

### Lesson Planning for Binary (Year 7)

```bash
# 1. Search for relevant content
node wa-curriculum-helper.cjs search "binary" "Year 7"
# Returns: WA7DIGDR1

# 2. Get full details with elaborations
node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1
# Returns: 4 elaborations with teaching examples

# 3. Check capability links
# Output shows: Digital literacy, Numeracy
```

### Unit Planning (Year 8 Digital Systems)

```bash
# Get all Digital systems content for Year 8
node wa-curriculum-helper.cjs get-strand "Year 8" "Digital systems"

# Get Year 8 achievement standard for assessment criteria
node wa-curriculum-helper.cjs achievement-standard "Year 8"
```

### Numeracy Integration Check

```bash
# Find all Numeracy-linked descriptors in Year 9
node wa-curriculum-helper.cjs by-capability "Numeracy" "Year 9"

# Then get details for each code
node wa-curriculum-helper.cjs get-descriptor WA9DIGDR1
node wa-curriculum-helper.cjs get-descriptor WA9DIGAD1
```

### Curriculum Coverage Report

```bash
# List all codes for the year
node wa-curriculum-helper.cjs list-codes "Year 10"

# Get complete list with descriptions
node wa-curriculum-helper.cjs list-by-year "Year 10" > year10-coverage.json
```

## Code Patterns

### Year Level Codes
- **Pre-primary**: `WAPDIG...` (e.g., WAPDIGDS1)
- **Year 1-10**: `WA[N]DIG...` (e.g., WA7DIGDR1, WA10DIGAD2)

### Strand Codes
- **DS** - Digital systems
- **DR** - Data representation  
- **PS** - Privacy and security
- **DI** - Digital implementation
- **AD** - Acquiring, managing and analysing data (Years 7-10)

### Design Thinking Codes
- **DTPM** - Project management
- **DTID** - Investigating and defining
- **DTDE** - Designing
- **DTPI** - Producing and implementing
- **DTEV** - Evaluating

## Year Level Quick Reference

| Year | Total Codes | With Elaborations | Key Focus |
|------|-------------|-------------------|-----------|
| PP | 10 | 5 | Digital awareness, safety basics |
| 1-2 | 10-11 | 4-5 | Digital systems, simple data |
| 3-6 | 11-12 | 4-5 | Networks, algorithms, data types |
| 7-8 | 16-18 | 6-8 | Binary, programming, cybersecurity |
| 9-10 | 18-19 | 8-10 | Data structures, complex algorithms |

## Strands by Year

### All Years (PP-10)
- Digital systems
- Data representation
- Privacy and security
- Digital implementation
- Design thinking skills

### Years 7-10 Only
- Acquiring, managing and analysing data

## Capabilities

All descriptors tagged with one or more:
- Digital literacy (most common)
- Numeracy (data, algorithms, binary)
- Critical and creative thinking (problem-solving)
- Literacy (communication, documentation)
- Personal and social capability (collaboration)
- Ethical understanding (responsible use)

## Output Format Examples

### Descriptor Output
```json
{
  "code": "WA7DIGDR1",
  "description": "...",
  "elaborations": ["...", "..."],
  "capabilities": ["Digital literacy", "Numeracy"],
  "strand": "Data representation",
  "yearLevel": "Year 7"
}
```

### Search Results
```json
[
  {
    "code": "WA7DIGDR1",
    "description": "...",
    "strand": "Data representation",
    "yearLevel": "Year 7",
    "elaborations": [...],
    "capabilities": [...]
  }
]
```

### Code List
```json
[
  "WA7DIGDS1",
  "WA7DIGDS2",
  "WA7DIGDR1",
  ...
]
```

## Integration with Claude

When using this skill with Claude:

1. **Reference codes in prompts**: "Create a lesson for WA7DIGDR1"
2. **Use search for discovery**: "Find Year 8 cybersecurity content"
3. **Check coverage**: "List all Year 9 codes we haven't covered"
4. **Get elaborations**: "What are the teaching examples for WA10DIGDI4?"

## Troubleshooting

### "Descriptor not found"
- Check code format: Must be exact (e.g., WA7DIGDR1, not wa7digdr1)
- Verify year exists: PP, Year 1-10 only
- Check strand code is valid

### "No results"
- Try broader search terms
- Remove year filter to search all years
- Check spelling

### File not found
- Ensure you're in the skill directory
- Check `curriculum/digital-technologies.json` exists
- Path should be relative to wa-curriculum-helper.cjs

## Tips

- **Use jq for filtering**: `node wa-curriculum-helper.cjs list-by-year "Year 7" | jq 'map({code, description})'`
- **Save to file**: `node wa-curriculum-helper.cjs get-descriptor WA7DIGDR1 > descriptor.json`
- **Pipe to grep**: `node wa-curriculum-helper.cjs search "privacy" | grep -i "personal"`
- **Count results**: `node wa-curriculum-helper.cjs list-codes "Year 7" | jq 'length'`
