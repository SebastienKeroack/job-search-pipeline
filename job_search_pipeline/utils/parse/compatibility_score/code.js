//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const common = require('/home/runner/job-search-pipeline/job_search_pipeline/utils/parse/common.js').default;

// Run Once for All Items
const job = $('loop-over-jobs1').first().json;
const llm = $input.first().json;

// Extract LLM Content
const content = common.extractInputText(llm);
const effectiveContent = (
  typeof content === 'string'
  && content.trim()
) ? content : common.getDefaultTemplate('compatibility_score-prompt');

// Preprocess content
// 1. Strip Markdown code fences if the model returned ```json ... ```
// 2. Normalize various dash characters and HTML entities to ASCII hyphen-minus
const cleanedContent = common.normalizeDashes(common.stripCodeFences(effectiveContent));

// Parse JSON content
let result = common.parseFirstJsonOrDefault(cleanedContent, 'compatibility_score-prompt');

// Clamp score between 0 and 18
result.score = common.clampScore(result.score ?? 0, 0, 18);

// Conditional Application Letter
result.application_letter = (
  result.score >= 13
  && common.levelToRank(job.level) <= common.LEVEL_MAP.mid
) ? 'TODO' : '-';

// Conditional Application Email
result.application_email = (
  result.application_letter === 'TODO'
  && typeof job.emails === 'string'
  && job.emails.trim()
) ? 'TODO' : '-';

// Return Result with Raw Content for Debugging when needed
result.raw = effectiveContent;
return [{ json: result }];
