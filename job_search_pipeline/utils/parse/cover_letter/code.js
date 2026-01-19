//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const IS_TEST = globalThis?.__TEST__ === true;

let input_json = $input.first().json;
let input_text = '';

// Extraction for OpenAI, Ollama and Responses API outputs
if (
  Array.isArray(input_json.choices) &&
  typeof input_json.choices[0]?.message?.content === 'string'
) {
  input_text = input_json.choices[0].message.content;
} else if (
  Array.isArray(input_json.output) &&
  typeof input_json.output[1]?.content?.[0]?.text === 'string'
) {
  input_text = input_json.output[1].content[0].text;
} else if (typeof input_json.content === 'string') {
  input_text = input_json.content;
} else {
  throw new Error('Input JSON does not contain expected fields.');
}

const content = input_text;

function getDefaultTemplate() {
  try {
    const template = $('cover_letter-prompt').first().json?.default;
    if (typeof template === 'string' && template.trim()) return template;
  } catch (e) {
    // ignore and throw below
  }
  throw new Error("Default template not found at $('cover_letter-prompt').first().json.default");
}

const effectiveContent =
  typeof content === 'string' && content.trim() ? content : getDefaultTemplate();

// Strip Markdown code fences if the model returned ```json ... ```
const cleaned = effectiveContent
  .trim()
  .replace(/^```(?:json)?\s*/i, '')
  .replace(/\s*```$/i, '');

function extractFirstJsonValue(text) {
  const s = String(text ?? '').trim();

  // Find first opening bracket for an object or array.
  let start = -1;
  let open = '';
  let close = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (ch === '{') {
      start = i;
      open = '{';
      close = '}';
      break;
    }
    if (ch === '[') {
      start = i;
      open = '[';
      close = ']';
      break;
    }
  }

  if (start === -1) {
    throw new Error('No JSON object/array start found');
  }

  let depth = 0;
  let inString = false;
  let escaped = false;

  for (let i = start; i < s.length; i++) {
    const ch = s[i];

    if (escaped) {
      escaped = false;
      continue;
    }

    if (inString) {
      if (ch === '\\') {
        escaped = true;
      } else if (ch === '"') {
        inString = false;
      }
      continue;
    }

    if (ch === '"') {
      inString = true;
      continue;
    }

    if (ch === open) depth++;
    else if (ch === close) depth--;

    if (depth === 0) {
      return s.slice(start, i + 1);
    }
  }

  throw new Error('Could not find a complete JSON value');
}

// Parse
let json;
try {
  // Some small LLMs repeat themselves and output multiple JSON objects.
  // Parse only the first complete JSON value.
  const firstJson = extractFirstJsonValue(cleaned);
  json = JSON.parse(firstJson);
} catch (err) {
  if (IS_TEST) {
    // In tests we want failures to be visible.
    throw new Error(
      `Invalid JSON in message.content: ${err.message}\nRaw content:\n${effectiveContent}`,
    );
  }

  json = JSON.parse(getDefaultTemplate());
}

json.raw = effectiveContent;
return [{ json: json }];