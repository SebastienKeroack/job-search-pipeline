//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const common = require('/home/runner/job-search-pipeline/job_search_pipeline/utils/parse/common.js').default;

let input_json = $input.first().json;

const content = common.extractInputText(input_json);

const effectiveContent = typeof content === 'string' && content.trim() ? content : common.getDefaultTemplate('compatibility_score-prompt');

// Strip Markdown code fences if the model returned ```json ... ```
let cleaned = common.stripCodeFences(effectiveContent);

// Parse
let json = common.parseFirstJsonOrDefault(cleaned, 'job_level-prompt');

json.raw = effectiveContent;
return [{ json: json }];
