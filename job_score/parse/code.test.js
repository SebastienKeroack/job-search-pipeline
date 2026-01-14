//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function runCodeNodeScript({ content, defaultTemplate = '{"total_score":0,"breakdown":{"skill_match":0,"compensation":0,"benefits":0,"employment_type":0},"short_reason":"N/A"}' }) {
  const codePath = path.resolve(__dirname, 'code.js');
  const code = fs.readFileSync(codePath, 'utf8');

  // Minimal n8n-like $input mock.
  const $input = {
    first() {
      return {
        json: {
          choices: [{ message: { content } }],
        },
      };
    },
  };

  // Minimal $() mock for n8n expression access.
  const $ = (nodeName) => {
    if (nodeName !== 'job_score-prompt') {
      throw new Error(`Unexpected node requested: ${nodeName}`);
    }
    return {
      first() {
        return { json: { default: defaultTemplate } };
      },
    };
  };

  const context = {
    $input,
    $,
    console,
    __TEST__: true,
  };

  // Wrap the Code node script so top-level `return ...` is valid.
  const wrapped = `"use strict";\n(function(){\n${code}\n})()`;

  try {
    return vm.runInNewContext(wrapped, context, { filename: codePath });
  } catch (err) {
    // Normalize to a plain Error with message for easier assertions.
    throw err;
  }
}

function toPlainJson(value) {
  return JSON.parse(JSON.stringify(value));
}

test('throws on invalid JSON', () => {
  assert.throws(
    () => runCodeNodeScript({ content: '{"a":1,}' }),
    /Invalid JSON in message\.content:/,
  );
});

test('parses a single JSON object string', () => {
  const result = runCodeNodeScript({ content: '{"a":1,"b":"x"}' });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0]), {
    json: {
      a: 1,
      b: 'x',
      total_score: 0,
      breakdown: { skill_match: 0, compensation: 0, benefits: 0, employment_type: 0 },
      raw: '{"a":1,"b":"x"}',
    },
  });
});

test('uses default template when content is missing/empty', () => {
  const result = runCodeNodeScript({ content: '' });
  assert.equal(result.length, 1);
  assert.equal(typeof result[0].json, 'object');
  assert.equal(result[0].json.total_score, 0);
  assert.equal(result[0].json.breakdown.skill_match, 0);
  assert.equal(result[0].json.breakdown.compensation, 0);
  assert.equal(result[0].json.breakdown.benefits, 0);
  assert.equal(result[0].json.breakdown.employment_type, 0);
  assert.equal(result[0].json.short_reason, "N/A");
});

test('strips ```json code fences before parsing', () => {
  const content = '```json\n{"a":1}\n```';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), {
    a: 1,
    total_score: 0,
    breakdown: { skill_match: 0, compensation: 0, benefits: 0, employment_type: 0 },
    raw: content,
  });
});

test('parses the first JSON object if multiple are present', () => {
  const content = '{"a":1}{"b":2}';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), {
    a: 1,
    total_score: 0,
    breakdown: { skill_match: 0, compensation: 0, benefits: 0, employment_type: 0 },
    raw: content,
  });
});

test('parses JSON with blank lines/whitespace around keys and braces', () => {
  const content = '{\n\n"x":1\n\n}';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), {
    x: 1,
    total_score: 0,
    breakdown: { skill_match: 0, compensation: 0, benefits: 0, employment_type: 0 },
    raw: content,
  });
});

test('parses JSON with leading/trailing whitespace and newlines', () => {
  const content = '\n  {\n\n"x":2\n\n}  \n';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), {
    x: 2,
    total_score: 0,
    breakdown: { skill_match: 0, compensation: 0, benefits: 0, employment_type: 0 },
    raw: content,
  });
});

test('clamps total_score and breakdown fields to allowed ranges', () => {
  const content = JSON.stringify({
    total_score: 42,
    breakdown: {
      skill_match: 99,
      compensation: -5,
      benefits: 2,
      employment_type: -1,
    },
    short_reason: 'test',
  });
  const result = runCodeNodeScript({ content });
  const parsed = toPlainJson(result[0].json);
  assert.equal(parsed.total_score, 10);
  assert.equal(parsed.breakdown.skill_match, 6);
  assert.equal(parsed.breakdown.compensation, 0);
  assert.equal(parsed.breakdown.benefits, 2);
  assert.equal(parsed.breakdown.employment_type, 0);
});

test('clamps fields and returns N/A for non-numeric total_score', () => {
  const content = JSON.stringify({
    total_score: 'not_a_number',
    breakdown: {
      skill_match: '7',
      compensation: '2',
      benefits: '1',
      employment_type: '1',
    },
    short_reason: 'test',
  });
  const result = runCodeNodeScript({ content });
  const parsed = toPlainJson(result[0].json);
  assert.equal(parsed.total_score, 'N/A');
  assert.equal(parsed.breakdown.skill_match, 6);
  assert.equal(parsed.breakdown.compensation, 1);
  assert.equal(parsed.breakdown.benefits, 1);
  assert.equal(parsed.breakdown.employment_type, 1);
});

test('parses the first JSON object even with ``` fences and trailing ELSE text', () => {
  const content =
    '```{"total_score":5,"breakdown":{"skill_match":3,"compensation":1,"benefits":1,"employment_type":0},"short_reason":"\\\\n\\\\n"}}}} ELSE {"total_score":0} ```';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);

  const parsed = toPlainJson(result[0].json);
  assert.equal(parsed.total_score, 5);
  assert.deepEqual(parsed.breakdown, {
    skill_match: 3,
    compensation: 1,
    benefits: 1,
    employment_type: 0,
  });
  assert.equal(parsed.short_reason, "\\n\\n");
});
