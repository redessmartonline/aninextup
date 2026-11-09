const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const script = fs.readFileSync(path.join(__dirname, '../assets/article-broadcasts.js'), 'utf8');
const broadcast = '2026-11-13T23:00:00+09:00';
const airTime = Date.parse('2026-11-13T14:00:00Z');
let now = airTime - 1;
let pending;
const row = {dataset: {broadcastAt: broadcast}, textContent: 'Listed Japanese broadcast'};
const past = {dataset: {broadcastAt: '2026-11-05T23:56:00+09:00'}};
const localTime = {dataset: {broadcastAt: '2026-11-13T23:00:00'}, textContent: 'Listed Japanese broadcast'};
vm.runInNewContext(script, {
  document: {querySelectorAll: () => [row, past, localTime]},
  Date: {parse: Date.parse, now: () => now},
  setTimeout: (callback, delay) => {
    assert.equal(delay, 1);
    pending = callback;
  },
});
assert.equal(row.textContent, 'Next listed Japanese broadcast');
assert.equal(past.textContent, 'Last listed Japanese broadcast');
assert.equal(localTime.textContent, 'Listed Japanese broadcast');
now = airTime;
pending();
assert.equal(row.textContent, 'Last listed Japanese broadcast');
console.log('PASS: scheduled, expired, exact-boundary and timezone-safe broadcast labels.');
