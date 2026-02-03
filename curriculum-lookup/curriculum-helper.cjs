#!/usr/bin/env node

/**
 * Australian Curriculum Helper
 * Extracts content descriptors and elaborations from ACARA curriculum JSONLD files
 */

const fs = require('fs');
const path = require('path');

// School level mapping
const SCHOOL_LEVELS = {
  'http://vocabulary.curriculum.edu.au/schoolLevel/0': 'Foundation',
  'http://vocabulary.curriculum.edu.au/schoolLevel/1': 'Year 1',
  'http://vocabulary.curriculum.edu.au/schoolLevel/2': 'Year 2',
  'http://vocabulary.curriculum.edu.au/schoolLevel/3': 'Year 3',
  'http://vocabulary.curriculum.edu.au/schoolLevel/4': 'Year 4',
  'http://vocabulary.curriculum.edu.au/schoolLevel/5': 'Year 5',
  'http://vocabulary.curriculum.edu.au/schoolLevel/6': 'Year 6',
  'http://vocabulary.curriculum.edu.au/schoolLevel/7': 'Year 7',
  'http://vocabulary.curriculum.edu.au/schoolLevel/8': 'Year 8',
  'http://vocabulary.curriculum.edu.au/schoolLevel/9': 'Year 9',
  'http://vocabulary.curriculum.edu.au/schoolLevel/10': 'Year 10',
};

/**
 * Load and parse a curriculum JSONLD file
 */
function loadCurriculumFile(filename) {
  const filePath = path.join(__dirname, 'curriculum', filename);
  const content = fs.readFileSync(filePath, 'utf8');
  const data = JSON.parse(content);
  return data[0]['@graph'];
}

/**
 * Get value from JSONLD property array
 */
function getValue(item, property, lang = 'en-au') {
  const prop = item[property];
  if (!prop || !Array.isArray(prop) || prop.length === 0) return null;
  
  const value = prop[0];
  if (value['@value']) return value['@value'];
  if (value['@id']) return value['@id'];
  return null;
}

/**
 * Get all values from JSONLD property array
 */
function getValues(item, property) {
  const prop = item[property];
  if (!prop || !Array.isArray(prop)) return [];
  
  return prop.map(value => {
    if (value['@value']) return value['@value'];
    if (value['@id']) return value['@id'];
    return null;
  }).filter(v => v !== null);
}

/**
 * Get year levels for an item
 */
function getYearLevels(item) {
  const levels = getValues(item, 'http://purl.org/dc/terms/educationLevel');
  return levels.map(levelId => SCHOOL_LEVELS[levelId] || levelId);
}

/**
 * Get content descriptors by year level from a learning area
 * @param {string} filename - The JSONLD file (e.g., 'Technologies.jsonld')
 * @param {string|string[]} yearLevels - Year level(s) to filter by (e.g., 'Year 7' or ['Year 7', 'Year 8'])
 * @returns {Array} Content descriptors with their details
 */
function getContentDescriptorsByYear(filename, yearLevels) {
  const graph = loadCurriculumFile(filename);
  const targetYears = Array.isArray(yearLevels) ? yearLevels : [yearLevels];
  
  // Find the school level IDs for target years
  const targetLevelIds = Object.entries(SCHOOL_LEVELS)
    .filter(([id, label]) => targetYears.includes(label))
    .map(([id]) => id);
  
  const contentDescriptors = graph.filter(item => {
    const statementLabel = getValue(item, 'http://purl.org/ASN/schema/core/statementLabel');
    if (statementLabel !== 'Content Description') return false;
    
    const itemLevels = getValues(item, 'http://purl.org/dc/terms/educationLevel');
    return itemLevels.some(level => targetLevelIds.includes(level));
  });
  
  return contentDescriptors.map(item => ({
    id: item['@id'],
    code: getValue(item, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(item, 'http://purl.org/dc/terms/description'),
    title: getValue(item, 'http://purl.org/dc/terms/title'),
    yearLevels: getYearLevels(item),
    elaborationIds: getValues(item, 'http://purl.org/gem/qualifiers/hasChild'),
    skillsEmbodied: getValues(item, 'http://purl.org/ASN/schema/core/skillEmbodied'),
    achievementLevels: getValues(item, 'http://purl.org/ASN/schema/core/hasLevel'),
  }));
}

/**
 * Get elaborations for a content descriptor
 * @param {string} filename - The JSONLD file (e.g., 'Technologies.jsonld')
 * @param {string} descriptorId - The ID or code of the content descriptor
 * @returns {Array} Elaborations for the descriptor
 */
function getElaborations(filename, descriptorId) {
  const graph = loadCurriculumFile(filename);
  
  // Find the content descriptor
  let descriptor = graph.find(item => 
    item['@id'] === descriptorId || 
    getValue(item, 'http://purl.org/ASN/schema/core/statementNotation') === descriptorId
  );
  
  if (!descriptor) {
    console.error(`Content descriptor not found: ${descriptorId}`);
    return [];
  }
  
  // Get child elaboration IDs
  const elaborationIds = getValues(descriptor, 'http://purl.org/gem/qualifiers/hasChild');
  
  // Find elaborations
  const elaborations = graph.filter(item => 
    elaborationIds.includes(item['@id']) &&
    getValue(item, 'http://purl.org/ASN/schema/core/statementLabel') === 'Elaboration'
  );
  
  return elaborations.map(item => ({
    id: item['@id'],
    code: getValue(item, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(item, 'http://purl.org/dc/terms/description'),
    title: getValue(item, 'http://purl.org/dc/terms/title'),
    yearLevels: getYearLevels(item),
    skillsEmbodied: getValues(item, 'http://purl.org/ASN/schema/core/skillEmbodied'),
  }));
}

/**
 * Get full details of a content descriptor including all elaborations
 * @param {string} filename - The JSONLD file (e.g., 'Technologies.jsonld')
 * @param {string} descriptorCode - The code of the content descriptor (e.g., 'AC9TDI8K04')
 * @returns {Object} Full descriptor details with elaborations
 */
function getDescriptorDetails(filename, descriptorCode) {
  const graph = loadCurriculumFile(filename);
  
  const descriptor = graph.find(item => 
    getValue(item, 'http://purl.org/ASN/schema/core/statementNotation') === descriptorCode &&
    getValue(item, 'http://purl.org/ASN/schema/core/statementLabel') === 'Content Description'
  );
  
  if (!descriptor) {
    return null;
  }
  
  const elaborations = getElaborations(filename, descriptor['@id']);
  
  return {
    code: getValue(descriptor, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(descriptor, 'http://purl.org/dc/terms/description'),
    title: getValue(descriptor, 'http://purl.org/dc/terms/title'),
    yearLevels: getYearLevels(descriptor),
    skillsEmbodied: getValues(descriptor, 'http://purl.org/ASN/schema/core/skillEmbodied'),
    achievementLevels: getValues(descriptor, 'http://purl.org/ASN/schema/core/hasLevel'),
    elaborations: elaborations,
    elaborationCount: elaborations.length,
  };
}

/**
 * Get cross-curricular capability indicators by level
 * @param {string} filename - The capability file (e.g., 'Digital-literacy.jsonld')
 * @param {string|string[]} yearLevels - Year level(s) to filter by
 * @returns {Array} Indicators for the level
 */
function getCapabilityIndicators(filename, yearLevels) {
  const graph = loadCurriculumFile(filename);
  const targetYears = Array.isArray(yearLevels) ? yearLevels : [yearLevels];
  
  // Find the school level IDs for target years
  const targetLevelIds = Object.entries(SCHOOL_LEVELS)
    .filter(([id, label]) => targetYears.includes(label))
    .map(([id]) => id);
  
  const indicators = graph.filter(item => {
    const statementLabel = getValue(item, 'http://purl.org/ASN/schema/core/statementLabel');
    if (statementLabel !== 'Indicator') return false;
    
    const itemLevels = getValues(item, 'http://purl.org/dc/terms/educationLevel');
    return itemLevels.some(level => targetLevelIds.includes(level));
  });
  
  return indicators.map(item => ({
    id: item['@id'],
    code: getValue(item, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(item, 'http://purl.org/dc/terms/description'),
    title: getValue(item, 'http://purl.org/dc/terms/title'),
    yearLevels: getYearLevels(item),
    proficiencyLevel: getValue(item, 'http://purl.org/ASN/schema/core/proficiencyLevel'),
  }));
}

/**
 * Search for content matching keywords
 * @param {string} filename - The JSONLD file
 * @param {string} searchTerm - Search term to look for in descriptions and titles
 * @param {string|string[]} yearLevels - Optional year level filter
 * @returns {Array} Matching content descriptors
 */
function searchContent(filename, searchTerm, yearLevels = null) {
  const graph = loadCurriculumFile(filename);
  const searchLower = searchTerm.toLowerCase();
  
  let targetLevelIds = null;
  if (yearLevels) {
    const targetYears = Array.isArray(yearLevels) ? yearLevels : [yearLevels];
    targetLevelIds = Object.entries(SCHOOL_LEVELS)
      .filter(([id, label]) => targetYears.includes(label))
      .map(([id]) => id);
  }
  
  const contentDescriptors = graph.filter(item => {
    const statementLabel = getValue(item, 'http://purl.org/ASN/schema/core/statementLabel');
    if (statementLabel !== 'Content Description') return false;
    
    if (targetLevelIds) {
      const itemLevels = getValues(item, 'http://purl.org/dc/terms/educationLevel');
      if (!itemLevels.some(level => targetLevelIds.includes(level))) return false;
    }
    
    const description = (getValue(item, 'http://purl.org/dc/terms/description') || '').toLowerCase();
    const title = (getValue(item, 'http://purl.org/dc/terms/title') || '').toLowerCase();
    
    return description.includes(searchLower) || title.includes(searchLower);
  });
  
  return contentDescriptors.map(item => ({
    code: getValue(item, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(item, 'http://purl.org/dc/terms/description'),
    title: getValue(item, 'http://purl.org/dc/terms/title'),
    yearLevels: getYearLevels(item),
  }));
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  switch (command) {
    case 'list-by-year':
      {
        const filename = args[1] || 'Technologies.jsonld';
        const yearLevel = args[2] || 'Year 7';
        const descriptors = getContentDescriptorsByYear(filename, yearLevel);
        console.log(JSON.stringify(descriptors, null, 2));
      }
      break;
      
    case 'get-descriptor':
      {
        const filename = args[1] || 'Technologies.jsonld';
        const code = args[2];
        if (!code) {
          console.error('Usage: curriculum-helper.js get-descriptor <filename> <code>');
          process.exit(1);
        }
        const details = getDescriptorDetails(filename, code);
        console.log(JSON.stringify(details, null, 2));
      }
      break;
      
    case 'search':
      {
        const filename = args[1] || 'Technologies.jsonld';
        const searchTerm = args[2];
        const yearLevel = args[3] || null;
        if (!searchTerm) {
          console.error('Usage: curriculum-helper.js search <filename> <search-term> [year-level]');
          process.exit(1);
        }
        const results = searchContent(filename, searchTerm, yearLevel);
        console.log(JSON.stringify(results, null, 2));
      }
      break;
      
    case 'capability-indicators':
      {
        const filename = args[1] || 'Digital-literacy.jsonld';
        const yearLevel = args[2] || 'Year 7';
        const indicators = getCapabilityIndicators(filename, yearLevel);
        console.log(JSON.stringify(indicators, null, 2));
      }
      break;
      
    default:
      console.log(`
Australian Curriculum Helper

Usage:
  curriculum-helper.js list-by-year [filename] [year-level]
    List all content descriptors for a year level
    Example: curriculum-helper.js list-by-year Technologies.jsonld "Year 7"
  
  curriculum-helper.js get-descriptor [filename] <code>
    Get full details of a content descriptor including elaborations
    Example: curriculum-helper.js get-descriptor Technologies.jsonld AC9TDI8K04
  
  curriculum-helper.js search [filename] <search-term> [year-level]
    Search for content descriptors matching keywords
    Example: curriculum-helper.js search Technologies.jsonld "binary" "Year 7"
  
  curriculum-helper.js capability-indicators [filename] [year-level]
    Get cross-curricular capability indicators for a year level
    Example: curriculum-helper.js capability-indicators Digital-literacy.jsonld "Year 7"

Available files:
  - Technologies.jsonld
  - Digital-literacy.jsonld
  - Critical-and-creative-thinking.jsonld
  - Ethical-understanding.jsonld
  - Intercultural-understanding.jsonld
  - Literacy.jsonld
  - Numeracy.jsonld
  - Personal-and-social-capability.jsonld
`);
  }
}

// Export functions for use as a module
module.exports = {
  getContentDescriptorsByYear,
  getElaborations,
  getDescriptorDetails,
  getCapabilityIndicators,
  searchContent,
  loadCurriculumFile,
  getValue,
  getValues,
  getYearLevels,
  SCHOOL_LEVELS,
};
