#!/usr/bin/env node

/**
 * Example usage of the WA SCSA Curriculum Helper
 * 
 * This file demonstrates common use cases for querying
 * the Western Australian Digital Technologies curriculum.
 */

const helper = require('./wa-curriculum-helper.cjs');

console.log('='.repeat(60));
console.log('WA SCSA Digital Technologies Curriculum - Example Usage');
console.log('='.repeat(60));
console.log();

// Example 1: Get a specific descriptor by code
console.log('Example 1: Get descriptor by code (WA7DIGDR1)');
console.log('-'.repeat(60));
const descriptor = helper.getDescriptorByCode('WA7DIGDR1');
if (descriptor) {
    console.log('Code:', descriptor.code);
    console.log('Description:', descriptor.description);
    console.log('Strand:', descriptor.strand);
    console.log('Year Level:', descriptor.yearLevel);
    console.log('Capabilities:', descriptor.capabilities?.join(', ') || 'None');
    console.log('Elaborations:', descriptor.elaborations?.length || 0);
    if (descriptor.elaborations && descriptor.elaborations.length > 0) {
        console.log('\nFirst elaboration:');
        console.log(' -', descriptor.elaborations[0]);
    }
}
console.log();

// Example 2: List all codes for a year level
console.log('Example 2: List all codes for Year 7');
console.log('-'.repeat(60));
const year7Codes = helper.listCodesByYear('Year 7');
console.log(`Found ${year7Codes.length} codes:`);
year7Codes.forEach((code, i) => {
    if (i < 5) {
        console.log(` - ${code}`);
    }
});
if (year7Codes.length > 5) {
    console.log(` ... and ${year7Codes.length - 5} more`);
}
console.log();

// Example 3: Search for content
console.log('Example 3: Search for "binary" content');
console.log('-'.repeat(60));
const searchResults = helper.searchContent('binary');
console.log(`Found ${searchResults.length} matching descriptors:`);
searchResults.forEach((result, i) => {
    if (i < 3) {
        console.log(`\n${result.code} (${result.yearLevel})`);
        console.log(`  ${result.description}`);
    }
});
if (searchResults.length > 3) {
    console.log(`\n... and ${searchResults.length - 3} more results`);
}
console.log();

// Example 4: Get strand content
console.log('Example 4: Get Digital systems strand for Year 7');
console.log('-'.repeat(60));
const strandContent = helper.getStrandContent('Year 7', 'Digital systems');
console.log(`Found ${strandContent.length} descriptors in strand:`);
strandContent.forEach(item => {
    console.log(`\n${item.code}:`);
    console.log(`  ${item.description}`);
    if (item.elaborations) {
        console.log(`  Elaborations: ${item.elaborations.length}`);
    }
});
console.log();

// Example 5: Get by capability
console.log('Example 5: Find Year 7 Numeracy-linked descriptors');
console.log('-'.repeat(60));
const numeracyDescriptors = helper.getByCapability('Numeracy', 'Year 7');
console.log(`Found ${numeracyDescriptors.length} descriptors with Numeracy:`);
numeracyDescriptors.forEach((desc, i) => {
    if (i < 3) {
        console.log(` - ${desc.code}: ${desc.description.substring(0, 60)}...`);
    }
});
if (numeracyDescriptors.length > 3) {
    console.log(` ... and ${numeracyDescriptors.length - 3} more`);
}
console.log();

// Example 6: Get achievement standard
console.log('Example 6: Year 7 Achievement Standard');
console.log('-'.repeat(60));
const achievementStd = helper.getAchievementStandard('Year 7');
console.log(achievementStd.substring(0, 200) + '...');
console.log();

// Example 7: Get all descriptors for a year
console.log('Example 7: Get all Year 10 descriptors');
console.log('-'.repeat(60));
const year10Descriptors = helper.getContentDescriptorsByYear('Year 10');
console.log(`Found ${year10Descriptors.length} total descriptors`);

// Count by strand
const strandCounts = {};
year10Descriptors.forEach(desc => {
    const strand = desc.subsection || desc.strand;
    strandCounts[strand] = (strandCounts[strand] || 0) + 1;
});

console.log('\nBreakdown by strand:');
Object.entries(strandCounts).forEach(([strand, count]) => {
    console.log(` - ${strand}: ${count}`);
});
console.log();

console.log('='.repeat(60));
console.log('For more examples, see SKILL.md');
console.log('='.repeat(60));
