const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.join(__dirname, '..');
const loader = fs.readFileSync(path.join(root, 'scripts/google-ads-tag.js'), 'utf8').trim();
const marker = '<script type="text/plain" data-cookie-consent="targeting" data-aninextup-ads>';
const pages = ['', 'articles/'].flatMap(dir =>
  fs.readdirSync(path.join(root, dir)).filter(name => name.endsWith('.html')).map(name => dir + name));
for (const name of pages) {
  const html = fs.readFileSync(path.join(root, name), 'utf8');
  assert.equal(html.split('GTM-NL276DVG').length, 2, name);
  assert.ok(html.includes(marker + '\n' + loader + '\n</script>'), name);
  assert.equal(html.split('googletagmanager.com/gtag/js?id=G-TRV5CF738D').length, 2, name);
}

const tags = [];
const existingTag = function () {};
let onLoad;
let robots = 'index,follow';
const context = vm.createContext({
  window: {dataLayer: [{event: 'existing-event'}], gtag: existingTag},
  document: {
    getElementById: id => tags.find(tag => tag.id === id),
    querySelector: () => ({content: robots}),
    createElement: () => ({
      addEventListener(event, handler, options) {
        assert.equal(event, 'load');
        assert.equal(options.once, true);
        onLoad = handler;
      },
    }),
    head: {appendChild: tag => tags.push(tag)},
  },
});
vm.runInContext(loader, context);
vm.runInContext(loader, context);
assert.equal(tags.length, 1);
assert.equal(tags[0].src, 'https://www.googletagmanager.com/gtm.js?id=GTM-NL276DVG');
assert.equal(context.window.gtag, existingTag);
const [existing, defaults, update, start] = context.window.dataLayer;
assert.equal(existing.event, 'existing-event');
assert.deepEqual(Array.from(defaults).slice(0, 2), ['consent', 'default']);
assert.deepEqual(Array.from(update).slice(0, 2), ['consent', 'update']);
for (const key of ['ad_storage', 'ad_user_data', 'ad_personalization']) {
  assert.equal(defaults[2][key], 'denied');
  assert.equal(update[2][key], 'granted');
}
assert.equal(start.event, 'gtm.js');
assert.equal(context.window.dataLayer.length, 4);
assert.equal(typeof onLoad, 'function');
onLoad();
const conversion = Array.from(context.window.dataLayer.at(-1));
assert.equal(context.window.dataLayer.length, 5);
assert.deepEqual(conversion.slice(0, 2), ['event', 'conversion']);
assert.equal(conversion[2].send_to, 'AW-18543289744/bL0sCNDmh7UdEJDLkIpF');

robots = 'noindex';
onLoad = undefined;
tags.length = 0;
context.window.dataLayer.length = 0;
vm.runInContext(loader, context);
assert.equal(onLoad, undefined);
assert.equal(context.window.dataLayer.length, 3);
console.log('PASS: targeting consent, one post-load Ads conversion on public pages, no conversion on noindex pages, GA4 preserved.');
