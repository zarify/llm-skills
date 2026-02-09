````skill
---
name: h5p-widget
description: Guidance for developing custom H5P learning exercises in Moodle with UDL, PRIMM, and WA curriculum alignment.
---

# H5P Widget Skill

## Project Overview

This repository is for developing custom H5P (HTML5 Package) learning exercises and interactive content to be deployed through our Moodle Learning Management System (LMS).

## Purpose

Create engaging, interactive learning experiences for students using H5P content types. These exercises should be:
- Pedagogically sound and aligned with learning objectives
- Accessible and mobile-responsive
- Compatible with Moodle's H5P integration
- Gradeable where appropriate (xAPI/SCORM compliant)

## Pedagogical Frameworks

### Universal Design for Learning (UDL)

As an online-only school, we adhere to Universal Design for Learning principles to ensure all students can access and engage with content. When designing H5P exercises, apply the three UDL principles:

#### 1. Multiple Means of Representation (the "What" of learning)
- Provide content in multiple formats (text, audio, video, diagrams)
- Use clear, simple language with visual supports
- Offer customizable display options (text size, contrast, audio speed)
- Provide vocabulary support and symbol clarification
- Include captions and transcripts for all multimedia

#### 2. Multiple Means of Action & Expression (the "How" of learning)
- Allow students to demonstrate knowledge in various ways
- Provide scaffolding and gradual release of support
- Enable different response methods (typing, drag-drop, selecting)
- Allow for varied pacing and time to complete activities
- Support planning and strategy development

#### 3. Multiple Means of Engagement (the "Why" of learning)
- Offer choices in content, tools, and activities when possible
- Provide immediate, constructive feedback
- Create authentic, relevant learning scenarios
- Minimize distractions and threats
- Foster collaboration and community when appropriate
- Include self-assessment and reflection opportunities

UDL Implementation Checklist for H5P:
- [ ] Content presented in at least 2 formats
- [ ] All media includes text alternatives
- [ ] Students have control over pace/progression
- [ ] Multiple ways to demonstrate understanding
- [ ] Feedback is immediate and actionable
- [ ] Activity connects to real-world contexts

### PRIMM Methodology for Code-Related Exercises

When creating exercises involving programming or code, follow the PRIMM methodology:

#### P - Predict
Start by having students predict what code will do before running it.
- Present code snippets and ask students to hypothesize outcomes
- Use H5P Question Sets or Fill in the Blanks for predictions
- Include multiple-choice questions about expected behavior
- No penalty for incorrect predictions - focus on reasoning

#### R - Run
Students run the code and observe actual behavior.
- Provide interactive code environments or embedded outputs
- Use Interactive Video to show code execution step-by-step
- Compare predicted vs. actual results
- Embed live code editors when possible (CodePen, Repl.it iframes)

#### I - Investigate
Students explore and trace through the code to understand how it works.
- Use Image Hotspots on code to explain specific lines
- Create interactive code walkthroughs with Course Presentation
- Include debugging exercises using Drag and Drop
- Ask comprehension questions about code logic and flow

#### M - Modify
Students make small changes to existing code.
- Provide scaffolded coding challenges
- Use Fill in the Blanks for code completion exercises
- Create Drag Text activities for code modification
- Give specific modification goals with clear success criteria

#### M - Make
Students create their own code from scratch.
- Open-ended coding projects with clear requirements
- Use Essay/text submission for code solutions
- Branching Scenarios for design decision-making
- Provide templates and examples as starting points

PRIMM Implementation Tips:
- Progress through stages sequentially for new concepts
- Cycle through PRIMM multiple times with increasing complexity
- Combine PRIMM stages within a single H5P activity when appropriate
- Provide example solutions and explanations after submission
- Link PRIMM stages across multiple H5P activities in a sequence

### Curriculum Alignment (Western Australia)

All H5P learning exercises should be aligned with relevant curriculum standards for Western Australian students.

#### ACARA - Australian Curriculum
Use the ACARA lookup skill to access:
- Technologies learning area descriptors and exemplars
- Achievement standards for different year levels
- Content descriptions and elaborations
- Work samples and assessment guidance

When designing content, reference specific curriculum codes and ensure exercises target the appropriate achievement level.

#### SCSA - School Curriculum and Standards Authority
Use the SCSA lookup skill to access:
- Western Australian Digital Technologies curriculum
- Year level content and achievement standards
- Scope and sequence information
- Assessment principles and practices

Curriculum Integration Workflow:
1. Identify the target year level and learning area
2. Look up relevant ACARA/SCSA content descriptors
3. Design H5P exercise aligned to specific learning outcomes
4. Include curriculum codes in exercise metadata/documentation
5. Ensure assessment criteria match achievement standards
6. Provide differentiation for various proficiency levels

## Technology Stack

- H5P Framework: HTML5-based interactive content creation
- Target Platform: Moodle LMS with H5P plugin
- Languages: JavaScript, HTML, CSS, JSON
- Standards: xAPI (Experience API), SCORM when applicable

## H5P Content Structure

Each H5P content type typically consists of:

```
content-type-name/
├── library.json          # Metadata and dependencies
├── semantics.json        # Editor form structure
├── presave.js           # Optional: Data processing before save
├── scripts/
│   └── content-type.js  # Main JavaScript logic
├── styles/
│   └── content-type.css # Styling
├── language/
│   └── en.json          # Translations
└── icon.svg             # Content type icon
```

## Development Guidelines

### H5P Best Practices

1. Use Existing Content Types When Possible
   - Explore the H5P Hub before creating custom content
   - Common types: Interactive Video, Course Presentation, Question Set, Branching Scenario

2. Custom Development
   - Follow H5P coding standards and API conventions
   - Ensure proper event dispatching for xAPI tracking
   - Implement responsive design (mobile-first approach)
   - Test across browsers (Chrome, Firefox, Safari, Edge)

3. Accessibility (WCAG 2.1 AA)
   - Include proper ARIA labels
   - Ensure keyboard navigation
   - Provide text alternatives for multimedia
   - Maintain sufficient color contrast

4. Moodle Integration
   - Test content in Moodle environment before deployment
   - Verify gradebook integration for assessments
   - Check xAPI statement logging
   - Ensure proper content packaging (.h5p files)

### File Naming Conventions

- Use kebab-case for directories and files
- JavaScript: meaningful-name.js
- CSS: meaningful-name.css
- JSON: library.json, semantics.json, etc.

### Code Style

- JavaScript: ES6+ features, clear variable names, JSDoc comments
- CSS: BEM methodology or similar, mobile-first media queries
- JSON: Properly formatted with 2-space indentation

## Common H5P Content Types to Build On

- Interactive Video: Video with embedded quizzes and interactions
- Course Presentation: Slide-based content with multimedia
- Question Set: Series of questions for assessment
- Drag and Drop: Interactive matching exercises
- Fill in the Blanks: Cloze activities
- Timeline: Interactive timelines
- Image Hotspots: Clickable image areas with popups
- Branching Scenario: Choose-your-own-adventure style learning

## xAPI Integration

When creating assessments, ensure proper xAPI statements are sent:
- attempted: User started the activity
- answered: User submitted a response
- completed: User finished the activity
- scored: Activity includes a gradeable score

## Testing Checklist

Before deploying to Moodle:
- [ ] Content displays correctly in local test environment or Moodle preview
- [ ] All interactions work as expected
- [ ] Mobile responsiveness verified
- [ ] Accessibility tested (keyboard, screen reader)
- [ ] xAPI events fire correctly
- [ ] Scores report to gradebook (if applicable)
- [ ] Content exports/imports as .h5p file
- [ ] Multi-language support (if needed)

## Packaging Sanity Checks

- Confirm required files exist: h5p.json and content/content.json
- Ensure each library folder contains a library.json
- Ensure the archive root is correct (no extra top-level folder)
- Check that h5p.json lists all libraries used by content
- Verify no missing media assets referenced by content.json

## Lightweight Automated Checks

PowerShell (Windows):

```powershell
# From the package root (where h5p.json lives)
$required = @("h5p.json", "content\content.json")
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) { Write-Error "Missing: $($missing -join ', ')"; exit 1 }

$libraryJson = Get-ChildItem -Directory | ForEach-Object { Join-Path $_.FullName "library.json" } | Where-Object { Test-Path $_ }
if (-not $libraryJson) { Write-Error "No library.json files found"; exit 1 }

Get-Content "h5p.json" -Raw | ConvertFrom-Json | Out-Null
Get-Content "content\content.json" -Raw | ConvertFrom-Json | Out-Null
Write-Host "Basic H5P package checks passed"
```

macOS/Linux:

```bash
# From the package root (where h5p.json lives)
test -f h5p.json && test -f content/content.json || { echo "Missing required files"; exit 1; }
find . -maxdepth 2 -name library.json | grep -q . || { echo "No library.json files found"; exit 1; }
python - <<'PY'
import json
json.load(open('h5p.json'))
json.load(open('content/content.json'))
print('Basic H5P package checks passed')
PY
```

## Dependency Preflight Check

Validate that every dependency listed in h5p.json exists as a folder in the package root.

PowerShell (Windows):

```powershell
# From the package root (where h5p.json lives)
$h5p = Get-Content "h5p.json" -Raw | ConvertFrom-Json
$deps = $h5p.preloadedDependencies | ForEach-Object { "$($_.machineName)-$($_.majorVersion).$($_.minorVersion)" }
$missing = $deps | Where-Object { -not (Test-Path $_) }
if ($missing) { Write-Error "Missing dependency folders: $($missing -join ', ')"; exit 1 }
Write-Host "Dependency preflight passed"
```

macOS/Linux:

```bash
# From the package root (where h5p.json lives)
python - <<'PY'
import json, os, sys
deps = []
data = json.load(open('h5p.json'))
for d in data.get('preloadedDependencies', []):
   deps.append(f"{d['machineName']}-{d['majorVersion']}.{d['minorVersion']}")
missing = [d for d in deps if not os.path.isdir(d)]
if missing:
   print("Missing dependency folders: " + ", ".join(missing))
   sys.exit(1)
print("Dependency preflight passed")
PY
```

## Library Metadata Check

Confirm each dependency folder contains a library.json file.

PowerShell (Windows):

```powershell
# From the package root (where h5p.json lives)
$h5p = Get-Content "h5p.json" -Raw | ConvertFrom-Json
$deps = $h5p.preloadedDependencies | ForEach-Object { "$($_.machineName)-$($_.majorVersion).$($_.minorVersion)" }
$missing = @()
foreach ($dep in $deps) {
   $libraryJson = Join-Path $dep "library.json"
   if (-not (Test-Path $libraryJson)) { $missing += $libraryJson }
}
if ($missing) { Write-Error "Missing library.json: $($missing -join ', ')"; exit 1 }
Write-Host "Library metadata check passed"
```

macOS/Linux:

```bash
# From the package root (where h5p.json lives)
python - <<'PY'
import json, os, sys
data = json.load(open('h5p.json'))
deps = [f"{d['machineName']}-{d['majorVersion']}.{d['minorVersion']}" for d in data.get('preloadedDependencies', [])]
missing = [os.path.join(d, 'library.json') for d in deps if not os.path.isfile(os.path.join(d, 'library.json'))]
if missing:
      print("Missing library.json: " + ", ".join(missing))
      sys.exit(1)
print("Library metadata check passed")
PY
```

## Content Asset Reference Check

Validate that file paths referenced in content/content.json exist on disk.

PowerShell (Windows):

```powershell
# From the package root (where h5p.json lives)
function Get-PathsFromJson($obj) {
   if ($null -eq $obj) { return @() }
   if ($obj -is [System.Collections.IDictionary]) {
      $paths = @()
      foreach ($key in $obj.Keys) {
         if ($key -in @('path','file')) {
            if ($obj[$key] -is [string]) { $paths += $obj[$key] }
         }
         $paths += Get-PathsFromJson $obj[$key]
      }
      return $paths
   }
   if ($obj -is [System.Collections.IEnumerable] -and -not ($obj -is [string])) {
      $paths = @()
      foreach ($item in $obj) { $paths += Get-PathsFromJson $item }
      return $paths
   }
   return @()
}

$content = Get-Content "content\content.json" -Raw | ConvertFrom-Json
$paths = Get-PathsFromJson $content | Sort-Object -Unique
$missing = $paths | Where-Object { -not (Test-Path (Join-Path "content" $_)) }
if ($missing) { Write-Error "Missing content assets: $($missing -join ', ')"; exit 1 }
Write-Host "Content asset reference check passed"
```

macOS/Linux:

```bash
# From the package root (where h5p.json lives)
python - <<'PY'
import json, os, sys
def walk(obj):
      if isinstance(obj, dict):
            for k, v in obj.items():
                  if k in ('path','file') and isinstance(v, str):
                        yield v
                  yield from walk(v)
      elif isinstance(obj, list):
            for item in obj:
                  yield from walk(item)

data = json.load(open('content/content.json'))
paths = sorted(set(walk(data)))
missing = [p for p in paths if not os.path.exists(os.path.join('content', p))]
if missing:
      print("Missing content assets: " + ", ".join(missing))
      sys.exit(1)
print("Content asset reference check passed")
PY
```

## One-Command Preflight

Run all checks in sequence from the package root.

PowerShell (Windows):

```powershell
# From the package root (where h5p.json lives)
$ErrorActionPreference = "Stop"

# Basic structure and JSON validity
$required = @("h5p.json", "content\content.json")
$missing = $required | Where-Object { -not (Test-Path $_) }
if ($missing) { Write-Error "Missing: $($missing -join ', ')"; exit 1 }

$libraryJson = Get-ChildItem -Directory | ForEach-Object { Join-Path $_.FullName "library.json" } | Where-Object { Test-Path $_ }
if (-not $libraryJson) { Write-Error "No library.json files found"; exit 1 }

Get-Content "h5p.json" -Raw | ConvertFrom-Json | Out-Null
Get-Content "content\content.json" -Raw | ConvertFrom-Json | Out-Null

# Dependency folders exist
$h5p = Get-Content "h5p.json" -Raw | ConvertFrom-Json
$deps = $h5p.preloadedDependencies | ForEach-Object { "$($_.machineName)-$($_.majorVersion).$($_.minorVersion)" }
$missing = $deps | Where-Object { -not (Test-Path $_) }
if ($missing) { Write-Error "Missing dependency folders: $($missing -join ', ')"; exit 1 }

# Dependency library.json files exist
$missing = @()
foreach ($dep in $deps) {
   $libraryJson = Join-Path $dep "library.json"
   if (-not (Test-Path $libraryJson)) { $missing += $libraryJson }
}
if ($missing) { Write-Error "Missing library.json: $($missing -join ', ')"; exit 1 }

# Content asset references exist
function Get-PathsFromJson($obj) {
   if ($null -eq $obj) { return @() }
   if ($obj -is [System.Collections.IDictionary]) {
      $paths = @()
      foreach ($key in $obj.Keys) {
         if ($key -in @('path','file')) {
            if ($obj[$key] -is [string]) { $paths += $obj[$key] }
         }
         $paths += Get-PathsFromJson $obj[$key]
      }
      return $paths
   }
   if ($obj -is [System.Collections.IEnumerable] -and -not ($obj -is [string])) {
      $paths = @()
      foreach ($item in $obj) { $paths += Get-PathsFromJson $item }
      return $paths
   }
   return @()
}

$content = Get-Content "content\content.json" -Raw | ConvertFrom-Json
$paths = Get-PathsFromJson $content | Sort-Object -Unique
$missing = $paths | Where-Object { -not (Test-Path (Join-Path "content" $_)) }
if ($missing) { Write-Error "Missing content assets: $($missing -join ', ')"; exit 1 }

Write-Host "All H5P preflight checks passed"
```

macOS/Linux:

```bash
# From the package root (where h5p.json lives)
python - <<'PY'
import json, os, sys

def fail(msg):
      print(msg)
      sys.exit(1)

if not os.path.isfile('h5p.json') or not os.path.isfile('content/content.json'):
      fail('Missing required files: h5p.json and/or content/content.json')

if not any(os.path.isfile(os.path.join(d, 'library.json')) for d in os.listdir('.') if os.path.isdir(d)):
      fail('No library.json files found')

with open('h5p.json') as f:
      h5p = json.load(f)
with open('content/content.json') as f:
      content = json.load(f)

deps = [f"{d['machineName']}-{d['majorVersion']}.{d['minorVersion']}" for d in h5p.get('preloadedDependencies', [])]
missing_deps = [d for d in deps if not os.path.isdir(d)]
if missing_deps:
      fail('Missing dependency folders: ' + ', '.join(missing_deps))

missing_libs = [os.path.join(d, 'library.json') for d in deps if not os.path.isfile(os.path.join(d, 'library.json'))]
if missing_libs:
      fail('Missing library.json: ' + ', '.join(missing_libs))

def walk(obj):
      if isinstance(obj, dict):
            for k, v in obj.items():
                  if k in ('path','file') and isinstance(v, str):
                        yield v
                  yield from walk(v)
      elif isinstance(obj, list):
            for item in obj:
                  yield from walk(item)

paths = sorted(set(walk(content)))
missing_assets = [p for p in paths if not os.path.exists(os.path.join('content', p))]
if missing_assets:
      fail('Missing content assets: ' + ', '.join(missing_assets))

print('All H5P preflight checks passed')
PY
```

## Deployment Process

1. Package Content: Build a .h5p archive (zip with .h5p extension)
    - Ensure the package root contains h5p.json and content/content.json
    - Include each library folder at the root (e.g., H5P.DragQuestion-1.13/)
    - Do not wrap the package contents in an extra top-level folder
    - Create the archive:
       - Windows (PowerShell): `Compress-Archive -Path .\* -DestinationPath .\my-content.h5p`
       - macOS/Linux: `zip -r my-content.h5p .`
2. Test in Staging: Upload to test Moodle instance
3. Student Testing: Have sample users test functionality
4. Production Deploy: Upload to production Moodle
5. Monitor: Check analytics and student feedback

## Resources

- H5P Documentation: https://h5p.org/documentation
- H5P Core API: https://h5p.org/documentation/api/H5P.html
- Moodle H5P Documentation: https://docs.moodle.org/en/H5P
- xAPI Specification: https://github.com/adlnet/xAPI-Spec
- H5P GitHub Repository: https://github.com/h5p

## Project-Specific Notes

### Content Categories
Organize content by subject area or type:
- assessments/ - Graded activities
- practice/ - Non-graded exercises
- presentations/ - Lecture content
- simulations/ - Interactive simulations

### Branding
- Follow institutional branding guidelines
- Use consistent color scheme across content
- Include appropriate logos/attribution

### Performance Considerations
- Optimize images and media files
- Minimize external dependencies
- Keep bundle sizes reasonable for student bandwidth

## Support and Troubleshooting

Common issues:
- Content not displaying: Check Moodle H5P plugin version compatibility
- Scores not recording: Verify xAPI configuration in Moodle
- Mobile issues: Test responsive breakpoints
- Slow loading: Optimize asset sizes

## Contributing

When adding new content types or experiments:
1. Create a descriptive directory name
2. Include a README.md explaining the content purpose
3. Document any custom parameters or configurations
4. Note Moodle version compatibility

---

Last Updated: February 5, 2026
Moodle Version: 4.5
H5P Plugin Version: 1.20+ (H5P Core API 1.23)
````
