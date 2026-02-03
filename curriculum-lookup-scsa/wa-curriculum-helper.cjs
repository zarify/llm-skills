#!/usr/bin/env node

/**
 * Western Australian Curriculum Helper
 * Extracts content descriptors and elaborations from WA SCSA curriculum JSON file
 */

const fs = require('fs');
const path = require('path');

/**
 * Load and parse the WA curriculum JSON file
 */
function loadCurriculumFile(filename = 'digital-technologies.json') {
    const filePath = path.join(__dirname, 'curriculum', filename);
    const content = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(content);
}

/**
 * Get all content descriptors for a year level
 * @param {string} yearLevel - Year level (e.g., 'Year 7', 'Pre-primary')
 * @returns {Array} Content descriptors with their details
 */
function getContentDescriptorsByYear(yearLevel) {
    const curriculum = loadCurriculumFile();
    const yearData = curriculum.years[yearLevel];

    if (!yearData || !yearData.strands) {
        return [];
    }

    const descriptors = [];

    for (const [strandName, items] of Object.entries(yearData.strands)) {
        if (Array.isArray(items)) {
            // Regular strand
            items.forEach(item => {
                if (typeof item === 'object') {
                    descriptors.push({
                        ...item,
                        strand: strandName,
                        yearLevel: yearLevel
                    });
                }
            });
        } else if (typeof items === 'object') {
            // Design thinking skills with subsections
            for (const [subsection, subitems] of Object.entries(items)) {
                if (Array.isArray(subitems)) {
                    subitems.forEach(item => {
                        if (typeof item === 'object') {
                            descriptors.push({
                                ...item,
                                strand: strandName,
                                subsection: subsection,
                                yearLevel: yearLevel
                            });
                        }
                    });
                }
            }
        }
    }

    return descriptors;
}

/**
 * Get full details of a content descriptor by code
 * @param {string} code - The code of the content descriptor (e.g., 'WA7DIGDR1')
 * @returns {Object|null} Full descriptor details
 */
function getDescriptorByCode(code) {
    const curriculum = loadCurriculumFile();

    for (const [yearLevel, yearData] of Object.entries(curriculum.years)) {
        if (!yearData.strands) continue;

        for (const [strandName, items] of Object.entries(yearData.strands)) {
            if (Array.isArray(items)) {
                const found = items.find(item => item.code === code);
                if (found) {
                    return {
                        ...found,
                        strand: strandName,
                        yearLevel: yearLevel
                    };
                }
            } else if (typeof items === 'object') {
                // Design thinking skills
                for (const [subsection, subitems] of Object.entries(items)) {
                    if (Array.isArray(subitems)) {
                        const found = subitems.find(item => item.code === code);
                        if (found) {
                            return {
                                ...found,
                                strand: strandName,
                                subsection: subsection,
                                yearLevel: yearLevel
                            };
                        }
                    }
                }
            }
        }
    }

    return null;
}

/**
 * Get content for a specific strand
 * @param {string} yearLevel - Year level (e.g., 'Year 7')
 * @param {string} strandName - Strand name (e.g., 'Digital systems')
 * @returns {Array} Content descriptors for the strand
 */
function getStrandContent(yearLevel, strandName) {
    const curriculum = loadCurriculumFile();
    const yearData = curriculum.years[yearLevel];

    if (!yearData || !yearData.strands || !yearData.strands[strandName]) {
        return [];
    }

    const items = yearData.strands[strandName];
    const descriptors = [];

    if (Array.isArray(items)) {
        items.forEach(item => {
            if (typeof item === 'object') {
                descriptors.push({
                    ...item,
                    strand: strandName,
                    yearLevel: yearLevel
                });
            }
        });
    } else if (typeof items === 'object') {
        // Design thinking skills with subsections
        for (const [subsection, subitems] of Object.entries(items)) {
            if (Array.isArray(subitems)) {
                subitems.forEach(item => {
                    if (typeof item === 'object') {
                        descriptors.push({
                            ...item,
                            strand: strandName,
                            subsection: subsection,
                            yearLevel: yearLevel
                        });
                    }
                });
            }
        }
    }

    return descriptors;
}

/**
 * Get achievement standard for a year level
 * @param {string} yearLevel - Year level (e.g., 'Year 7')
 * @returns {string} Achievement standard
 */
function getAchievementStandard(yearLevel) {
    const curriculum = loadCurriculumFile();
    const yearData = curriculum.years[yearLevel];

    return yearData?.achievement_standard || '';
}

/**
 * Search for content matching keywords
 * @param {string} searchTerm - Search term to look for in descriptions and elaborations
 * @param {string|null} yearLevel - Optional year level filter
 * @returns {Array} Matching content descriptors
 */
function searchContent(searchTerm, yearLevel = null) {
    const curriculum = loadCurriculumFile();
    const searchLower = searchTerm.toLowerCase();
    const results = [];

    const yearsToSearch = yearLevel
        ? [yearLevel]
        : Object.keys(curriculum.years);

    for (const year of yearsToSearch) {
        const descriptors = getContentDescriptorsByYear(year);

        for (const descriptor of descriptors) {
            const descMatch = descriptor.description?.toLowerCase().includes(searchLower);
            const elabMatch = descriptor.elaborations?.some(elab =>
                elab.toLowerCase().includes(searchLower)
            );

            if (descMatch || elabMatch) {
                results.push(descriptor);
            }
        }
    }

    return results;
}

/**
 * List all curriculum codes for a year level
 * @param {string} yearLevel - Year level (e.g., 'Year 7')
 * @returns {Array} Array of codes
 */
function listCodesByYear(yearLevel) {
    const descriptors = getContentDescriptorsByYear(yearLevel);
    return descriptors.map(d => d.code).filter(Boolean);
}

/**
 * Get all descriptors with a specific capability
 * @param {string} capability - Capability name (e.g., 'Digital literacy')
 * @param {string|null} yearLevel - Optional year level filter
 * @returns {Array} Matching content descriptors
 */
function getByCapability(capability, yearLevel = null) {
    const curriculum = loadCurriculumFile();
    const results = [];

    const yearsToSearch = yearLevel
        ? [yearLevel]
        : Object.keys(curriculum.years);

    for (const year of yearsToSearch) {
        const descriptors = getContentDescriptorsByYear(year);

        for (const descriptor of descriptors) {
            if (descriptor.capabilities?.includes(capability)) {
                results.push(descriptor);
            }
        }
    }

    return results;
}

// CLI interface
if (require.main === module) {
    const args = process.argv.slice(2);
    const command = args[0];

    switch (command) {
        case 'list-by-year':
            {
                const yearLevel = args[1] || 'Year 7';
                const descriptors = getContentDescriptorsByYear(yearLevel);
                console.log(JSON.stringify(descriptors, null, 2));
            }
            break;

        case 'get-descriptor':
            {
                const code = args[1];
                if (!code) {
                    console.error('Usage: wa-curriculum-helper.cjs get-descriptor <code>');
                    process.exit(1);
                }
                const details = getDescriptorByCode(code);
                if (details) {
                    console.log(JSON.stringify(details, null, 2));
                } else {
                    console.error(`Descriptor not found: ${code}`);
                    process.exit(1);
                }
            }
            break;

        case 'get-strand':
            {
                const yearLevel = args[1] || 'Year 7';
                const strandName = args[2] || 'Digital systems';
                const content = getStrandContent(yearLevel, strandName);
                console.log(JSON.stringify(content, null, 2));
            }
            break;

        case 'achievement-standard':
            {
                const yearLevel = args[1] || 'Year 7';
                const standard = getAchievementStandard(yearLevel);
                console.log(standard);
            }
            break;

        case 'search':
            {
                const searchTerm = args[1];
                const yearLevel = args[2] || null;
                if (!searchTerm) {
                    console.error('Usage: wa-curriculum-helper.cjs search <search-term> [year-level]');
                    process.exit(1);
                }
                const results = searchContent(searchTerm, yearLevel);
                console.log(JSON.stringify(results, null, 2));
            }
            break;

        case 'list-codes':
            {
                const yearLevel = args[1] || 'Year 7';
                const codes = listCodesByYear(yearLevel);
                console.log(JSON.stringify(codes, null, 2));
            }
            break;

        case 'by-capability':
            {
                const capability = args[1];
                const yearLevel = args[2] || null;
                if (!capability) {
                    console.error('Usage: wa-curriculum-helper.cjs by-capability <capability> [year-level]');
                    process.exit(1);
                }
                const results = getByCapability(capability, yearLevel);
                console.log(JSON.stringify(results, null, 2));
            }
            break;

        default:
            console.log(`
Western Australian Curriculum Helper (SCSA Digital Technologies)

Usage:
  wa-curriculum-helper.cjs list-by-year [year-level]
    List all content descriptors for a year level
    Example: wa-curriculum-helper.cjs list-by-year "Year 7"
  
  wa-curriculum-helper.cjs get-descriptor <code>
    Get full details of a content descriptor including elaborations
    Example: wa-curriculum-helper.cjs get-descriptor WA7DIGDR1
  
  wa-curriculum-helper.cjs get-strand [year-level] [strand-name]
    Get all content for a specific strand
    Example: wa-curriculum-helper.cjs get-strand "Year 7" "Digital systems"
  
  wa-curriculum-helper.cjs achievement-standard [year-level]
    Get the achievement standard for a year level
    Example: wa-curriculum-helper.cjs achievement-standard "Year 7"
  
  wa-curriculum-helper.cjs search <search-term> [year-level]
    Search for content descriptors matching keywords
    Example: wa-curriculum-helper.cjs search "binary" "Year 7"
  
  wa-curriculum-helper.cjs list-codes [year-level]
    List all curriculum codes for a year level
    Example: wa-curriculum-helper.cjs list-codes "Year 7"
  
  wa-curriculum-helper.cjs by-capability <capability> [year-level]
    Find descriptors by capability (e.g., "Digital literacy")
    Example: wa-curriculum-helper.cjs by-capability "Numeracy" "Year 7"

Available year levels:
  - Pre-primary
  - Year 1 through Year 10

Available capabilities:
  - Digital literacy
  - Numeracy
  - Critical and creative thinking
  - Personal and social capability
  - Ethical understanding
  - Literacy
`);
    }
}

// Export functions for use as a module
module.exports = {
    getContentDescriptorsByYear,
    getDescriptorByCode,
    getStrandContent,
    getAchievementStandard,
    searchContent,
    listCodesByYear,
    getByCapability,
    loadCurriculumFile,
};
