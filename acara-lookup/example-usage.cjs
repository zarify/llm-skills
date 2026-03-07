#!/usr/bin/env node

/**
 * Example usage of curriculum-helper as a module
 * Demonstrates lookups across ALL Australian Curriculum learning areas,
 * general capabilities, and cross-curriculum priorities.
 */

const {
    searchContent,
    getDescriptorDetails,
    getContentDescriptorsByYear,
    getCapabilityIndicators,
    searchAll,
    listFiles,
    getPriorityOrganisingIdeas,
    CURRICULUM_FILES,
} = require('./curriculum-helper.cjs');

console.log('=== Australian Curriculum Lookup Examples ===\n');

// ---------- 1. List available curriculum files ----------
console.log('1. Available curriculum files:');
const filesByCategory = listFiles();
for (const [category, items] of Object.entries(filesByCategory)) {
    console.log(`   [${category}]`);
    items.forEach(f => {
        console.log(`     ${f.filename.padEnd(14)} ${f.name}`);
    });
}

// ---------- 2. Search Technologies for privacy (Year 5-6) ----------
console.log('\n2. Searching for "privacy" in Technologies:');
const privacyResults = searchContent('TEC.jsonld', 'privacy');
privacyResults.forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description.substring(0, 80)}...`);
});

// ---------- 3. Full descriptor details ----------
console.log('\n3. Getting full details for AC9TDI6P10 (privacy descriptor):');
const privacyDescriptor = getDescriptorDetails('TEC.jsonld', 'AC9TDI6P10');
if (privacyDescriptor) {
    console.log(`   Code: ${privacyDescriptor.code}`);
    console.log(`   Description: ${privacyDescriptor.description}`);
    console.log(`   Year Levels: ${privacyDescriptor.yearLevels.join(', ')}`);
    console.log(`   Elaborations: ${privacyDescriptor.elaborationCount}`);
    privacyDescriptor.elaborations.forEach((elab, index) => {
        console.log(`   ${index + 1}. ${elab.description.substring(0, 100)}...`);
    });
}

// ---------- 4. Content descriptors by year ----------
console.log('\n4. Digital Technologies content descriptors for Year 7:');
const year7Descriptors = getContentDescriptorsByYear('TEC.jsonld', 'Year 7');
console.log(`   Found ${year7Descriptors.length} content descriptors`);
const dtDescriptors = year7Descriptors.filter(d => d.code.startsWith('AC9TDI'));
console.log(`   ${dtDescriptors.length} are Digital Technologies (AC9TDI*)`);
dtDescriptors.slice(0, 5).forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description.substring(0, 70)}...`);
});

// ---------- 5. Digital Literacy capability indicators ----------
console.log('\n5. Digital Literacy capability indicators for Year 7-8:');
const dlIndicators = getCapabilityIndicators('DL.jsonld', 'Year 7');
console.log(`   Found ${dlIndicators.length} indicators`);
dlIndicators.slice(0, 3).forEach(ind => {
    console.log(`   - ${ind.code}: ${ind.description.substring(0, 70)}...`);
});

// ---------- 6. Binary search in Technologies ----------
console.log('\n6. Finding binary-related content in Technologies:');
const binaryResults = searchContent('TEC.jsonld', 'binary', ['Year 7', 'Year 8']);
console.log(`   Found ${binaryResults.length} result(s)`);
binaryResults.forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description}`);
    const details = getDescriptorDetails('TEC.jsonld', desc.code);
    console.log(`     Has ${details.elaborationCount} elaboration(s)`);
});

// ---------- 7. searchAll — cross-learning-area search ----------
console.log('\n7. Searching ALL learning area files for "energy" in Year 8:');
const energyResults = searchAll('energy', 'Year 8');
console.log(`   Found ${energyResults.length} result(s) across all files`);
energyResults.slice(0, 5).forEach(desc => {
    const label = CURRICULUM_FILES[desc.file]?.name || desc.file;
    console.log(`   [${label}] ${desc.code}: ${desc.description.substring(0, 60)}...`);
});

// ---------- 8. Search a non-Technologies learning area ----------
console.log('\n8. Searching Science for "chemical" in Year 8:');
const chemResults = searchContent('SCI.jsonld', 'chemical', 'Year 8');
console.log(`   Found ${chemResults.length} result(s)`);
chemResults.slice(0, 3).forEach(desc => {
    console.log(`   - ${desc.code}: ${desc.description.substring(0, 80)}...`);
});

// ---------- 9. Sustainability priority organising ideas ----------
console.log('\n9. Sustainability priority organising ideas:');
const sustainIdeas = getPriorityOrganisingIdeas('S.jsonld');
console.log(`   Found ${sustainIdeas.length} organising idea(s)`);
sustainIdeas.slice(0, 3).forEach(idea => {
    console.log(`   - ${idea.code}: ${idea.description.substring(0, 80)}...`);
});

// ---------- 10. Lesson planning use case ----------
console.log('\n=== Lesson Planning Use Case ===');
console.log('For a lesson on "Digital Footprints and Privacy" for Year 7-8:');
const lessonDescriptors = searchContent('TEC.jsonld', 'digital footprint');
if (lessonDescriptors.length === 0) {
    console.log('Searching more broadly for privacy...');
    const broadSearch = searchContent('TEC.jsonld', 'privacy', 'Year 7');
    broadSearch.forEach(desc => {
        console.log(`\nContent Descriptor: ${desc.code}`);
        console.log(`Description: ${desc.description}`);
        const details = getDescriptorDetails('TEC.jsonld', desc.code);
        console.log(`\nElaborations to address:`);
        details.elaborations.forEach((elab, i) => {
            console.log(`${i + 1}. ${elab.description}`);
        });
    });
}

console.log('\n\nRelevant Digital Literacy indicators:');
const privacyIndicators = getCapabilityIndicators('DL.jsonld', 'Year 7')
    .filter(ind =>
        ind.description.toLowerCase().includes('privacy') ||
        ind.description.toLowerCase().includes('data') ||
        ind.description.toLowerCase().includes('consent')
    );
privacyIndicators.forEach(ind => {
    console.log(`- ${ind.code}: ${ind.description}`);
});
