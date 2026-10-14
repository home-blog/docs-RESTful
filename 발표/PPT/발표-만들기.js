// 발표 PPT와 대본을 만든다. 디자인은 발표/PPT/디자인-시스템.md (크림 · 코랄 · 다크).
//
//   cd 발표/PPT && npm install && node 발표-만들기.js
//   → 발표/RESTful-API-설계.pptx  (테마 · 레이아웃 · 섹션 · 발표자 노트 · 편집 가능한 차트)
//   → 발표/발표-흐름-15분.md        (같은 대사로 만든 대본)
//
// 대사는 대사.json, 차트 숫자는 측정/결과.json (python3 측정/페이징-측정.py 로 다시 잴 수 있다).
const fs = require("fs");
const os = require("os");
const path = require("path");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");
const JSZip = require(require.resolve("jszip", { paths: [require.resolve("pptxgenjs")] }));

const HERE = __dirname;
const TOP = path.dirname(HERE);
const REAL = path.join(HERE, "실제-응답");
const IMG = path.join(TOP, "그림", "글결");
const SAY = JSON.parse(fs.readFileSync(path.join(HERE, "대사.json"), "utf8"));
const BENCH = JSON.parse(fs.readFileSync(path.join(HERE, "측정", "결과.json"), "utf8"));
const OUT = process.env.OUT || path.join(TOP, "RESTful-API-설계.pptx");

// ------------------------------------------------------------------ 테마 (디자인-시스템.md 1-3, 2)
const THEME = {
  name: "REST 발표",
  headFontFace: "Noto Serif KR",
  bodyFontFace: "Pretendard",
  colors: {
    dk1: "141413", lt1: "FAF9F5", dk2: "181715", lt2: "EFE9DE",
    accent1: "CC785C", accent2: "A9583E", accent3: "6C6A64", accent4: "E8A55A",
    accent5: "5DB8A6", accent6: "C64545", hlink: "A9583E", folHlink: "6C6A64",
  },
};
const MONO = "JetBrains Mono";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                       // 13.333 × 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "RESTful API 설계";
pres.author = "이재웅";
const C = pres.SchemeColor;
const K = {                                        // 색 이름 → 테마 색 (테마 밖의 색은 HEX)
  ink: C.text1, canvas: C.background1, dark: C.text2, card: C.background2,
  coral: C.accent1, coralText: C.accent2, muted: C.accent3, amber: C.accent4, teal: C.accent5, error: C.accent6,
  body: "3D3D3A", mutedSoft: "8E8B82", hair: "E6DFD8", onDarkSoft: "A09D96", darkSoft: "1F1E1B",
  elevated: "252320", creamStrong: "E8E0D2", success: "5DB872", errorOnDark: "E5806F", dot: "4A4844",
};
const X = 0.71, W = 11.91;                         // 좌우 여백 1.8 cm, 내용 폭
const Y0 = 1.73;                                   // 내용 시작 4.4 cm

// ------------------------------------------------------------------ 레이아웃 (디자인-시스템.md 6)
pres.defineSlideMaster({
  title: "표지",
  background: { color: K.canvas },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: X, y: 2.35, w: 6.3, h: 1.9, fontSize: 54, color: K.ink, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: X, y: 4.45, w: 6.3, h: 0.9, fontSize: 20, color: K.muted, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "meta", type: "body", x: X, y: 6.35, w: 6.3, h: 0.4, fontSize: 14, color: K.muted, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "섹션",
  background: { color: K.dark },
  objects: [
    { placeholder: { options: { name: "num", type: "body", x: X, y: 2.1, w: 3, h: 1.1, fontSize: 60, fontFace: "+mj-lt", color: K.coral, align: "left", valign: "bottom", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X, y: 3.35, w: 11, h: 1.0, fontSize: 40, color: K.canvas, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: X, y: 4.5, w: 11, h: 0.6, fontSize: 20, color: K.onDarkSoft, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "본문",
  background: { color: K.canvas },
  objects: [
    { placeholder: { options: { name: "eyebrow", type: "body", x: X, y: 0.42, w: 9, h: 0.3, fontSize: 12, color: K.muted, charSpacing: 1.5, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: X, y: 0.74, w: W, h: 0.8, fontSize: 32, color: K.ink, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 12.0, y: 7.0, w: 0.62, h: 0.3, fontSize: 11, color: K.muted, align: "right" },
});
pres.defineSlideMaster({
  title: "마무리",
  background: { color: K.dark },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: X, y: 0.74, w: W, h: 0.8, fontSize: 32, color: K.canvas, align: "left", valign: "top", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ 구성 요소 (디자인-시스템.md 5)
const NOTES = [];                                  // [제목, 대사, 화면 설명, 예비?]
let section = "";
function addSection(title) { section = title; pres.addSection({ title }); }

function content(title, eyebrow, say, screen = "", spare = false) {
  const s = pres.addSlide({ masterName: "본문", sectionTitle: section });
  s.addText(eyebrow, { placeholder: "eyebrow" });
  s.addText(title, { placeholder: "title" });
  s.addNotes(say);
  NOTES.push([title, say, screen, spare]);
  return s;
}

function divider(num, title, desc, say) {
  const s = pres.addSlide({ masterName: "섹션", sectionTitle: section });
  s.addText(num, { placeholder: "num" });
  s.addText(title, { placeholder: "title" });
  s.addText(desc, { placeholder: "body" });
  s.addNotes(say);
  NOTES.push([`[섹션] ${title}`, say, "", false]);
}

function text(s, x, y, w, h, runs, o = {}) {
  // runs: 문자열, 또는 [[글자, {색·크기·굵게·mono}], …] 줄 배열
  const lines = typeof runs === "string" ? [[[runs, {}]]] : runs;
  const out = [];
  lines.forEach((line, i) => {
    const segs = (typeof line === "string" ? [line] : line).map((sg) => (typeof sg === "string" ? [sg, {}] : [sg[0], sg[1] || {}]));
    segs.forEach(([t, so], j) => {
      const opt = { color: so.color || o.color || K.ink, fontSize: so.size || o.size || 20, bold: !!so.bold };
      if (so.mono || o.mono) opt.fontFace = MONO;
      if (j === segs.length - 1 && i < lines.length - 1) opt.breakLine = true;
      out.push({ text: t, options: opt });
    });
  });
  s.addText(out, { x, y, w, h, isTextBox: true, margin: 0, valign: o.valign || "top", align: o.align || "left",
                   paraSpaceAfter: o.gap ?? 6, lineSpacingMultiple: o.line || 1.15, objectName: o.name || "text" });
}

function card(s, x, y, w, h, fill = K.card, name = "card") {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.12, objectName: name });
}

function badge(s, x, y, label) {
  const w = 0.3 + [...label].reduce((a, ch) => a + (/[\u3131-\uD79D]/.test(ch) ? 0.17 : 0.09), 0);
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.34, fill: { color: K.creamStrong }, rectRadius: 0.17, objectName: "badge" });
  s.addText(label, { x, y, w, h: 0.34, fontSize: 12, color: K.muted, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "badge-text" });
}

function codeWindow(s, x, y, w, h, lines, o = {}) {
  // 다크 코드 창: 바탕 + 창 머리 점 3개 + 고정폭 글자 (디자인-시스템.md 5, 5-1)
  card(s, x, y, w, h, K.dark, "code-window");
  [0, 1, 2].forEach((i) => s.addShape(pres.ShapeType.ellipse, { x: x + 0.22 + i * 0.19, y: y + 0.16, w: 0.11, h: 0.11, fill: { color: K.dot }, objectName: "code-window-dot" }));
  if (o.label) text(s, x + 0.9, y + 0.1, w - 1.1, 0.25, [[[o.label, { color: K.onDarkSoft, size: 11 }]]], { name: "code-window-label" });
  const runs = lines.map(([t, c]) => [[t || " ", { color: c || K.canvas, mono: true, size: o.size || 13 }]]);
  text(s, x + 0.28, y + 0.48, w - 0.5, h - 0.6, runs, { gap: 0, line: 1.05, name: "code-window-text" });
}

function inlineCode(s, x, y, w, t, size = 16, color = K.coralText) {
  const h = Math.max(0.6, (size / 72) * 1.4 + 0.32);
  card(s, x, y, w, h, K.card, "code-inline");
  text(s, x + 0.25, y, w - 0.5, h, [[[t, { mono: true, size, color }]]], { name: "code-inline-text", valign: "middle", gap: 0, line: 1.0 });
}

function table(s, x, y, colW, rows, o = {}) {
  const size = o.size || 16;
  const data = rows.map((row, i) => row.map((v, j) => {
    const head = i === 0;
    const color = head ? K.muted : ((o.color && o.color(i, j, v)) || K.ink);
    const cell = { text: v, options: { fontSize: head ? size - 3 : size, color, bold: false, valign: "middle", margin: [3, 8, 3, 0],
      border: [{ type: "none" }, { type: "none" }, head ? { pt: 1, color: "6C6A64" } : { pt: 0.75, color: K.hair }, { type: "none" }] } };
    if (!head && (o.mono || []).includes(j)) cell.options.fontFace = MONO;
    return cell;
  }));
  s.addTable(data, { x, y, w: colW.reduce((a, b) => a + b, 0), colW, rowH: o.rowH || 0.42, objectName: o.name || "table" });
}

async function picture(s, file, x, y, maxW, maxH, cuts = []) {
  // 실제 화면: 가로 폭에 맞추고, 세로로 긴 화면은 잘라 나란히 놓는다. 테두리는 hairline.
  const meta = await sharp(file).metadata();
  const edges = [0, ...cuts.map((c) => Math.round(meta.height * c)), meta.height];
  const parts = edges.slice(1).map((b, i) => ({ top: edges[i], height: b - edges[i] }));
  const gap = 0.25;
  const colW = (maxW - gap * (parts.length - 1)) / parts.length;
  const k = Math.min(colW / meta.width, maxH / Math.max(...parts.map((p) => p.height)));
  const totalW = parts.length * meta.width * k + gap * (parts.length - 1);
  let px = x + (maxW - totalW) / 2;
  for (const p of parts) {
    const f = path.join(os.tmpdir(), `slide-img-${process.pid}-${Math.random().toString(36).slice(2)}.png`);
    await sharp(file).extract({ left: 0, top: p.top, width: meta.width, height: p.height }).toFile(f);
    const w = meta.width * k, h = p.height * k;
    s.addImage({ path: f, x: px, y, w, h, objectName: "screenshot" });
    s.addShape(pres.ShapeType.rect, { x: px, y, w, h, fill: { type: "none" }, line: { color: K.hair, width: 0.75 }, objectName: "screenshot-frame" });
    px += w + gap;
  }
}

function http(fname, cmd, keep = ["Content-Type", "Location"]) {
  // 예제 서버에 실제로 보낸 curl -i 결과를 코드 창 줄로
  const raw = fs.readFileSync(path.join(REAL, fname), "utf8").replace(/\r/g, "").split("\n\n");
  const head = raw[0].split("\n");
  const body = raw.slice(1).join("\n\n").trim();
  const st = head[0].trim();
  const out = [["$ " + cmd, K.teal], [st, /^\S+ [45]/.test(st) ? K.errorOnDark : K.success]];
  head.slice(1).forEach((h) => { if (keep.includes(h.split(":")[0])) out.push([h, K.onDarkSoft]); });
  if (body) {
    out.push(["", null]);
    JSON.stringify(JSON.parse(body), null, 2).split("\n").forEach((l) => out.push([l, /"code"/.test(l) ? K.amber : null]));
  }
  return out;
}

const say = (title) => {
  const hit = [...SAY.main, ...SAY.spare].find((x) => x.title === title);
  if (!hit) throw new Error(`대사.json에 없는 제목: ${title}`);
  return hit.say;
};
const statusColor = (i, j, v) => (j === 0 && /^[45]/.test(v) ? K.error : null);
const CHART_TEXT = { titleFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
                     dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt", valAxisTitleFontFace: "+mn-lt" };

// ------------------------------------------------------------------ 슬라이드
async function build() {
  // 표지 ---------------------------------------------------------------
  addSection("시작");
  {
    const s = pres.addSlide({ masterName: "표지", sectionTitle: section });
    s.addText("RESTful API 설계", { placeholder: "title" });
    s.addText("URL · 메서드 · 상태 코드 · 에러 · 목록 · 문서", { placeholder: "body" });
    s.addText("이재웅 · 2026.10.16", { placeholder: "meta" });
    codeWindow(s, 7.55, 2.45, 5.07, 2.6, [["$ curl -i -X DELETE \\", K.teal], ["    localhost:8080/api/v1/posts/42", K.teal], ["", null],
      ["HTTP/1.1 204 No Content", K.success]], { label: "터미널", size: 15 });
    s.addNotes(say("표지"));
    NOTES.push(["표지", say("표지"), "", false]);
  }
  {
    const t = "REST로 설계한다는 것";
    const s = content(t, "INTRO", say(t));
    inlineCode(s, X, Y0, W, "DELETE /api/v1/posts/42   →   204 No Content", 22, K.ink);
    [["자원", "URL", "/api/v1/posts/42"], ["행동", "메서드", "DELETE"], ["결과", "상태 코드", "204 No Content"]].forEach(([k, v, ex], i) => {
      const x = X + i * (3.82 + 0.225);
      card(s, x, 2.75, 3.82, 2.35);
      text(s, x + 0.35, 3.0, 3.1, 0.35, [[[k, { color: K.muted, size: 16 }]]]);
      text(s, x + 0.35, 3.4, 3.1, 0.7, [[[v, { size: 30 }]]], { name: "card-title" });
      text(s, x + 0.35, 4.35, 3.1, 0.4, [[[ex, { mono: true, size: 15, color: K.coralText }]]]);
    });
    text(s, X, 5.6, W, 0.8, [[["REST는 표준 규격이 아니라 설계 스타일이다. 그래서 세부 규칙은 팀이 정한다.", { color: K.body, size: 20 }]]]);
  }

  // 01 URL -------------------------------------------------------------
  addSection("01 자원 중심 URL");
  divider("01", "자원 중심 URL", "주소는 자원만 가리키고, 행동은 메서드에 맡긴다", "먼저 URL부터 보겠습니다.");
  {
    const t = "URL에는 자원만 쓴다";
    const s = content(t, "01 · URL", say(t));
    table(s, X, Y0, [5.95, 5.96], [["흔히 보는 URL", "바꾼 URL"], ["GET  /getPosts", "GET    /posts"], ["POST /posts/create", "POST   /posts"],
      ["GET  /deletePost?id=42", "DELETE /posts/42"], ["GET  /post_list,  /Posts", "GET    /posts"]],
      { size: 18, mono: [0, 1], rowH: 0.5, color: (i, j) => (j === 0 ? K.error : null) });
    card(s, X, 4.6, 5.83, 1.75);
    text(s, X + 0.35, 4.85, 5.2, 1.4, [[["복수 명사 · 소문자 · 하이픈", { size: 20, bold: true }]], [["/blog-posts", { mono: true, size: 17, color: K.coralText }]],
      [["경로는 대소문자를 구분해서 한 글자만 달라도 404", { size: 15, color: K.muted }]]], { gap: 4 });
    card(s, X + 6.08, 4.6, 5.83, 1.75);
    text(s, X + 6.43, 4.85, 5.2, 1.4, [[["GET으로 상태를 바꾸지 않는다", { size: 20, bold: true }]],
      [["크롤러 · 링크 미리보기는 GET을 마음대로 보낸다", { size: 15, color: K.muted }]], [["삭제 링크를 공유만 해도 지워질 수 있다", { size: 15, color: K.muted }]]], { gap: 4 });
  }
  {
    const t = "계층은 두 단계까지, 보여 주는 방식은 쿼리로";
    const s = content(t, "01 · URL", say(t));
    table(s, X, Y0, [6.4, 5.51], [["요청", "뜻"], ["GET /posts", "글 목록"], ["GET /posts/42", "42번 글"], ["GET /posts/42/comments", "42번 글의 댓글"],
      ["GET /comments/7", "댓글 하나는 id만으로 → 끊는다"], ["GET /members/3/posts/42/comments/7", "✗ 앞의 id를 다 알아야 한다"],
      ["GET /posts?keyword=제주&page=0", "검색 · 정렬 · 쪽 번호는 쿼리"]],
      { size: 17, mono: [0], rowH: 0.52, color: (i) => (i === 5 ? K.error : null) });
    badge(s, X, 5.6, "중첩 = 자원 두 개까지 · id 하나로 찾히면 끊는다");
  }
  {
    const t = "CRUD로 안 떨어지는 행위";
    const s = content(t, "01 · URL", say(t));
    text(s, X, Y0, W, 0.4, [[["주문 취소 · 결제 승인 · 비밀번호 재설정은?", { size: 20, color: K.body }]]]);
    [["①", "PATCH /orders/42", '{"status":"CANCELED"}', "상태 값만 바꾼다. 단순하지만 환불 · 재고 복구가 숨는다"],
     ["②", "POST /orders/42/cancel", "", "행위를 드러낸다. 권한 · 검증을 따로 걸기 쉽다"],
     ["③", "POST /orders/42/cancellations", "", "취소를 자원으로 만든다. 취소 이력을 조회할 수 있다"]].forEach(([n, u, b, d], i) => {
      const x = X + i * (3.82 + 0.225);
      card(s, x, 2.35, 3.82, 2.75);
      text(s, x + 0.3, 2.55, 3.3, 0.45, [[[n, { size: 22, color: K.coralText }]]]);
      text(s, x + 0.3, 3.1, 3.3, 0.7, [[[u, { mono: true, size: 13 }]], ...(b ? [[[b, { mono: true, size: 12, color: K.muted }]]] : [])], { gap: 2 });
      text(s, x + 0.3, 4.0, 3.3, 0.95, [[[d, { size: 15, color: K.body }]]]);
    });
    card(s, X, 5.45, W, 0.95, K.coral, "callout-coral");
    text(s, X + 0.4, 5.66, W - 0.8, 0.55, [[["부수 작업이 있으면 ② · ③처럼 행위를 드러낸다", { size: 22, bold: true, color: K.ink }]]], { valign: "middle" });
  }

  // 02 메서드 · 상태 코드 ------------------------------------------------
  addSection("02 HTTP 메서드와 상태 코드");
  divider("02", "HTTP 메서드와 상태 코드", "안전성과 멱등성으로 고르고, 결과는 상태 코드로 알린다", "다음은 메서드와 상태 코드입니다.");
  {
    const t = "메서드는 안전성과 멱등성으로 고른다";
    const s = content(t, "02 · METHOD", say(t));
    const ox = (v) => (v === "×" ? K.error : v === "△" ? K.muted : null);
    table(s, X, Y0, [2.2, 5.5, 2.1, 2.11], [["메서드", "하는 일", "안전", "멱등"], ["GET", "조회", "○", "○"], ["POST", "생성", "×", "×"],
      ["PUT", "전체 교체 (안 보낸 칸은 비워짐)", "×", "○"], ["PATCH", "보낸 칸만 수정", "×", "△"], ["DELETE", "삭제", "×", "○"]],
      { size: 18, mono: [0], rowH: 0.48, color: (i, j, v) => (j >= 2 ? ox(v) : null) });
    card(s, X, 4.95, 5.83, 1.45);
    text(s, X + 0.35, 5.15, 5.2, 1.1, [[["안전", { size: 20, bold: true }]], [["서버 상태를 바꾸지 않는다 → 캐시 · 프리페치가 불러도 된다", { size: 15, color: K.body }]]], { gap: 4 });
    card(s, X + 6.08, 4.95, 5.83, 1.45);
    text(s, X + 6.43, 5.15, 5.2, 1.1, [[["멱등", { size: 20, bold: true }]], [["여러 번 보내도 결과가 같다 → 실패하면 다시 보내도 된다", { size: 15, color: K.body }]]], { gap: 4 });
  }
  {
    const t = "POST가 두 번 가면 두 번 만들어진다";
    const s = content(t, "02 · METHOD", say(t));
    codeWindow(s, X, Y0, 6.2, 2.45, [["POST /api/v1/payments", K.canvas], ["Idempotency-Key: 8f3a2c1e-4b7d-…", K.amber], ["", null],
      ['{ "orderId": 42, "amount": 30000 }', K.canvas]], { label: "요청 (예시)", size: 15 });
    card(s, X + 6.45, Y0, 5.46, 1.1);
    text(s, X + 6.75, Y0 + 0.17, 5, 0.8, [[["처음 온 키", { size: 18, bold: true }]], [["처리하고 결과를 키와 함께 저장", { size: 15, color: K.body }]]], { gap: 2 });
    card(s, X + 6.45, Y0 + 1.35, 5.46, 1.1);
    text(s, X + 6.75, Y0 + 1.52, 5, 0.8, [[["같은 키가 또 오면", { size: 18, bold: true }]], [["다시 처리하지 않고 저장한 결과를 반환", { size: 15, color: K.body }]]], { gap: 2 });
    table(s, X, 4.7, [3.6, 8.31], [["막는 곳", "막을 수 있는 것"], ["버튼 비활성화", "같은 화면에서 빠른 연속 클릭"],
      ["서버에서 키 확인", "재전송 · 새로고침 · 다른 탭 · 화면 없이 직접 호출"]], { size: 17, rowH: 0.48 });
  }
  {
    const t = "자주 쓰는 상태 코드";
    const s = content(t, "02 · STATUS CODE", say(t));
    table(s, X, Y0, [1.4, 3.5, 7.01], [["코드", "이름", "언제"], ["200", "OK", "조회 · 수정 성공"], ["201", "Created", "생성. Location 헤더에 새 주소"],
      ["204", "No Content", "삭제 성공, 바디 없음"], ["400", "Bad Request", "값이 빠졌거나 형식이 틀림"],
      ["401", "Unauthorized", "누구인지 모름 (로그인 안 함, 토큰 · 세션 만료)"], ["403", "Forbidden", "누구인지 알지만 권한 없음"],
      ["404", "Not Found", "없는 자원 (존재를 숨길 때도)"], ["409", "Conflict", "중복 · 동시 수정 충돌"], ["500", "Internal Server Error", "서버가 처리 못 한 예외"]],
      { size: 16, mono: [0, 1], rowH: 0.48, color: statusColor });
  }
  {
    const t = "실패를 200으로 보내면";
    const s = content(t, "02 · STATUS CODE", say(t), "왼쪽은 안티패턴 예시, 오른쪽은 예제 서버의 실제 응답");
    codeWindow(s, X, Y0, 5.83, 3.45, [["HTTP/1.1 200 OK", K.success], ["", null], ["{", null], ['  "success": false,', K.errorOnDark],
      ['  "message": "글이 없습니다"', null], ["}", null]], { label: "✗ 안티패턴 (예시)", size: 14 });
    codeWindow(s, X + 6.08, Y0, 5.83, 3.45, http("get-404.txt", "curl -i localhost:8080/api/v1/posts/99999"), { label: "예제 서버 실제 응답", size: 12 });
    card(s, X, 5.45, W, 0.95, K.coral, "callout-coral");
    text(s, X + 0.4, 5.66, W - 0.8, 0.55, [[["모니터링 · 로드밸런서 · 캐시 · 재시도는 바디가 아니라 상태 코드를 본다", { size: 20, bold: true, color: K.ink }]]], { valign: "middle" });
  }

  // 03 응답 · 에러 -------------------------------------------------------
  addSection("03 공통 응답과 에러 형식");
  divider("03", "공통 응답과 에러 형식", "모든 API가 같은 모양으로 답하고, 내부 정보는 로그에만 남긴다", "이번에는 응답과 에러의 모양입니다.");
  {
    const t = "에러는 모든 API가 같은 모양으로";
    const s = content(t, "03 · RESPONSE · ERROR", say(t), "예제 서버의 실제 400 · 409 응답");
    codeWindow(s, X, Y0, 5.83, 4.1, http("post-400.txt", "curl -i -X POST …/posts -d '{\"title\":\"\"}'"), { label: "실제 응답 · 400", size: 11 });
    codeWindow(s, X + 6.08, Y0, 5.83, 4.1, http("post-409.txt", "curl -i -X POST …/posts -d '{\"title\":\"제주 여행\"}'"), { label: "실제 응답 · 409", size: 11 });
    text(s, X, 6.05, W, 0.45, [[["type · title · status · detail", { mono: true, size: 15, color: K.muted }], ["  RFC 9457 표준     ", { size: 15, color: K.muted }],
      ["code", { mono: true, size: 15, color: K.coralText, bold: true }], ["  화면이 분기하는 값     ", { size: 15, color: K.muted }],
      ["errors", { mono: true, size: 15, color: K.coralText, bold: true }], ["  틀린 칸", { size: 15, color: K.muted }]]]);
  }
  {
    const t = "내부 정보는 로그로, 응답에는 traceId만";
    const s = content(t, "03 · RESPONSE · ERROR", say(t), "예시 화면 (예제 서버에는 아직 없는 기능)");
    badge(s, X + W - 0.9, 0.42, "예시");
    codeWindow(s, X, Y0, W, 1.55, [["HTTP/1.1 500", K.errorOnDark], ['{ "code": "INTERNAL_ERROR", "detail": "잠시 후 다시 시도해 주세요.", "traceId": "9b1deb4d" }', null]],
      { label: "사용자에게 가는 응답", size: 15 });
    codeWindow(s, X, 3.55, W, 1.85, [["ERROR [traceId=9b1deb4d] 글 조회 실패", K.errorOnDark], ["java.lang.NullPointerException: …", null],
      ["    at com.example.blog.PostService.find(PostService.java:42)", K.onDarkSoft]], { label: "서버 로그 (개발자만)", size: 15 });
    text(s, X, 5.75, W, 0.5, [[["스택 트레이스 · SQL · 테이블 이름은 응답에 넣지 않는다. 같은 traceId로 로그를 찾는다.", { size: 20, color: K.body }]]]);
  }

  // 04 예외 처리 · 검증 --------------------------------------------------
  addSection("04 전역 예외 처리와 입력 검증");
  divider("04", "전역 예외 처리와 입력 검증", "검증은 두 층으로, 응답 변환은 한 곳에서", "다음은 전역 예외 처리와 입력 검증입니다.");
  {
    const t = "검증과 예외 처리는 한 곳에서";
    const s = content(t, "04 · EXCEPTION · VALIDATION", say(t));
    const steps = ["요청", "@Valid 형식 검증", "컨트롤러", "서비스 (업무 규칙)", "DB"];
    const ws = [1.2, 2.75, 1.85, 2.95, 1.0];
    let x = X;
    steps.forEach((st, i) => {
      const strong = i === 1 || i === 3;
      card(s, x, Y0, ws[i], 0.6, strong ? K.creamStrong : K.card, "flow-step");
      text(s, x, Y0 + 0.15, ws[i], 0.3, [[[st, { size: 15, bold: strong, mono: i === 1 && false }]]], { align: "center" });
      x += ws[i];
      if (i < steps.length - 1) { text(s, x, Y0 + 0.13, 0.54, 0.35, [[["→", { size: 18, color: K.muted }]]], { align: "center" }); x += 0.54; }
    });
    table(s, X, 2.65, [2.2, 1.9, 4.9, 2.91], [["실패", "어디서", "예외", "응답"], ["빈 제목", "DTO 검증", "MethodArgumentNotValidException", "400 INVALID_INPUT"],
      ["없는 글", "서비스", "ApiException(POST_NOT_FOUND)", "404"], ["제목 중복", "서비스", "ApiException(DUPLICATE_TITLE)", "409"],
      ["예상 못 한 오류", "어디서든", "Exception", "500 + 로그"]], { size: 15, mono: [2, 3], rowH: 0.48, color: (i, j, v) => (j === 3 && /^[45]/.test(v) ? K.error : null) });
    text(s, X, 5.35, W, 1.0, [[["모두 ", { size: 18 }], ["@RestControllerAdvice", { mono: true, size: 17, color: K.coralText, bold: true }], [" 한 곳에서 같은 형식으로 바꾼다 · 컨트롤러에 try-catch 없음", { size: 18 }]],
      [["Security 필터에서 난 예외는 컨트롤러 밖이라 여기서 안 잡힌다", { size: 15, color: K.muted }]]], { gap: 6 });
  }
  {
    const t = "코드로 보면";
    const s = content(t, "04 · EXCEPTION · VALIDATION", say(t), "예제 프로젝트(발표/예제-프로젝트/blog-api)의 실제 코드를 줄인 것");
    const A = K.amber, D = K.onDarkSoft;
    codeWindow(s, X, Y0, 5.83, 4.7, [["record CreatePostRequest(", null], ["  @NotBlank @Size(max = 100) String title,", A], ["  @NotBlank String content) {}", A], ["", null],
      ["enum ErrorCode {", null], ['  POST_NOT_FOUND(NOT_FOUND, "글이 없음"),', A], ['  DUPLICATE_TITLE(CONFLICT, "같은 제목…");', A], ["}", null], ["", null],
      ["// 서비스", D], ["throw new ApiException(POST_NOT_FOUND, …);", null]], { label: "Dtos.java · ErrorCode.java", size: 13 });
    codeWindow(s, X + 6.08, Y0, 5.83, 4.7, [["@RestControllerAdvice", A], ["class GlobalExceptionHandler {", null], ["", null], ["  @ExceptionHandler(ApiException.class)", A],
      ["  ResponseEntity<ProblemDetail> handleApi(…) {", null], ["    body = forStatusAndDetail(status, …);", null], ['    body.setProperty("code", code);', null], ["  }", null], ["", null],
      ["  @ExceptionHandler(", A], ["    MethodArgumentNotValidException.class)", A], ["  … // 400 + 필드별 errors", D], ["}", null]], { label: "GlobalExceptionHandler.java", size: 13 });
  }

  // 05 페이징 · 검색 · 정렬 ----------------------------------------------
  addSection("05 페이징 · 검색 · 정렬");
  divider("05", "페이징 · 검색 · 정렬", "조건은 쿼리로 받고, 한도는 서버가 정한다", "이제 목록 API입니다.");
  {
    const t = "목록 요청은 쿼리로";
    const s = content(t, "05 · PAGINATION", say(t));
    inlineCode(s, X, Y0, W, "GET /api/v1/posts?topic=TRAVEL&keyword=제주&sort=createdAt,desc&sort=id,desc&page=0&size=20", 14);
    table(s, X, 2.6, [1.9, 3.8, 6.21], [["종류", "파라미터", "규칙"], ["필터", "topic=TRAVEL", "값이 같은 것만"], ["검색", "keyword=제주", "제목 · 본문에 들어 있는 것"],
      ["정렬", "sort=필드,방향", "여러 개 가능, 마지막은 id로 동점 정리"], ["페이징", "page=0&size=20", "0부터인지 1부터인지 문서에 적는다"]], { size: 17, mono: [1], rowH: 0.5 });
    card(s, X, 5.55, W, 0.85);
    text(s, X + 0.35, 5.77, W - 0.7, 0.45, [[["서버가 정할 것  ", { size: 18, bold: true }], ["size 최댓값 · 정렬 허용 필드 · 기본 정렬 (최신순 20개)", { size: 18, color: K.body }]]], { valign: "middle" });
  }
  {
    const t = "목록 응답에는 페이지 정보를 같이";
    const s = content(t, "05 · PAGINATION", say(t) + ` 직접 재 보니, 글 20개를 가져오는 데는 ${BENCH.page_query_ms}ms였는데 전체 개수를 세는 데는 ${Math.round(BENCH.count_query_ms)}ms가 걸렸습니다.`,
      "왼쪽은 응답 예시, 오른쪽 차트는 SQLite 100만 행에서 직접 잰 값 (차트를 두 번 누르면 숫자를 고칠 수 있다)");
    codeWindow(s, X, Y0, 5.6, 4.65, [["{", null], ['  "content": [', K.amber], ['    { "id": 43, "title": "부산 맛집" },', null], ['    { "id": 42, "title": "제주 여행" }, …', null],
      ["  ],", K.amber], ['  "page": {', K.amber], ['    "number": 0,', null], ['    "size": 20,', null], ['    "totalElements": 57,', null], ['    "totalPages": 3', null],
      ["  }", K.amber], ["}", null]], { label: "응답 (예시)", size: 14 });
    const cx = X + 5.85, cw = W - 5.85;
    s.addChart(pres.ChartType.bar, [{ name: "걸린 시간 (ms)", labels: ["목록 20개 (LIMIT 20)", "전체 개수 (COUNT(*))"], values: [BENCH.page_query_ms, BENCH.count_query_ms] }], {
      x: cx, y: Y0, w: cw, h: 3.0, barDir: "bar", chartColors: ["141413", "CC785C"], invertedColors: ["141413", "CC785C"],
      showTitle: true, title: `같은 100만 행에서 걸린 시간 (ms)`, titleFontSize: 14, titleColor: "3D3D3A",
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0.0#", dataLabelFontSize: 13, dataLabelColor: "141413",
      catAxisLabelColor: "3D3D3A", catAxisLabelFontSize: 13, valAxisLabelColor: "6C6A64", valAxisLabelFontSize: 11,
      valGridLine: { color: "E6DFD8", size: 0.75 }, catGridLine: { style: "none" }, valAxisLineShow: false, catAxisLineShow: false,
      showLegend: false, barGapWidthPct: 60, chartArea: { fill: { color: "FAF9F5" } }, plotArea: { fill: { color: "FAF9F5" } }, objectName: "chart-count-cost", ...CHART_TEXT,
    });
    text(s, cx, 4.95, cw, 1.4, [[["결과가 없으면 200 + 빈 배열 [ ]  (404 아님)", { size: 16, bold: true }]],
      [["totalElements를 주려면 COUNT 쿼리가 한 번 더 나간다 → 무한 스크롤이면 hasNext만", { size: 15, color: K.body }]]], { gap: 6 });
  }
  {
    const t = "오프셋 페이징과 커서 페이징";
    const s = content(t, "05 · PAGINATION", say(t));
    table(s, X, Y0, [2.2, 4.85, 4.86], [["", "오프셋", "커서"], ["요청", "?page=2&size=20", "?cursor=981&size=20"], ["SQL", "LIMIT 20 OFFSET 40", "WHERE id < 981 LIMIT 20"],
      ["장점", "쪽 번호로 바로 이동, 전체 쪽 수", "뒤로 가도 속도 일정, 중복 없음"], ["단점", "뒤 페이지일수록 느림, 중간 추가 시 중복 · 누락", "특정 쪽으로 바로 못 감"],
      ["어울리는 곳", "게시판 (쪽 번호)", "피드 · 무한 스크롤"]], { size: 17, rowH: 0.62 });
  }
  {
    const t = "직접 재 보면: 뒤로 갈수록 오프셋만 느려진다";
    const sayText = `실제로 재 봤습니다. SQLite에 글 100만 개를 넣고 20개씩 가져왔습니다. 오프셋은 1쪽에서 ${BENCH.offset_ms[0]}ms였는데, 5만 쪽에서는 ${Math.round(BENCH.offset_ms[BENCH.offset_ms.length - 1])}ms로 늘었습니다. 앞의 데이터를 전부 읽고 버리기 때문입니다. `
      + "커서는 어느 위치에서나 거의 0에 가깝게 일정했습니다. 숫자는 환경마다 다르지만, 뒤로 갈수록 오프셋만 느려진다는 건 같습니다.";
    const s = content(t, "05 · PAGINATION", sayText, "SQLite 100만 행에서 직접 잰 값. 차트를 두 번 누르면 숫자를 고칠 수 있다");
    badge(s, X + W - 1.3, 0.42, "직접 측정");
    const labels = BENCH.pages.map((p) => `${p.toLocaleString("en-US")}쪽`);
    s.addChart(pres.ChartType.bar, [{ name: "오프셋 (LIMIT … OFFSET)", labels, values: BENCH.offset_ms }, { name: "커서 (WHERE id < …)", labels, values: BENCH.cursor_ms }], {
      x: X, y: Y0, w: 8.1, h: 4.65, barDir: "col", barGrouping: "clustered", chartColors: ["CC785C", "141413"],
      showTitle: true, title: "20개를 가져오는 시간 (ms, 15회 중앙값)", titleFontSize: 14, titleColor: "3D3D3A",
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0.0#", dataLabelFontSize: 11, dataLabelColor: "3D3D3A",
      catAxisLabelColor: "3D3D3A", catAxisLabelFontSize: 12, valAxisLabelColor: "6C6A64", valAxisLabelFontSize: 11,
      valGridLine: { color: "E6DFD8", size: 0.75 }, catGridLine: { style: "none" }, valAxisLineShow: false,
      showLegend: true, legendPos: "t", legendFontSize: 13, legendColor: "3D3D3A", barGapWidthPct: 70,
      chartArea: { fill: { color: "FAF9F5" } }, plotArea: { fill: { color: "FAF9F5" } }, objectName: "chart-offset-vs-cursor", ...CHART_TEXT,
    });
    const last = BENCH.offset_ms.length - 1;
    text(s, X + 8.45, Y0 + 0.2, 3.46, 4.4, [[["오프셋", { size: 16, color: K.muted }]], [[`${BENCH.offset_ms[0]} → ${BENCH.offset_ms[last]} ms`, { size: 24, color: K.coralText }]], [" "],
      [["커서", { size: 16, color: K.muted }]], [["거의 일정", { size: 24 }]], [" "],
      [[`${BENCH.engine} · ${(BENCH.rows / 10000).toLocaleString()}만 행 · ${BENCH.size}개씩 · 이 노트북에서 측정. 숫자는 환경마다 다르다.`, { size: 13, color: K.muted }]]], { gap: 2 });
  }

  // 06 API 문서 ---------------------------------------------------------
  addSection("06 API 문서 작성");
  divider("06", "API 문서 작성", "손으로 쓰지 않고, 코드와 테스트에서 만든다", "마지막은 API 문서입니다.");
  {
    const t = "API 문서: Swagger와 REST Docs";
    const s = content(t, "06 · DOCS", say(t));
    table(s, X, Y0, [2.5, 4.7, 4.71], [["", "Swagger (springdoc)", "Spring REST Docs"], ["만드는 법", "의존성 추가 → 컨트롤러를 읽어 자동 생성", "API마다 테스트 작성 → 통과하면 생성"],
      ["정확도", "코드 기준. 설명 문구는 사람이 관리", "테스트가 실제로 주고받은 값"], ["운영 코드", "@Operation 같은 어노테이션이 붙음", "건드리지 않음"],
      ["화면에서 호출", "Try it out", "기본은 없음 (정적 HTML)"], ["비용", "시작이 쉽다", "테스트 작성 비용"]], { size: 16, rowH: 0.52 });
    card(s, X, 5.4, W, 0.95);
    text(s, X + 0.35, 5.62, W - 0.7, 0.5, [[["혼합  ", { size: 18, bold: true }], ["REST Docs 테스트 → OpenAPI 명세 (restdocs-api-spec) → Swagger UI", { size: 18, color: K.body }]]], { valign: "middle" });
  }
  for (const [t, file, cuts, screen] of [
    ["글결: Swagger", "Swagger-1-목록.png", [], "글결 REST Docs의 API로 명세를 만들어 Swagger UI로 띄운 화면"],
    ["글결: Swagger에서 API 하나 펼치기", "Swagger-2-글-쓰기.png", [0.5], "왼쪽 요청, 오른쪽 응답 예시"],
    ["글결: REST Docs", "REST-Docs-00-첫-화면.png", [], "글결 REST Docs 첫 화면 (Asciidoctor로 다시 만든 화면)"],
    ["글결: 에러 응답", "REST-Docs-02-오류-응답.png", [], "글결 REST Docs 8.1 · 8.3"]]) {
    const s = content(t, "06 · DOCS · 글결", say(t), screen);
    await picture(s, path.join(IMG, file), X, Y0, W, 5.3, cuts);
  }

  // 정리 -----------------------------------------------------------------
  addSection("정리");
  {
    const s = pres.addSlide({ masterName: "마무리", sectionTitle: section });
    s.addText("정리", { placeholder: "title" });
    [["URL", "자원만 · 복수 · 소문자 · 두 단계 · 행위는 드러나게"], ["메서드", "안전성 · 멱등성으로 고른다 · POST 중복은 키로 막는다"],
     ["상태 코드", "실패는 4xx · 5xx, 200에 실패를 담지 않는다"], ["에러", "한 모양 + code · 내부 정보는 로그와 traceId로"],
     ["예외 처리", "검증은 DTO와 서비스, 변환은 한 곳에서"], ["목록", "쿼리로 받고 한도를 정한다 · 게시판은 오프셋, 피드는 커서"],
     ["문서", "코드와 테스트에서 만든다 · Swagger와 REST Docs"]].forEach(([k, v], i) => {
      const y = Y0 + i * 0.68;
      text(s, X, y, 2.2, 0.5, [[[k, { size: 20, color: K.coral }]]]);
      text(s, X + 2.3, y, W - 2.3, 0.5, [[[v, { size: 20, color: K.canvas }]]]);
    });
    s.addNotes(say("정리"));
    NOTES.push(["정리", say("정리"), "", false]);
  }

  // 예비 -----------------------------------------------------------------
  addSection("예비 (질문이 나오면)");
  {
    const t = "성공 응답은 감쌀까?";
    const s = content(t, "APPENDIX", say(t), "질문이 나오면: 응답을 success/data로 감싸야 하나요?", true);
    [["그대로 주기", [["{", null], ['  "id": 42,', null], ['  "title": "제주 여행"', null], ["}", null]], ["+ 상태 코드와 겹치는 정보가 없다", "− 응답마다 꺼내는 방식이 조금씩 다르다"]],
     ["감싸기 (envelope)", [["{", null], ['  "success": true,', K.errorOnDark], ['  "data": { "id": 42, … }', null], ["}", null]], ["+ 꺼내는 코드가 하나, 메타 정보 넣기 쉽다", "− success가 상태 코드와 중복된다"]]].forEach(([h, code, pc], i) => {
      const x = X + i * 6.08;
      text(s, x, Y0, 5.83, 0.4, [[[h, { size: 20, bold: true }]]]);
      codeWindow(s, x, Y0 + 0.55, 5.83, 2.3, code, { size: 15 });
      text(s, x, Y0 + 3.1, 5.83, 1.0, pc.map((l) => [[l, { size: 16, color: K.body }]]), { gap: 4 });
    });
    text(s, X, 5.85, W, 0.5, [[["어느 쪽이든: 목록은 content + page · camelCase · ISO 8601", { size: 18, bold: true }]]]);
  }
  {
    const t = "[예비] 버전: /api/v1";
    const s = content(t.replace("[예비] ", ""), "APPENDIX", say(t), "질문이 나오면: 버전은 왜 붙이나요?", true);
    table(s, X, Y0, [4.4, 4.0, 3.51], [["변경", "예전 클라이언트", "v2 필요?"], ["칸 추가", "모르는 칸은 무시", "필요 없음"], ["칸 삭제", "읽으려던 값이 없음", "필요"],
      ["이름 변경 (writer → author)", "못 찾음", "필요"], ["타입 변경 (글자 → 객체)", "읽다가 실패", "필요"]], { size: 17, rowH: 0.52 });
    text(s, X, 4.7, W, 0.5, [[["v1과 v2를 같이 운영 → v1 요청이 거의 없어지면 닫는다", { size: 18, color: K.body }]]]);
  }
  for (const [t, file, cuts, screen] of [
    ["[예비] 글결이 쓰는 상태 코드", "REST-Docs-01-오류-상태-코드.png", [], "질문이 나오면: 실제 프로젝트에서는 어떤 코드를 썼나요?"],
    ["[예비] REST Docs에 API 하나가 적힌 모양", "REST-Docs-03-댓글-쓰기-전체.png", [0.36, 0.7], "질문이 나오면: REST Docs는 어떻게 생겼나요?"]]) {
    const s = content(t.replace("[예비] ", ""), "APPENDIX", say(t), screen, true);
    await picture(s, path.join(IMG, file), X, Y0, W, 5.3, cuts);
  }
  {
    const t = "[예비] MSA에서 보는 502 · 503 · 504";
    const s = content(t.replace("[예비] ", ""), "APPENDIX", say(t), "질문이 나오면: MSA에서는 에러가 어떻게 오나요?", true);
    table(s, X, Y0, [1.5, 3.9, 6.51], [["코드", "이름", "언제"], ["502", "Bad Gateway", "뒤쪽 서비스가 잘못된 응답을 줌"], ["503", "Service Unavailable", "과부하 · 점검 · 배포 중"],
      ["504", "Gateway Timeout", "제한 시간 안에 응답이 없음"]], { size: 17, mono: [0, 1], rowH: 0.52, color: statusColor });
    text(s, X, 4.0, W, 0.5, [[["다른 서비스의 에러는 그대로 넘기지 않고 내 API의 에러 형식으로 바꾼다", { size: 18, color: K.body }]]]);
  }
}

// ------------------------------------------------------------------ 테마 색 · 한글 글꼴 쓰기
// pptxgenjs는 테마 색을 Office 기본값으로 쓰고, 한글(ea) 글꼴 칸을 비워 둔다. 둘 다 채운다.
async function patchTheme(file) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  for (const name of Object.keys(zip.files).filter((n) => /^ppt\/theme\/theme\d+\.xml$/.test(n))) {
    let xml = await zip.file(name).async("string");
    for (const [slot, hex] of Object.entries(THEME.colors)) {
      xml = xml.replace(new RegExp(`(<a:${slot}>)[\\s\\S]*?(</a:${slot}>)`), `$1<a:srgbClr val="${hex}"/>$2`);
    }
    xml = xml.replace(/(<a:(?:theme|clrScheme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, `$1${THEME.name}"`);
    const fontBlock = (tag, face) => {
      xml = xml.replace(new RegExp(`<a:${tag}>([\\s\\S]*?)</a:${tag}>`), (m, inner) => {
        inner = inner.replace(/<a:ea typeface="[^"]*"\/>/, `<a:ea typeface="${face}"/>`)
                     .replace(/<a:font script="Hang" typeface="[^"]*"\/>/, `<a:font script="Hang" typeface="${face}"/>`);
        if (!/script="Hang"/.test(inner)) inner += `<a:font script="Hang" typeface="${face}"/>`;
        return `<a:${tag}>${inner}</a:${tag}>`;
      });
    };
    fontBlock("majorFont", THEME.headFontFace);
    fontBlock("minorFont", THEME.bodyFontFace);
    zip.file(name, xml);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

// ------------------------------------------------------------------ 대본
function script() {
  const secs = (t) => Math.max(5, Math.round(t.length / 5.5 / 5) * 5);
  const mm = (t) => `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`;
  const main = NOTES.filter((n) => !n[3]);
  const total = main.reduce((a, n) => a + secs(n[1]), 0);
  const L = ["# 발표 흐름 (약 15분 + 질문)", "",
    "- 일시: 2026-10-16(금) 13:30 · 발표자: 이재웅(AIGJ_01_012)",
    "- 주제: RESTful API 설계 (자원 중심 URL, HTTP 메서드와 상태 코드, 공통 응답·에러 형식, 전역 예외 처리와 입력 검증, 페이징·검색·정렬, API 문서 작성)",
    "- 대상: 동료 개발자 (주니어). 문법보다 **왜 그렇게 정하는지와 선택지 사이의 트레이드오프**를 전한다.",
    "- 발표 파일: [`RESTful-API-설계.pptx`](RESTful-API-설계.pptx) — 발표자 노트에 아래 대사가 그대로 들어 있다. 디자인 규칙은 [`PPT/디자인-시스템.md`](PPT/디자인-시스템.md).",
    "- 차트 두 개는 PowerPoint 네이티브 차트라 두 번 눌러 숫자를 고칠 수 있다. 값은 [`PPT/측정/페이징-측정.py`](PPT/측정/페이징-측정.py)로 직접 잰 것.",
    "- 고칠 때: [`PPT/대사.json`](PPT/대사.json)(대사)이나 [`PPT/발표-만들기.js`](PPT/발표-만들기.js)(화면)를 바꾸고 `cd 발표/PPT && node 발표-만들기.js`를 실행하면 PPT와 이 대본이 같이 바뀐다.", "",
    "## 시간 배분 (대사 길이로 어림)", "", "| # | 슬라이드 | 시간 | 누적 |", "|---|---|---|---|"];
  let t = 0;
  main.forEach((n, i) => { t += secs(n[1]); L.push(`| ${i + 1} | ${n[0]} | ${mm(secs(n[1]))} | ${mm(t)} |`); });
  L.push("", `> 합계 약 ${Math.floor(total / 60)}분 ${total % 60}초. 섹션 슬라이드는 한 문장만 말하고 넘긴다. 넘치면 '오프셋 페이징과 커서 페이징' 표는 짧게 짚고 바로 측정 차트로 넘어간다.`, "", "---", "");
  main.forEach((n, i) => { L.push(`## ${i + 1}. ${n[0]} (${mm(secs(n[1]))})`, ""); if (n[2]) L.push(`*화면: ${n[2]}*`, ""); L.push(`> ${n[1]}`, "", "---", ""); });
  L.push("## 예비 슬라이드 (PPT 맨 뒤, 질문이 나오면)", "");
  NOTES.filter((n) => n[3]).forEach((n, i) => L.push(`### ${main.length + i + 1}. ${n[0].replace("[예비] ", "")}`, "", `*${n[2]}*`, "", `> ${n[1]}`, ""));
  L.push("## 질문 대비", "", "자세한 답: [10-예상-질문과-답.md](../10-예상-질문과-답.md)", "", "| 질문 | 짧은 답 |", "|---|---|", ...SAY.qa.map(([q, a]) => `| ${q} | ${a} |`));
  L.push("", "## 발표 전 체크", "",
    "- [ ] 발표 PC에 Noto Serif KR · Pretendard · JetBrains Mono가 있는지 확인한다. 없으면 설치하거나 파일 › 옵션 › 저장 › 파일의 글꼴 포함으로 저장한다",
    "- [ ] 발표자 보기로 노트를 보며 한 번, 노트 없이 한 번 리허설해서 15분 안쪽인지 잰다",
    "- [ ] 코드 창과 차트가 뒷자리에서도 보이는지 확인한다",
    "- [ ] (선택) 시연: 예제 서버를 띄워 `curl -i localhost:8080/api/v1/posts/99999` → 404를 보여 준다", "");
  fs.writeFileSync(path.join(TOP, "발표-흐름-15분.md"), L.join("\n"));
  return total;
}

(async () => {
  await build();
  await pres.writeFile({ fileName: OUT });
  await patchTheme(OUT);
  const total = script();
  console.log(OUT, `${NOTES.filter((n) => !n[3]).length} main + ${NOTES.filter((n) => n[3]).length} spare, about ${Math.floor(total / 60)}:${String(total % 60).padStart(2, "0")}`);
})();
