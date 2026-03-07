#!/usr/bin/env node

/**
 * Australian Curriculum Helper
 * Extracts content descriptors and elaborations from ACARA curriculum JSONLD files
 */

const fs = require('fs');
const path = require('path');

// Curriculum file mapping: abbreviation → full name + category
const CURRICULUM_FILES = {
  // Learning Areas
  'TEC.jsonld':  { name: 'Technologies', category: 'learning-area' },
  'ENG.jsonld':  { name: 'English', category: 'learning-area' },
  'MAT.jsonld':  { name: 'Mathematics', category: 'learning-area' },
  'SCI.jsonld':  { name: 'Science', category: 'learning-area' },
  'HASS.jsonld': { name: 'Humanities and Social Sciences', category: 'learning-area' },
  'HPE.jsonld':  { name: 'Health and Physical Education', category: 'learning-area' },
  'ART.jsonld':  { name: 'The Arts', category: 'learning-area' },
  'LAN.jsonld':  { name: 'Languages', category: 'learning-area' },
  // General Capabilities
  'DL.jsonld':   { name: 'Digital Literacy', category: 'general-capability' },
  'CCT.jsonld':  { name: 'Critical and Creative Thinking', category: 'general-capability' },
  'EU.jsonld':   { name: 'Ethical Understanding', category: 'general-capability' },
  'IU.jsonld':   { name: 'Intercultural Understanding', category: 'general-capability' },
  'L.jsonld':    { name: 'Literacy', category: 'general-capability' },
  'N.jsonld':    { name: 'Numeracy', category: 'general-capability' },
  'PSC.jsonld':  { name: 'Personal and Social Capability', category: 'general-capability' },
  // Cross-Curriculum Priorities
  'AA.jsonld':    { name: 'Asia and Australia\'s Engagement with Asia', category: 'cross-curriculum-priority' },
  'A_TSI.jsonld': { name: 'Aboriginal and Torres Strait Islander Histories and Cultures', category: 'cross-curriculum-priority' },
  'S.jsonld':     { name: 'Sustainability', category: 'cross-curriculum-priority' },
};

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
 * @param {string} filename - The JSONLD file (e.g., 'TEC.jsonld')
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
 * @param {string} filename - The JSONLD file (e.g., 'TEC.jsonld')
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
 * @param {string} filename - The JSONLD file (e.g., 'TEC.jsonld')
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
 * @param {string} filename - The capability file (e.g., 'DL.jsonld')
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
 * List available curriculum files grouped by category
 * @returns {Object} Files grouped by category
 */
function listFiles() {
  const grouped = { 'learning-area': [], 'general-capability': [], 'cross-curriculum-priority': [] };
  for (const [filename, info] of Object.entries(CURRICULUM_FILES)) {
    grouped[info.category].push({ filename, name: info.name });
  }
  return grouped;
}

/**
 * Search for content matching keywords across all learning area files
 * @param {string} searchTerm - Search term to look for
 * @param {string|string[]} yearLevels - Optional year level filter
 * @returns {Array} Matching content descriptors tagged with source file
 */
function searchAll(searchTerm, yearLevels = null) {
  const results = [];
  for (const [filename, info] of Object.entries(CURRICULUM_FILES)) {
    if (info.category !== 'learning-area') continue;
    try {
      const matches = searchContent(filename, searchTerm, yearLevels);
      matches.forEach(match => {
        results.push({ ...match, file: filename, learningArea: info.name });
      });
    } catch (e) {
      // Skip files that fail to load
    }
  }
  return results;
}

/**
 * Get cross-curriculum priority organising ideas
 * @param {string} filename - The CCP file (e.g., 'AA.jsonld', 'A_TSI.jsonld', 'S.jsonld')
 * @returns {Array} Organising ideas with their details
 */
function getPriorityOrganisingIdeas(filename) {
  const graph = loadCurriculumFile(filename);

  const organisingIdeas = graph.filter(item => {
    const statementLabel = getValue(item, 'http://purl.org/ASN/schema/core/statementLabel');
    return statementLabel === 'Organising Idea';
  });

  return organisingIdeas.map(item => ({
    id: item['@id'],
    code: getValue(item, 'http://purl.org/ASN/schema/core/statementNotation'),
    description: getValue(item, 'http://purl.org/dc/terms/description'),
    title: getValue(item, 'http://purl.org/dc/terms/title'),
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
    case 'list-files':
      {
        const files = listFiles();
        console.log(JSON.stringify(files, null, 2));
      }
      break;

    case 'list-by-year':
      {
        const filename = args[1] || 'TEC.jsonld';
        const yearLevel = args[2] || 'Year 7';
        const descriptors = getContentDescriptorsByYear(filename, yearLevel);
        console.log(JSON.stringify(descriptors, null, 2));
      }
      break;
      
    case 'get-descriptor':
      {
        const filename = args[1] || 'TEC.jsonld';
        const code = args[2];
        if (!code) {
          console.error('Usage: curriculum-helper.cjs get-descriptor <filename> <code>');
          process.exit(1);
        }
        const details = getDescriptorDetails(filename, code);
        console.log(JSON.stringify(details, null, 2));
      }
      break;
      
    case 'search':
      {
        const filename = args[1] || 'TEC.jsonld';
        const searchTerm = args[2];
        const yearLevel = args[3] || null;
        if (!searchTerm) {
          console.error('Usage: curriculum-helper.cjs search <filename> <search-term> [year-level]');
          process.exit(1);
        }
        const results = searchContent(filename, searchTerm, yearLevel);
        console.log(JSON.stringify(results, null, 2));
      }
      break;

    case 'search-all':
      {
        const searchTerm = args[1];
        const yearLevel = args[2] || null;
        if (!searchTerm) {
          console.error('Usage: curriculum-helper.cjs search-all <search-term> [year-level]');
          process.exit(1);
        }
        const results = searchAll(searchTerm, yearLevel);
        console.log(JSON.stringify(results, null, 2));
      }
      break;
      
    case 'capability-indicators':
      {
        const filename = args[1] || 'DL.jsonld';
        const yearLevel = args[2] || 'Year 7';
        const indicators = getCapabilityIndicators(filename, yearLevel);
        console.log(JSON.stringify(indicators, null, 2));
      }
      break;

    case 'get-priorities':
      {
        const filename = args[1];
        if (!filename) {
          console.error('Usage: curriculum-helper.cjs get-priorities <filename>');
          console.error('Files: AA.jsonld, A_TSI.jsonld, S.jsonld');
          process.exit(1);
        }
        const ideas = getPriorityOrganisingIdeas(filename);
        console.log(JSON.stringify(ideas, null, 2));
      }
      break;
      
    default:
      console.log(`
Australian Curriculum Helper

Usage:
  curriculum-helper.cjs list-files
    List all available curriculum files grouped by category

  curriculum-helper.cjs list-by-year [filename] [year-level]
    List all content descriptors for a year level
    Example: curriculum-helper.cjs list-by-year TEC.jsonld "Year 7"
  
  curriculum-helper.cjs get-descriptor [filename] <code>
    Get full details of a content descriptor including elaborations
    Example: curriculum-helper.cjs get-descriptor TEC.jsonld AC9TDI8K04
  
  curriculum-helper.cjs search [filename] <search-term> [year-level]
    Search for content descriptors matching keywords in a specific file
    Example: curriculum-helper.cjs search SCI.jsonld "energy" "Year 8"
  
  curriculum-helper.cjs search-all <search-term> [year-level]
    Search across ALL learning area files for matching content descriptors
    Example: curriculum-helper.cjs search-all "algorithm" "Year 7"
  
  curriculum-helper.cjs capability-indicators [filename] [year-level]
    Get general capability indicators for a year level
    Example: curriculum-helper.cjs capability-indicators DL.jsonld "Year 7"

  curriculum-helper.cjs get-priorities <filename>
    Get cross-curriculum priority organising ideas
    Example: curriculum-helper.cjs get-priorities S.jsonld

Learning Area files:    TEC, ENG, MAT, SCI, HASS, HPE, ART, LAN
Capability files:       DL, CCT, EU, IU, L, N, PSC
Priority files:         AA, A_TSI, S
(All filenames end with .jsonld)
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
  searchAll,
  listFiles,
  getPriorityOrganisingIdeas,
  loadCurriculumFile,
  getValue,
  getValues,
  getYearLevels,
  SCHOOL_LEVELS,
  CURRICULUM_FILES,
};
