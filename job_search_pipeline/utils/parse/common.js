// Common parsing utilities for parsers in this workspace
const common = (() => {
  'use strict';

  function extractFirstJsonValue(text) {
    const s = String(text ?? '').trim();

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

  function stripCodeFences(s) {
    return String(s ?? '')
      .trim()
      .replace(/^```(?:json)?\s*/i, '')
      .replace(/\s*```$/i, '');
  }

  function normalizeDashes(s) {
    // Normalize various dash characters and HTML entities to ASCII hyphen-minus
    // Covers: en-dash (U+2013), em-dash (U+2014), figure dash, non-breaking hyphen,
    // and common HTML entities like &ndash;, &mdash;, &#8211;, &#8212;.
    return String(s ?? '').replace(/&ndash;|&mdash;|&#8211;|&#8212;|\u2013|\u2014|\u2012|\u2011|\u2010/g, '-');
  }

  function extractInputText(input_json) {
    // Mirrors previous extraction logic used across parsers.
    if (Array.isArray(input_json.choices) && typeof input_json.choices[0]?.message?.content === 'string') {
      return input_json.choices[0].message.content;
    }

    if (Array.isArray(input_json.output) && typeof input_json.output[1]?.content?.[0]?.text === 'string') {
      return input_json.output[1].content[0].text;
    }

    if (typeof input_json.content === 'string') {
      return input_json.content;
    }

    throw new Error('Input JSON does not contain expected fields.');
  }

  function getDefaultTemplate(promptName) {
    try {
      const template = $(promptName).first().json?.default;
      if (typeof template === 'string' && template.trim()) return template;
    } catch (e) {
      // fallthrough to throw below
    }
    throw new Error(`Default template not found at $(${promptName}).first().json.default`);
  }

  // clamp a numeric score to [vmin, vmax], return 'N/A' for non-numeric input
  function clampScore(val, vmin, vmax) {
    const num = Number(val);
    if (isNaN(num)) return 'N/A';
    return Math.max(vmin, Math.min(vmax, num));
  }

  // canonical level map for fast lookups
  const LEVEL_MAP = Object.freeze(Object.assign(Object.create(null), {
    intern: 0,
    entry: 1,
    junior: 2,
    mid: 3,
    senior: 4,
    executive: 5,
  }));

  function levelToRank(level, map = LEVEL_MAP) {
    if (typeof level !== 'string') return -1;
    const key = level.trim().toLowerCase();
    const v = map[key];
    return v === undefined ? -1 : v;
  }

  function levelAtMost(level, target, map = LEVEL_MAP) {
    const rank = levelToRank(level, map);
    const targetRank = levelToRank(target, map);
    if (rank === -1 || targetRank === -1) return false;
    return rank <= targetRank;
  }

  function parseFirstJsonOrDefault(cleaned, promptName) {
    try {
      const firstJson = extractFirstJsonValue(cleaned);
      return JSON.parse(firstJson);
    } catch (err) {
      if (globalThis?.__TEST__ === true) {
        throw new Error(`Invalid JSON in message.content: ${err.message}\nRaw content:\n${cleaned}`);
      }
      return JSON.parse(getDefaultTemplate(promptName));
    }
  }

  return {
    extractFirstJsonValue,
    stripCodeFences,
    normalizeDashes,
    extractInputText,
    getDefaultTemplate,
    clampScore,
    LEVEL_MAP,
    levelToRank,
    levelAtMost,
    parseFirstJsonOrDefault,
  };
})();

export default common;
