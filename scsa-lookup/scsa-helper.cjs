#!/usr/bin/env node
'use strict';

const path = require('path');
const Database = require('better-sqlite3');

const DB_PATH = path.join(__dirname, 'scsa.db');

function openDb() {
  return new Database(DB_PATH, { readonly: true });
}

/** Add prefix matching to FTS search terms so "algorithm" matches "algorithms" etc. */
function ftsQuery(term) {
  // Split into words and add prefix wildcard to each
  return term.trim().split(/\s+/).map(w => `"${w}"*`).join(' ');
}

function normalizeYear(input) {
  if (!input) return null;
  const s = input.toUpperCase().trim();
  if (/^(PP|Y\d{1,2})$/.test(s)) return s;
  if (/^\d{1,2}$/.test(s)) return `Y${s}`;
  if (s === 'PRE-PRIMARY' || s === 'PREPRIMARY') return 'PP';
  return s;
}

function normalizeArea(input) {
  return input ? input.toLowerCase().trim() : null;
}

function output(command, params, results, notes) {
  const obj = { command, params, results: Array.isArray(results) ? results : [results], count: Array.isArray(results) ? results.length : 1 };
  if (notes) obj.notes = notes;
  console.log(JSON.stringify(obj, null, 2));
}

function parseFlags(args) {
  const flags = {};
  let i = 0;
  while (i < args.length) {
    if (args[i].startsWith('--') && i + 1 < args.length) {
      flags[args[i].slice(2)] = args[i + 1];
      i += 2;
    } else {
      i++;
    }
  }
  return flags;
}

function extractPositionalAndFlags(args) {
  const positional = [];
  const flags = {};
  let i = 0;
  while (i < args.length) {
    if (args[i].startsWith('--') && i + 1 < args.length) {
      flags[args[i].slice(2)] = args[i + 1];
      i += 2;
    } else {
      positional.push(args[i]);
      i++;
    }
  }
  return { positional, flags };
}

function annotateImageContext(row) {
  if (row && row.has_generated_context && row.image_context) {
    return { ...row, image_context: `[AI-GENERATED CONTEXT] ${row.image_context}` };
  }
  return row;
}

// --- Commands ---

function listAreas(db) {
  const rows = db.prepare('SELECT id, name, category, parent_id, implementation_year, implementation_status FROM learning_areas ORDER BY category, name').all();
  output('list-areas', {}, rows);
}

function search(db, args) {
  const { positional, flags } = extractPositionalAndFlags(args);
  const term = positional.join(' ');
  if (!term) { console.error('Usage: search <term> [--year <yl>] [--area <area>]'); process.exit(1); }

  const year = normalizeYear(flags.year);
  const area = normalizeArea(flags.area);

  let sql = `SELECT cd.id, cd.learning_area_id, cd.year_level_id, cd.strand, cd.sub_strand,
    cd.content_description, cd.elaborations, cd.has_generated_context, cd.image_context,
    cd.is_mandated, cd.source_document,
    rank
    FROM content_fts fts
    JOIN content_descriptors cd ON cd.rowid = fts.rowid
    WHERE content_fts MATCH ?`;
  const params = [ftsQuery(term)];

  if (year) { sql += ' AND cd.year_level_id = ?'; params.push(year); }
  if (area) { sql += ' AND cd.learning_area_id = ?'; params.push(area); }
  sql += ' ORDER BY rank';

  const rows = db.prepare(sql).all(...params).map(annotateImageContext);
  output('search', { term, year, area }, rows);
}

function searchAll(db, args) {
  const { positional, flags } = extractPositionalAndFlags(args);
  const term = positional.join(' ');
  if (!term) { console.error('Usage: search-all <term> [--year <yl>]'); process.exit(1); }

  const year = normalizeYear(flags.year);

  const fts = ftsQuery(term);

  // Content descriptors
  let contentSql = `SELECT cd.id, cd.learning_area_id, cd.year_level_id, cd.strand, cd.sub_strand,
    cd.content_description, cd.elaborations, cd.has_generated_context, cd.image_context,
    cd.source_document, rank
    FROM content_fts fts
    JOIN content_descriptors cd ON cd.rowid = fts.rowid
    WHERE content_fts MATCH ?`;
  const contentParams = [fts];
  if (year) { contentSql += ' AND cd.year_level_id = ?'; contentParams.push(year); }
  contentSql += ' ORDER BY rank';
  const contentRows = db.prepare(contentSql).all(...contentParams).map(annotateImageContext);

  // Achievement standards
  let achSql = `SELECT a.id, a.learning_area_id, a.year_level_id, a.standard_text, a.source_document, rank
    FROM achievement_fts fts
    JOIN achievement_standards a ON a.rowid = fts.rowid
    WHERE achievement_fts MATCH ?`;
  const achParams = [fts];
  if (year) { achSql += ' AND a.year_level_id = ?'; achParams.push(year); }
  achSql += ' ORDER BY rank';
  const achRows = db.prepare(achSql).all(...achParams);

  // Glossary
  let glossSql = `SELECT g.id, g.learning_area_id, g.term, g.definition, g.source_document, rank
    FROM glossary_fts fts
    JOIN glossary_terms g ON g.rowid = fts.rowid
    WHERE glossary_fts MATCH ?`;
  const glossParams = [fts];
  glossSql += ' ORDER BY rank';
  const glossRows = db.prepare(glossSql).all(...glossParams);

  const results = {
    content_descriptors: contentRows,
    achievement_standards: achRows,
    glossary_terms: glossRows
  };
  const totalCount = contentRows.length + achRows.length + glossRows.length;
  output('search-all', { term, year }, results, `Found ${contentRows.length} content descriptors, ${achRows.length} achievement standards, ${glossRows.length} glossary terms`);
}

function getContent(db, args) {
  const { positional } = extractPositionalAndFlags(args);
  if (positional.length < 2) { console.error('Usage: get-content <area> <year>'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const year = normalizeYear(positional[1]);

  const rows = db.prepare(`SELECT id, learning_area_id, year_level_id, strand, sub_strand,
    content_description, elaborations, has_generated_context, image_context, image_context_source,
    is_mandated, source_document
    FROM content_descriptors
    WHERE learning_area_id = ? AND year_level_id = ?
    ORDER BY strand, sub_strand, id`).all(area, year).map(annotateImageContext);

  // Group by strand
  const grouped = {};
  for (const row of rows) {
    const key = row.strand || '(no strand)';
    if (!grouped[key]) grouped[key] = [];
    grouped[key].push(row);
  }

  output('get-content', { area, year }, rows, `${rows.length} descriptors across ${Object.keys(grouped).length} strands: ${Object.keys(grouped).join(', ')}`);
}

function getAchievement(db, args) {
  const { positional } = extractPositionalAndFlags(args);
  if (positional.length < 2) { console.error('Usage: get-achievement <area> <year>'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const year = normalizeYear(positional[1]);

  const rows = db.prepare(`SELECT id, learning_area_id, year_level_id, standard_text, source_document
    FROM achievement_standards WHERE learning_area_id = ? AND year_level_id = ?`).all(area, year);
  output('get-achievement', { area, year }, rows);
}

function getDescription(db, args) {
  const { positional } = extractPositionalAndFlags(args);
  if (positional.length < 2) { console.error('Usage: get-description <area> <year>'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const year = normalizeYear(positional[1]);

  const rows = db.prepare(`SELECT id, learning_area_id, year_level_id, description_text, source_document
    FROM year_level_descriptions WHERE learning_area_id = ? AND year_level_id = ?`).all(area, year);
  output('get-description', { area, year }, rows);
}

function getCapability(db, args) {
  const { positional, flags } = extractPositionalAndFlags(args);
  if (positional.length < 1) { console.error('Usage: get-capability <capability> [--year <yl>]'); process.exit(1); }
  const capability = normalizeArea(positional[0]);
  const year = normalizeYear(flags.year);

  // Get capability info
  const cap = db.prepare('SELECT * FROM general_capabilities WHERE id = ?').get(capability);

  let sql = `SELECT ci.id, ci.element_id, ci.year_level_id, ci.level_name, ci.indicator_text,
    ce.capability_id, ce.element_name, ce.sub_element_name, ce.description as element_description
    FROM capability_indicators ci
    JOIN capability_elements ce ON ci.element_id = ce.id
    WHERE ce.capability_id = ?`;
  const params = [capability];
  if (year) { sql += ' AND ci.year_level_id = ?'; params.push(year); }
  sql += ' ORDER BY ce.element_name, ci.year_level_id, ci.id';

  const rows = db.prepare(sql).all(...params);
  const result = { capability: cap, indicators: rows };
  output('get-capability', { capability, year }, rows, cap ? `Capability: ${cap.name} — ${rows.length} indicators` : `No capability found for '${capability}'`);
}

function getJudging(db, args) {
  const { positional } = extractPositionalAndFlags(args);
  if (positional.length < 2) { console.error('Usage: get-judging <area> <year>'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const year = normalizeYear(positional[1]);

  const rows = db.prepare(`SELECT id, learning_area_id, year_level_id, strand, grade, descriptor_text, source_document, is_best_effort
    FROM judging_standards WHERE learning_area_id = ? AND year_level_id = ?
    ORDER BY strand, CASE grade WHEN 'A' THEN 1 WHEN 'B' THEN 2 WHEN 'C' THEN 3 WHEN 'D' THEN 4 WHEN 'E' THEN 5 ELSE 6 END`).all(area, year);

  const hasBestEffort = rows.some(r => r.is_best_effort);
  const notes = hasBestEffort ? 'Based on older syllabus documentation; may not align perfectly with current curriculum' : undefined;
  output('get-judging', { area, year }, rows, notes);
}

function getGlossary(db, args) {
  const { positional, flags } = extractPositionalAndFlags(args);
  if (positional.length < 1) { console.error('Usage: get-glossary <area> [--term <term>]'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const termFilter = flags.term;

  let sql = 'SELECT id, learning_area_id, term, definition, source_document FROM glossary_terms WHERE learning_area_id = ?';
  const params = [area];
  if (termFilter) {
    sql += ' AND term LIKE ?';
    params.push(`%${termFilter}%`);
  }
  sql += ' ORDER BY term';

  const rows = db.prepare(sql).all(...params);
  output('get-glossary', { area, term: termFilter || null }, rows);
}

function getPrinciples(db, args) {
  const { flags } = extractPositionalAndFlags(args);
  const category = flags.category || null;

  let sql = 'SELECT id, category, principle_number, title, description, reflection_questions, guidance, source_document FROM principles';
  const params = [];
  if (category) { sql += ' WHERE category = ?'; params.push(category); }
  sql += ' ORDER BY category, principle_number';

  const rows = db.prepare(sql).all(...params).map(r => {
    if (r.reflection_questions) {
      try { r.reflection_questions = JSON.parse(r.reflection_questions); } catch (_) {}
    }
    return r;
  });
  output('get-principles', { category }, rows);
}

function getAblewa(db, args) {
  const { positional, flags } = extractPositionalAndFlags(args);
  if (positional.length < 1) { console.error('Usage: get-ablewa <area> [--level <level>]'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const level = flags.level || null;

  let sql = 'SELECT id, learning_area_id, level, strand, content_description, source_document FROM ablewa_content WHERE learning_area_id = ?';
  const params = [area];
  if (level) { sql += ' AND level = ?'; params.push(level); }
  sql += ' ORDER BY level, strand, id';

  const rows = db.prepare(sql).all(...params);
  output('get-ablewa', { area, level }, rows);
}

function crossref(db, args) {
  const { positional } = extractPositionalAndFlags(args);
  if (positional.length < 2) { console.error('Usage: crossref <area> <year>'); process.exit(1); }
  const area = normalizeArea(positional[0]);
  const year = normalizeYear(positional[1]);

  const rows = db.prepare(`SELECT cr.id, cr.scsa_content_id, cr.acara_code, cr.acara_description, cr.match_type, cr.confidence, cr.notes,
    cd.strand, cd.sub_strand, cd.content_description AS scsa_description
    FROM acara_crossref cr
    JOIN content_descriptors cd ON cr.scsa_content_id = cd.id
    WHERE cd.learning_area_id = ? AND cd.year_level_id = ?
    ORDER BY cr.match_type, cr.confidence DESC`).all(area, year);
  output('crossref', { area, year }, rows, rows.length === 0 ? 'No cross-references found. This data may not yet be populated.' : undefined);
}

function stats(db) {
  const tables = [
    'learning_areas', 'year_levels', 'content_descriptors', 'achievement_standards',
    'year_level_descriptions', 'general_capabilities', 'capability_elements',
    'capability_indicators', 'glossary_terms', 'judging_standards', 'principles',
    'ablewa_content', 'acara_crossref'
  ];
  const results = {};
  for (const t of tables) {
    try {
      results[t] = db.prepare(`SELECT count(*) as count FROM ${t}`).get().count;
    } catch (_) {
      results[t] = 0;
    }
  }
  output('stats', {}, results, `Total records: ${Object.values(results).reduce((a, b) => a + b, 0)}`);
}

function showHelp() {
  console.log(`SCSA Curriculum Helper — Query the WA (SCSA) curriculum database

Usage: node scsa-helper.cjs <command> [args] [--flags]

Commands:
  list-areas                              List all learning areas with categories
  search <term> [--year <yl>] [--area <a>]  FTS search across content descriptors
  search-all <term> [--year <yl>]         Search across ALL tables (content, achievement, glossary)
  get-content <area> <year>               Get content descriptors for area+year (grouped by strand)
  get-achievement <area> <year>           Get achievement standard
  get-description <area> <year>           Get year level description
  get-capability <cap> [--year <yl>]      Get capability indicators
  get-judging <area> <year>               Get judging standards (A–E grades)
  get-glossary <area> [--term <term>]     Look up glossary terms
  get-principles [--category <cat>]       Get teaching/assessment principles
  get-ablewa <area> [--level <level>]     Get ABLEWA content
  crossref <area> <year>                  Show ACARA cross-references
  stats                                   Show database statistics
  help                                    Show this help message

Year levels: PP, Y1, Y2, ... Y10 (also accepts bare numbers: 7 → Y7)
Learning areas: english, mathematics, science, hass, hpe, tech-digital, tech-design,
  arts-dance, arts-drama, arts-media, arts-music, arts-visual, and more.
Capabilities: gc-critical-creative, gc-digital-literacy, gc-ethical,
  gc-intercultural, gc-literacy, gc-personal-social
Principle categories: assessment, teaching-and-learning

Output: JSON to stdout.`);
}

// --- Main ---
const args = process.argv.slice(2);
const command = args[0];
const rest = args.slice(1);

if (!command || command === 'help') {
  showHelp();
  process.exit(0);
}

const db = openDb();
try {
  switch (command) {
    case 'list-areas': listAreas(db); break;
    case 'search': search(db, rest); break;
    case 'search-all': searchAll(db, rest); break;
    case 'get-content': getContent(db, rest); break;
    case 'get-achievement': getAchievement(db, rest); break;
    case 'get-description': getDescription(db, rest); break;
    case 'get-capability': getCapability(db, rest); break;
    case 'get-judging': getJudging(db, rest); break;
    case 'get-glossary': getGlossary(db, rest); break;
    case 'get-principles': getPrinciples(db, rest); break;
    case 'get-ablewa': getAblewa(db, rest); break;
    case 'crossref': crossref(db, rest); break;
    case 'stats': stats(db); break;
    default:
      console.error(`Unknown command: ${command}`);
      showHelp();
      process.exit(1);
  }
} finally {
  db.close();
}
