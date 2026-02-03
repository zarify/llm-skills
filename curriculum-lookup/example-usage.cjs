#!/usr/bin/env node

/**
 * Example usage of curriculum-helper as a module
 * Demonstrates how to integrate curriculum lookups in lesson planning workflows
 */

const {
    searchContent,
    getDescriptorDetails,
    getContentDescriptorsByYear,
    getCapabilityIndicators,
} = require('./curriculum-helper.cjs');

console.log('=== Australian Curriculum Lookup Examples ===\n');

// Example 1: Search for privacy-related content in Year 7-8
console.log('1. Searching for "privacy" in Year 7 Technologies:');
const privacyResults = searchContent('Technologies.jsonld', 'privacy', 'Year 7');
privacyResults.forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description.substring(0, 80)}...`);
});

console.log('\n2. Getting full details for AC9TDI8P09 (privacy descriptor):');
const privacyDescriptor = getDescriptorDetails('Technologies.jsonld', 'AC9TDI8P09');
if (privacyDescriptor) {
    console.log(`   Code: ${privacyDescriptor.code}`);
    console.log(`   Description: ${privacyDescriptor.description}`);
    console.log(`   Year Levels: ${privacyDescriptor.yearLevels.join(', ')}`);
    console.log(`   Elaborations: ${privacyDescriptor.elaborationCount}`);
    privacyDescriptor.elaborations.forEach((elab, index) => {
        console.log(`   ${index + 1}. ${elab.description.substring(0, 100)}...`);
    });
}

console.log('\n3. Listing all Digital Technologies content descriptors for Year 7:');
const year7Descriptors = getContentDescriptorsByYear('Technologies.jsonld', 'Year 7');
console.log(`   Found ${year7Descriptors.length} content descriptors`);
const dtDescriptors = year7Descriptors.filter(d => d.code.startsWith('AC9TDI'));
console.log(`   ${dtDescriptors.length} are Digital Technologies (AC9TDI*)`);
dtDescriptors.slice(0, 5).forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description.substring(0, 70)}...`);
});

console.log('\n4. Digital Literacy capability indicators for Year 7-8:');
const dlIndicators = getCapabilityIndicators('Digital-literacy.jsonld', 'Year 7');
console.log(`   Found ${dlIndicators.length} indicators`);
dlIndicators.slice(0, 3).forEach(ind => {
    console.log(`   - ${ind.code}: ${ind.description.substring(0, 70)}...`);
});

console.log('\n5. Finding binary-related content:');
const binaryResults = searchContent('Technologies.jsonld', 'binary', ['Year 7', 'Year 8']);
console.log(`   Found ${binaryResults.length} result(s)`);
binaryResults.forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description}`);
    const details = getDescriptorDetails('Technologies.jsonld', desc.code);
    console.log(`     Has ${details.elaborationCount} elaboration(s)`);
});

console.log('\n=== Lesson Planning Use Case ===');
console.log('For a lesson on "Digital Footprints and Privacy" for Year 7-8:');
const lessonDescriptors = searchContent('Technologies.jsonld', 'digital footprint');
if (lessonDescriptors.length === 0) {
    console.log('Searching more broadly for privacy...');
    const broadSearch = searchContent('Technologies.jsonld', 'privacy', 'Year 7');
    broadSearch.forEach(desc => {
        console.log(`\nContent Descriptor: ${desc.code}`);
        console.log(`Description: ${desc.description}`);
        const details = getDescriptorDetails('Technologies.jsonld', desc.code);
        console.log(`\nElaborations to address:`);
        details.elaborations.forEach((elab, i) => {
            console.log(`${i + 1}. ${elab.description}`);
        });
    });
}

console.log('\n\nRelevant Digital Literacy indicators:');
const privacyIndicators = getCapabilityIndicators('Digital-literacy.jsonld', 'Year 7')
    .filter(ind =>
        ind.description.toLowerCase().includes('privacy') ||
        ind.description.toLowerCase().includes('data') ||
        ind.description.toLowerCase().includes('consent')
    );
privacyIndicators.forEach(ind => {
    console.log(`- ${ind.code}: ${ind.description}`);
});
