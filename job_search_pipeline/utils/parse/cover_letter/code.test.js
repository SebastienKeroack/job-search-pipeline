//                                MIT License
//                     Copyright 2026, Sébastien Kéroack
// =============================================================================

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function runCodeNodeScript({ content, defaultTemplate = '{"cover_letter":"N/A"}' }) {
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
    if (nodeName !== 'cover_letter-prompt') {
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
      raw: '{"a":1,"b":"x"}',
    },
  });
});

test('uses default template when content is missing/empty', () => {
  const result = runCodeNodeScript({ content: '' });
  assert.equal(result.length, 1);
  assert.equal(typeof result[0].json, 'object');
  assert.equal(result[0].json.cover_letter, 'N/A');
  assert.equal(result[0].json.raw, '{"cover_letter":"N/A"}');
});

test('strips ```json code fences before parsing', () => {
  const content = '```json\n{"a":1}\n```';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), { a: 1, raw: content });
});

test('parses the first JSON object if multiple are present', () => {
  const content = '{"a":1}{"b":2}';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), { a: 1, raw: content });
});

test('parses JSON with blank lines/whitespace around keys and braces', () => {
  const content = '{\n\n"x":"y"\n\n}';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), { x: 'y', raw: content });
});

test('parses JSON with leading/trailing whitespace and newlines', () => {
  const content = '\n  {\n\n"x":"y"\n\n}  \n';
  const result = runCodeNodeScript({ content });
  assert.ok(Array.isArray(result));
  assert.equal(result.length, 1);
  assert.deepEqual(toPlainJson(result[0].json), { x: 'y', raw: content });
});

test('parses the first JSON object even with ``` fences and trailing ELSE text', () => {
  const content =
    '```{"total_score":5,"breakdown":{"skill_match":3,"compensation":1,"benefits":1,"employment_type":0},"reasoning":"\\\\n\\\\n"}}}} ELSE {"total_score":0} ```';
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
  assert.equal(parsed.reasoning, "\\n\\n");
  assert.equal(parsed.raw, content);
});
