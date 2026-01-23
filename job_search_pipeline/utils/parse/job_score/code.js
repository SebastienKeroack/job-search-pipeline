//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const IS_TEST = globalThis?.__TEST__ === true;

const common = require('/home/runner/job-search-pipeline/job_search_pipeline/utils/parse/common.js').default;

let input_json = $input.first().json;

const content = common.extractInputText(input_json);

const effectiveContent = typeof content === 'string' && content.trim() ? content : common.getDefaultTemplate('job_score-prompt');

// Strip Markdown code fences if the model returned ```json ... ```
let cleaned = common.stripCodeFences(effectiveContent);

// Normalize various dash characters and HTML entities to ASCII hyphen-minus
cleaned = common.normalizeDashes(cleaned);

// Parse
let json = common.parseFirstJsonOrDefault(cleaned, 'job_score-prompt', IS_TEST);
json.score = common.clampScore(json.score ?? 0, 0, 10);

json.raw = effectiveContent;
return [{ json: json }];
