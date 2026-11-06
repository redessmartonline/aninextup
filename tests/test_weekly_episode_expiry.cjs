const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const script = fs.readFileSync(require.resolve('../assets/weekly-episodes-ui.js'), 'utf8');
const data = {
  sourceUrl: 'https://www.crunchyroll.com/pt-br/simulcastcalendar',
  validFrom: '2026-10-26',
  validThrough: '2026-11-01',
  timezone: 'America/Sao_Paulo',
  regions: ['Brazil'],
  episodes: [{date: '2026-11-01', title: 'Example anime', times: ['13:00']}],
};

function render(at, overrides = {}) {
  const root = {dataset: {}};
  const source = {};
  const select = {value: '0', parentElement: {}, addEventListener() {}};
  const nodes = {
    '[data-weekly-episodes-week]': root,
    '[data-weekly-episode-source]': source,
    '[data-episode-region]': select,
  };
  class FixedDate extends Date {
    constructor(...args) {
      super(...(args.length ? args : [at]));
    }
  }
  vm.runInNewContext(script, {
    window: {ANINEXTUP_WEEKLY_EPISODES: {...data, ...overrides}},
    document: {querySelector: selector => nodes[selector]},
    Date: FixedDate,
  });
  return {root, source, select};
}

const active = render('2026-11-02T02:59:59Z');
assert.equal(active.root.dataset.scheduleState, 'verified');
assert.match(active.root.innerHTML, /Example anime/);
assert.equal(active.source.hidden, false);

for (const at of ['2026-11-02T03:00:00Z', '2026-11-06T12:00:00Z']) {
  const expired = render(at);
  assert.equal(expired.root.dataset.scheduleState, 'awaiting-verification');
  assert.match(expired.root.innerHTML, /awaiting verification/);
  assert.match(expired.root.innerHTML, /simulcastcalendar\?date=2026-11-02/);
  assert.doesNotMatch(expired.root.innerHTML, /Example anime|October/);
  assert.equal(expired.source.hidden, true);
  assert.equal(expired.source.innerHTML, '');
  assert.equal(expired.select.parentElement.hidden, true);
}

const incomplete = render('2026-11-06T12:00:00Z', {
  validFrom: '2026-11-05', validThrough: '2026-11-08',
});
assert.equal(incomplete.root.dataset.scheduleState, 'awaiting-verification');
console.log('Weekly episode coverage and expiry passed.');
