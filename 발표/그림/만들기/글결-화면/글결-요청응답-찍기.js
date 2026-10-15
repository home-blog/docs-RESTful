// 글결 REST Docs의 '3.3 분류 추가' 요청 · 응답 블록을 슬라이드용 PNG로 찍고,
// 첫 줄 · 헤더 · 바디가 그림의 어디에 있는지(비율)를 JSON으로 남긴다.
// node 글결-요청응답-찍기.js   (먼저 build/html 이 있어야 한다: python3 글결-화면-만들기.py)
let pw;
try { pw = require('playwright'); } catch { pw = require('/opt/node-tools/node_modules/playwright'); }
const path = require('path'), fs = require('fs');
const HTML = path.join(__dirname, 'build', 'html', 'index.html');
const OUT = path.join(__dirname, '..', '..', '글결');

// 슬라이드에서 읽히도록 글자를 키우고, 긴 토큰 줄은 접는다
const CSS = `.listingblock pre{font-size:19px!important;line-height:1.5!important;white-space:pre-wrap!important;word-break:break-all!important;padding:18px 22px!important}
  .listingblock{margin:0!important}`;

(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 2, viewport: { width: 760, height: 900 } });
  await p.goto('file://' + HTML, { waitUntil: 'networkidle' });
  await p.addStyleTag({ content: CSS });
  await p.evaluate(() => document.fonts.ready);
  const marks = {};
  for (const [id, file, firstHeader] of [
    ['category-create_http_request', 'REST-Docs-04-요청.png', 'Content-Type'],
    ['category-create_http_response', 'REST-Docs-05-응답.png', 'Set-Cookie'],
  ]) {
    const block = p.locator(`#${id}`).locator('xpath=..').locator('.listingblock').first();
    await block.scrollIntoViewIfNeeded();
    // 첫 줄 / 헤더 / 바디의 위치를 글자 범위로 재서 블록 기준 비율로 바꾼다
    const r = await block.evaluate((el, firstHeader) => {
      const pre = el.querySelector('pre');
      const text = pre.textContent;
      const walker = document.createTreeWalker(pre, NodeFilter.SHOW_TEXT);
      const nodes = []; let n, pos = 0;
      while ((n = walker.nextNode())) { nodes.push([n, pos]); pos += n.length; }
      const at = (i) => { for (const [node, start] of nodes) if (i < start + node.length) return [node, i - start]; const [node, start] = nodes[nodes.length - 1]; return [node, node.length]; };
      const rect = (a, z) => { const g = document.createRange(); g.setStart(...at(a)); g.setEnd(...at(z)); return g.getBoundingClientRect(); };
      const box = el.getBoundingClientRect();
      const lineEnd = text.indexOf('\n');
      const h0 = text.indexOf(firstHeader);
      const blank = text.indexOf('\n\n');
      const body = text.indexOf('{', blank);
      const end = text.trimEnd().length;
      const rel = (q) => ({ x: (q.left - box.left) / box.width, y: (q.top - box.top) / box.height, w: q.width / box.width, h: q.height / box.height });
      return { line: rel(rect(0, lineEnd)), headers: rel(rect(h0, blank)), body: rel(rect(body, end)) };
    }, firstHeader);
    await block.screenshot({ path: path.join(OUT, file) });
    marks[file] = r;
  }
  fs.writeFileSync(path.join(OUT, 'REST-Docs-요청응답-위치.json'), JSON.stringify(marks, null, 2));
  console.log(JSON.stringify(marks, null, 2));
  await b.close();
})();
