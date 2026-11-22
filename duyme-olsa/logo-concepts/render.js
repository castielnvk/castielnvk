// Renders board.png (comparison board) and NN-*/preview.png (one row each) from board.html.
const {chromium} = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({deviceScaleFactor: 2, viewport: {width: 1800, height: 1000}});
  await p.goto('file://' + path.join(__dirname, 'board.html'));
  await p.waitForLoadState('networkidle');
  await p.screenshot({path: path.join(__dirname, 'board.png'), fullPage: true});
  const map = {c01: '01-button-wordmark', c02: '02-d-icon', c03: '03-the-tap', c04: '04-xala-butasi'};
  for (const [id, dir] of Object.entries(map))
    await p.locator('#' + id).screenshot({path: path.join(__dirname, dir, 'preview.png')});
  await b.close();
})();
