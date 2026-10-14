// build/html 의 글결 문서를 PNG로 찍어 발표/그림/글결/ 에 둔다 (2배 해상도).
// node 글결-화면-찍기.js
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node-tools/node_modules/playwright'); }
const path = require('path'), fs = require('fs');
const HTML = path.join(__dirname, 'build', 'html');
const OUT = path.join(__dirname, '..', '..', '글결');
fs.mkdirSync(OUT, { recursive: true });

(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 980, height: 900 } });
  const open = async f => {
    await p.goto('file://' + path.join(HTML, f), { waitUntil: 'networkidle' });
    await p.evaluate(() => document.fonts.ready);
  };
  // 슬라이드용 발췌: 본문(#content)만. 슬라이드에 들어가도록 간격만 줄이고, 긴 발췌는 두 단으로 놓는다.
  const TIGHT = `#content{padding-bottom:4px} #content h2{font-size:1.75em;margin:.2em 0 .35em}
    .sect1{padding-bottom:.6em} .sect1+.sect1{padding-top:.2em} .paragraph p{margin-bottom:.5em}
    .listingblock,.tableblock{margin-bottom:.7em} table.tableblock{margin-bottom:.7em}`;
  const TWO = `#content{column-count:2;column-gap:48px;max-width:none} .sect1{border-top:0!important}
    .listingblock,.paragraph,table.tableblock{break-inside:avoid} #content h2{break-after:avoid}`;
  const LAYOUT = { '발췌-02-오류-응답.html': [1600, TWO] };
  for (const f of fs.readdirSync(HTML).filter(f => f.startsWith('발췌-')).sort()) {
    const [w, extra] = LAYOUT[f] || [980, ''];
    await p.setViewportSize({ width: w, height: 900 });
    await open(f);
    await p.addStyleTag({ content: TIGHT + extra });
    await p.locator('#content').screenshot({ path: path.join(OUT, f.replace('발췌-', 'REST-Docs-').replace('.html', '.png')) });
  }
  // 전체 문서: 첫 화면(왼쪽 차례 + 머리말)과 한 API 전체(댓글 쓰기)
  await p.setViewportSize({ width: 1440, height: 900 });
  await open('index.html');
  await p.screenshot({ path: path.join(OUT, 'REST-Docs-00-첫-화면.png') });
  await p.setViewportSize({ width: 980, height: 900 });
  await open('index.html');
  await p.locator('#comment-create').locator('xpath=..').screenshot({ path: path.join(OUT, 'REST-Docs-03-댓글-쓰기-전체.png') });
  // Swagger UI: REST Docs에 적힌 API로 만든 명세를 Swagger UI로 띄운다
  await p.setViewportSize({ width: 1440, height: 1000 });
  await open('swagger/index.html');
  await p.waitForSelector('.opblock-summary');
  await p.addStyleTag({ content: '.swagger-ui .topbar{display:none}' });
  await p.screenshot({ path: path.join(OUT, 'Swagger-1-목록.png') });
  const op = p.locator('#operations-글-post-create');
  await op.locator('.opblock-summary').first().click();
  await p.waitForTimeout(600);
  await op.screenshot({ path: path.join(OUT, 'Swagger-2-글-쓰기.png') });
  await b.close();
})();
