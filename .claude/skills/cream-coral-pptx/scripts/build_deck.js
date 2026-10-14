#!/usr/bin/env node
// cream-coral-pptx 덱 엔진: 덱 스펙(JSON) → .pptx (테마 · 레이아웃 · 섹션 · 발표자 노트 · 네이티브 차트) + 대본 .md
//
//   node build_deck.js spec.json [--out deck.pptx] [--script script.md]
//
// 필요한 패키지: pptxgenjs, sharp (작업 폴더에서 `npm install pptxgenjs@3.12.0 sharp@0.33.5`).
// 스펙 형식은 references/spec-format.md. 상대 경로(이미지, curl 파일)는 스펙 파일 위치 기준.
const fs = require("fs");
const os = require("os");
const path = require("path");

function need(name) {
  for (const base of [process.cwd(), path.join(process.cwd(), "node_modules"), __dirname]) {
    try { return require(require.resolve(name, { paths: [base] })); } catch { /* 다음 위치 */ }
  }
  try { return require(name); } catch {
    console.error(`'${name}'을(를) 찾을 수 없습니다. 작업 폴더에서: npm install pptxgenjs@3.12.0 sharp@0.33.5`);
    process.exit(1);
  }
}
const pptxgen = need("pptxgenjs");
const sharp = need("sharp");
const JSZip = require(require.resolve("jszip", { paths: [path.dirname(require.resolve("pptxgenjs", { paths: [process.cwd(), __dirname] }))] }));

// ------------------------------------------------------------------ 입력
const args = process.argv.slice(2);
if (!args[0]) { console.error("사용법: node build_deck.js spec.json [--out deck.pptx] [--script script.md]"); process.exit(1); }
const specPath = path.resolve(args[0]);
const BASE = path.dirname(specPath);
const SPEC = JSON.parse(fs.readFileSync(specPath, "utf8"));
const opt = (k) => { const i = args.indexOf(k); return i > 0 ? path.resolve(args[i + 1]) : null; };
const OUT = opt("--out") || path.resolve(BASE, SPEC.output || "deck.pptx");
const SCRIPT = opt("--script") || (SPEC.script === false ? null : path.resolve(BASE, SPEC.script || OUT.replace(/\.pptx$/, "-대본.md")));
const rel = (p) => (path.isAbsolute(p) ? p : path.resolve(BASE, p));

// ------------------------------------------------------------------ 테마 (references/design-system.md 1, 2)
const FONTS = { head: "Noto Serif KR", body: "Pretendard", mono: "JetBrains Mono", ...(SPEC.fonts || {}) };
const THEME = {
  name: SPEC.themeName || "Cream Coral",
  colors: { dk1: "141413", lt1: "FAF9F5", dk2: "181715", lt2: "EFE9DE", accent1: "CC785C", accent2: "A9583E",
            accent3: "6C6A64", accent4: "E8A55A", accent5: "5DB8A6", accent6: "C64545", hlink: "A9583E", folHlink: "6C6A64" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";                       // 13.333 × 7.5 in
pres.theme = { headFontFace: FONTS.head, bodyFontFace: FONTS.body };
pres.title = SPEC.title || "";
pres.author = SPEC.author || "";
const C = pres.SchemeColor;
const K = {
  ink: C.text1, canvas: C.background1, dark: C.text2, card: C.background2,
  coral: C.accent1, coralText: C.accent2, muted: C.accent3, amber: C.accent4, teal: C.accent5, error: C.accent6,
  body: "3D3D3A", mutedSoft: "8E8B82", hair: "E6DFD8", onDark: "FAF9F5", onDarkSoft: "A09D96", elevated: "252320",
  creamStrong: "E8E0D2", success: "5DB872", errorOnDark: "E5806F", dot: "4A4844",
};
const color = (c, fallback) => (!c ? fallback : K[c] !== undefined ? K[c] : /^[0-9A-Fa-f]{6}$/.test(c) ? c.toUpperCase() : fallback);
const SERIES = ["CC785C", "141413", "A9583E", "6C6A64", "E8A55A", "5DB8A6"];
const X = 0.71, W = 11.91, Y0 = 1.73, BOTTOM = 7.0, GAP = 0.25;

// ------------------------------------------------------------------ 레이아웃 (references/design-system.md 6)
const ph = (name, type, o) => ({ placeholder: { options: { name, type, align: "left", valign: "top", margin: 0, ...o }, text: "" } });
pres.defineSlideMaster({ title: "표지", background: { color: K.canvas }, objects: [
  ph("title", "title", { x: X, y: 2.35, w: 6.3, h: 1.9, fontSize: 54, color: K.ink, valign: "bottom" }),
  ph("body", "body", { x: X, y: 4.45, w: 6.3, h: 0.9, fontSize: 20, color: K.muted }),
  ph("meta", "body", { x: X, y: 6.35, w: 6.3, h: 0.4, fontSize: 14, color: K.muted })] });
pres.defineSlideMaster({ title: "표지-넓게", background: { color: K.canvas }, objects: [
  ph("title", "title", { x: X, y: 2.2, w: W, h: 2.0, fontSize: 54, color: K.ink, valign: "bottom" }),
  ph("body", "body", { x: X, y: 4.4, w: W, h: 0.9, fontSize: 20, color: K.muted }),
  ph("meta", "body", { x: X, y: 6.35, w: W, h: 0.4, fontSize: 14, color: K.muted })] });
pres.defineSlideMaster({ title: "섹션", background: { color: K.dark }, objects: [
  ph("num", "body", { x: X, y: 2.1, w: 3, h: 1.1, fontSize: 60, fontFace: "+mj-lt", color: K.coral, valign: "bottom" }),
  ph("title", "title", { x: X, y: 3.35, w: 11, h: 1.0, fontSize: 40, color: K.canvas }),
  ph("body", "body", { x: X, y: 4.5, w: 11, h: 0.6, fontSize: 20, color: K.onDarkSoft })] });
pres.defineSlideMaster({ title: "본문", background: { color: K.canvas }, objects: [
  ph("eyebrow", "body", { x: X, y: 0.42, w: 9, h: 0.3, fontSize: 12, color: K.muted, charSpacing: 1.5 }),
  ph("title", "title", { x: X, y: 0.74, w: W, h: 0.8, fontSize: 32, color: K.ink })],
  slideNumber: { x: 12.0, y: 7.0, w: 0.62, h: 0.3, fontSize: 11, color: K.muted, align: "right" } });
pres.defineSlideMaster({ title: "마무리", background: { color: K.dark }, objects: [
  ph("title", "title", { x: X, y: 0.74, w: W, h: 0.8, fontSize: 32, color: K.canvas })] });

// ------------------------------------------------------------------ 글자
// 줄: "문자열" 또는 [조각, …]. 조각: "문자열" 또는 ["문자열", {color, size, bold, mono}]
function runs(lines, d) {
  const out = [];
  lines.forEach((line, i) => {
    const segs = (Array.isArray(line) ? line : [line]).map((sg) => (typeof sg === "string" ? [sg, {}] : [sg[0], sg[1] || {}]));
    segs.forEach(([t, so], j) => {
      const o = { color: color(so.color, d.color), fontSize: so.size || d.size, bold: !!(so.bold ?? d.bold), italic: !!so.italic };
      if (so.mono || d.mono) o.fontFace = FONTS.mono;
      if (j === segs.length - 1 && i < lines.length - 1) o.breakLine = true;
      out.push({ text: String(t), options: o });
    });
  });
  return out;
}
function text(s, x, y, w, h, lines, d = {}) {
  s.addText(runs(lines, { color: K.ink, size: 20, ...d }), { x, y, w, h, isTextBox: true, margin: 0, valign: d.valign || "top",
    align: d.align || "left", paraSpaceAfter: d.gap ?? 6, lineSpacingMultiple: d.line || 1.15, objectName: d.name || "text" });
}
const lineH = (size, mult = 1.3) => (size / 72) * mult;
const textHeight = (lines, size, gap = 6) => lines.length * lineH(size) + Math.max(0, lines.length - 1) * (gap / 72) + 0.05;

// ------------------------------------------------------------------ 구성 요소 (references/design-system.md 5)
function card(s, x, y, w, h, fill = K.card, name = "card") {
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h, fill: { color: fill }, rectRadius: 0.12, objectName: name });
}
function badge(s, x, y, label) {
  const w = 0.3 + [...label].reduce((a, ch) => a + (/[ㄱ-힝]/.test(ch) ? 0.17 : 0.09), 0);
  s.addShape(pres.ShapeType.roundRect, { x, y, w, h: 0.34, fill: { color: K.creamStrong }, rectRadius: 0.17, objectName: "badge" });
  s.addText(label, { x, y, w, h: 0.34, fontSize: 12, color: K.muted, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: "badge-text" });
  return w;
}
function codeLines(lines) {
  // 줄: "문자열" 또는 ["문자열", 색 이름]
  return lines.map((l) => (Array.isArray(l) ? [l[0], color(l[1], K.onDark)] : [l, K.onDark]));
}
function codeWindow(s, x, y, w, h, lines, o = {}) {
  card(s, x, y, w, h, K.dark, "code-window");
  [0, 1, 2].forEach((i) => s.addShape(pres.ShapeType.ellipse, { x: x + 0.22 + i * 0.19, y: y + 0.16, w: 0.11, h: 0.11, fill: { color: K.dot }, objectName: "code-window-dot" }));
  if (o.label) text(s, x + 0.9, y + 0.1, w - 1.1, 0.25, [[[o.label, { color: "onDarkSoft", size: 11 }]]], { name: "code-window-label" });
  const r = lines.map(([t, c]) => [[t || " ", { color: c, mono: true, size: o.size || 13 }]]);
  text(s, x + 0.28, y + 0.48, w - 0.5, h - 0.6, r, { gap: 0, line: 1.05, name: "code-window-text", color: K.onDark });
}
function httpLines(file, cmd, keep = ["Content-Type", "Location"]) {
  // curl -i 로 받은 실제 응답 파일 → 코드 창 줄 (CRLF 처리, JSON 들여쓰기, "code" 줄 강조)
  const raw = fs.readFileSync(rel(file), "utf8").replace(/\r/g, "").split("\n\n");
  const head = raw[0].split("\n");
  const body = raw.slice(1).join("\n\n").trim();
  const st = head[0].trim();
  const out = [];
  if (cmd) out.push(["$ " + cmd, K.teal]);
  out.push([st, /^\S+ [45]/.test(st) ? K.errorOnDark : K.success]);
  head.slice(1).forEach((h) => { if (keep.includes(h.split(":")[0])) out.push([h, K.onDarkSoft]); });
  if (body) {
    out.push(["", K.onDark]);
    let pretty; try { pretty = JSON.stringify(JSON.parse(body), null, 2).split("\n"); } catch { pretty = body.split("\n"); }
    pretty.forEach((l) => out.push([l, /"code"/.test(l) ? K.amber : K.onDark]));
  }
  return out;
}
function table(s, x, y, w, b) {
  const size = b.size || 16, rowH = b.rowH || Math.max(0.42, lineH(size, 1.9));
  const ratios = b.colW || b.rows[0].map(() => 1);
  const sum = ratios.reduce((a, c) => a + c, 0);
  const colW = ratios.map((r) => (r / sum) * w);
  const statusCol = b.status === true ? 0 : b.status;
  const data = b.rows.map((row, i) => row.map((v, j) => {
    const head = i === 0;
    let c = head ? K.muted : K.ink;
    if (!head && statusCol !== undefined && statusCol !== false && j === statusCol && /^[45]\d\d/.test(String(v))) c = K.error;
    if (!head && b.colorCol && b.colorCol[j]) c = color(b.colorCol[j], c);
    if (!head && b.colorRow && b.colorRow[i]) c = color(b.colorRow[i], c);
    if (!head && (b.marks !== false) && /^[×✕✗]$/.test(String(v).trim())) c = K.error;
    const cell = { text: String(v), options: { fontSize: head ? size - 3 : size, color: c, valign: "middle", margin: [3, 8, 3, 0],
      border: [{ type: "none" }, { type: "none" }, head ? { pt: 1, color: "6C6A64" } : { pt: 0.75, color: K.hair }, { type: "none" }] } };
    if (!head && (b.mono || []).includes(j)) cell.options.fontFace = FONTS.mono;
    return cell;
  }));
  s.addTable(data, { x, y, w, colW, rowH, objectName: "table" });
  return b.rows.length * rowH + 0.05;
}
async function imageCols(s, file, cuts, x, y, maxW, maxH) {
  const meta = await sharp(file).metadata();
  const edges = [0, ...(cuts || []).map((c) => Math.round(meta.height * c)), meta.height];
  const parts = edges.slice(1).map((b, i) => ({ top: edges[i], height: b - edges[i] }));
  const gap = 0.25;
  const colW = (maxW - gap * (parts.length - 1)) / parts.length;
  const k = Math.min(colW / meta.width, maxH / Math.max(...parts.map((p) => p.height)));
  const totalW = parts.length * meta.width * k + gap * (parts.length - 1);
  let px = x + (maxW - totalW) / 2, used = 0;
  for (const p of parts) {
    const f = path.join(os.tmpdir(), `ccp-${process.pid}-${Math.random().toString(36).slice(2)}.png`);
    await sharp(file).extract({ left: 0, top: p.top, width: meta.width, height: p.height }).toFile(f);
    const w = meta.width * k, h = p.height * k;
    s.addImage({ path: f, x: px, y, w, h, objectName: "screenshot" });
    s.addShape(pres.ShapeType.rect, { x: px, y, w, h, fill: { type: "none" }, line: { color: K.hair, width: 0.75 }, objectName: "screenshot-frame" });
    px += w + gap; used = Math.max(used, h);
  }
  return used;
}
function chart(s, x, y, w, h, b) {
  const types = { bar: pres.ChartType.bar, col: pres.ChartType.bar, line: pres.ChartType.line, pie: pres.ChartType.pie, doughnut: pres.ChartType.doughnut };
  const t = b.chartType || "col";
  const data = b.series.map((sr) => ({ name: sr.name, labels: b.labels, values: sr.values }));
  const single = data.length === 1;
  const o = {
    x, y, w, h, showTitle: !!b.title, title: b.title || "", titleFontSize: 14, titleColor: "3D3D3A",
    showValue: b.showValue !== false, dataLabelFormatCode: b.format || (b.showPercent ? "0%" : "#,##0.##"), dataLabelFontSize: 12, dataLabelColor: "3D3D3A",
    catAxisLabelColor: "3D3D3A", catAxisLabelFontSize: 12, valAxisLabelColor: "6C6A64", valAxisLabelFontSize: 11,
    valGridLine: { color: "E6DFD8", size: 0.75 }, catGridLine: { style: "none" }, valAxisLineShow: false,
    showLegend: !single || t === "pie" || t === "doughnut", legendPos: b.legendPos || "t", legendFontSize: 12, legendColor: "3D3D3A",
    chartColors: b.colors || (single && (t === "bar" || t === "col") && b.highlight !== undefined
      ? b.labels.map((_, i) => (i === b.highlight ? "CC785C" : "141413")) : SERIES),
    chartArea: { fill: { color: "FAF9F5" } }, plotArea: { fill: { color: "FAF9F5" } }, objectName: b.name || "chart",
    titleFontFace: "+mn-lt", catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt", legendFontFace: "+mn-lt",
  };
  if (t === "bar" || t === "col") Object.assign(o, { barDir: t === "bar" ? "bar" : "col", barGrouping: b.stacked ? "stacked" : "clustered",
    dataLabelPosition: b.stacked ? "ctr" : "outEnd", barGapWidthPct: 70 });
  // 가로 막대는 기본으로 아래에서 위로 쌓여 표와 순서가 반대가 된다. 위에서 아래로 읽히게 뒤집는다.
  if (t === "bar") Object.assign(o, { catAxisOrientation: "maxMin", catAxisCrossesAt: "max" });
  if (t === "line") Object.assign(o, { lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 7, dataLabelPosition: "t" });
  // 막대 안 · 조각 안 숫자는 짙은 바탕(잉크 · 코랄) 위에 놓이므로 흰 굵은 글자 (14pt 굵게는 큰 글자 기준 3:1 충족)
  if (t === "pie" || t === "doughnut") Object.assign(o, { dataLabelPosition: t === "pie" ? "bestFit" : undefined, showValue: !b.showPercent && b.showValue !== false,
    showPercent: !!b.showPercent, holeSize: 55, dataLabelColor: "FFFFFF", dataLabelFontSize: 14, dataLabelFontBold: true });
  if (b.stacked) Object.assign(o, { dataLabelColor: "FFFFFF", dataLabelFontSize: 14, dataLabelFontBold: true });
  if (single && b.highlight !== undefined && (t === "bar" || t === "col")) o.invertedColors = o.chartColors;
  if (b.valueTitle) Object.assign(o, { showValAxisTitle: true, valAxisTitle: b.valueTitle, valAxisTitleFontSize: 11, valAxisTitleColor: "6C6A64", valAxisTitleFontFace: "+mn-lt" });
  s.addChart(types[t], data, o);
}

// ------------------------------------------------------------------ 블록 배치 (위에서 아래로 쌓고, row는 옆으로)
function estimate(b, w) {
  if (b.h) return b.h;
  switch (b.kind) {
    case "text": return textHeight(b.lines, b.size || 20, b.gap ?? 6);
    case "table": { const size = b.size || 16; return b.rows.length * (b.rowH || Math.max(0.42, lineH(size, 1.9))) + 0.05; }
    case "code": case "http": { const n = b.kind === "http" ? httpLines(b.file, b.cmd).length : b.lines.length; return n * lineH(b.size || 13, 1.25) + 0.8; }
    case "inline": return Math.max(0.6, lineH(b.size || 16, 1.4) + 0.32);
    case "cards": return 2.1;
    case "callout": return 0.95;
    case "chart": return 4.2;
    case "image": return 4.8;
    case "badge": return 0.34;
    case "row": { const n = b.cols.length; const cw = (w - GAP * (n - 1)) / n; return Math.max(...b.cols.map((c) => estimate(c, cw))); }
    default: return 0.5;
  }
}
async function place(s, b, x, y, w, room) {
  const h = Math.min(estimate(b, w), room);
  switch (b.kind) {
    case "text": text(s, x, y, w, h, b.lines, { size: b.size || 20, color: color(b.color, K.ink), bold: b.bold, gap: b.gap, align: b.align }); return h;
    case "table": return table(s, x, y, w, b);
    case "code": codeWindow(s, x, y, w, h, codeLines(b.lines), { label: b.label, size: b.size }); return h;
    case "http": codeWindow(s, x, y, w, h, httpLines(b.file, b.cmd, b.keep), { label: b.label, size: b.size }); return h;
    case "inline": card(s, x, y, w, h, K.card, "code-inline");
      text(s, x + 0.25, y, w - 0.5, h, [[[b.text, { mono: b.mono !== false, size: b.size || 16, color: b.color || "coralText" }]]], { valign: "middle", gap: 0, line: 1.0 }); return h;
    case "cards": {
      const n = b.items.length, cw = (w - GAP * (n - 1)) / n;
      b.items.forEach((it, i) => {
        const cx = x + i * (cw + GAP);
        card(s, cx, y, cw, h, it.fill === "dark" ? K.dark : K.card);
        const dark = it.fill === "dark";
        const lines = [];
        if (it.kicker) lines.push([[it.kicker, { size: 15, color: it.kickerColor || (dark ? "onDarkSoft" : "muted") }]]);
        if (it.title) lines.push([[it.title, { size: it.titleSize || 22, bold: it.bold !== false, color: dark ? "onDark" : "ink" }]]);
        if (it.code) lines.push([[it.code, { mono: true, size: it.codeSize || 14, color: dark ? "amber" : "coralText" }]]);
        (it.body || []).forEach((l) => lines.push(typeof l === "string" ? [[l, { size: it.bodySize || 15, color: dark ? "onDarkSoft" : "body" }]] : l));
        text(s, cx + 0.3, y + 0.25, cw - 0.6, h - 0.4, lines, { gap: 5 });
      });
      return h;
    }
    case "callout": card(s, x, y, w, h, K.coral, "callout-coral");
      text(s, x + 0.4, y, w - 0.8, h, [[[b.text, { size: b.size || 22, bold: true, color: "ink" }]]], { valign: "middle" }); return h;
    case "chart": chart(s, x, y, w, h, b); return h;
    case "image": return imageCols(s, rel(b.path), b.cuts, x, y, w, Math.min(b.h || room, room));
    case "badge": badge(s, x, y, b.text); return 0.34;
    case "row": {
      const n = b.cols.length, ratios = b.widths || b.cols.map(() => 1), sum = ratios.reduce((a, c) => a + c, 0);
      let cx = x, used = 0;
      for (let i = 0; i < n; i++) {
        const cw = (w - GAP * (n - 1)) * (ratios[i] / sum);
        // 옆 칸끼리 높이를 맞춘다 (가장 큰 칸 기준)
        const col = { ...b.cols[i], h: b.cols[i].h || b.h || estimate(b, w) };
        used = Math.max(used, await place(s, col, cx, y, cw, room));
        cx += cw + GAP;
      }
      return used;
    }
    default: throw new Error(`알 수 없는 블록 종류: ${b.kind}`);
  }
}

// ------------------------------------------------------------------ 슬라이드
const NOTES = [];   // { title, notes, screen, spare }
const WARN = [];
async function addContent(sl, n, sectionTitle, spare) {
  const s = pres.addSlide({ masterName: "본문", sectionTitle });
  s.addText(sl.eyebrow || (spare ? "APPENDIX" : ""), { placeholder: "eyebrow" });
  s.addText(sl.title, { placeholder: "title" });
  if (sl.badge) badge(s, X + W - (0.3 + [...sl.badge].reduce((a, ch) => a + (/[ㄱ-힝]/.test(ch) ? 0.17 : 0.09), 0)), 0.42, sl.badge);
  let y = Y0;
  for (const b of sl.blocks || []) {
    if (estimate(b, W) > BOTTOM - y + 0.02) WARN.push(`${n}번 '${sl.title}': '${b.kind}' 블록이 남은 높이(${(BOTTOM - y).toFixed(2)}in)보다 커서 줄여 그렸습니다. 블록을 줄이거나 슬라이드를 나누세요.`);
    const used = await place(s, b, X, y, W, BOTTOM - y);
    y += used + (b.gapAfter ?? GAP);
  }
  if (y - GAP > BOTTOM + 0.02) WARN.push(`${n}번 '${sl.title}': 내용이 아래 여백(7.0in)을 넘습니다 (y=${(y - GAP).toFixed(2)}). 블록을 줄이거나 나누세요.`);
  return s;
}
async function build() {
  const all = [...(SPEC.slides || []).map((x) => [x, false]), ...(SPEC.spare || []).map((x) => [x, true])];
  let section = null, n = 0;
  for (const [sl, spare] of all) {
    n++;
    const sec = spare ? (SPEC.spareTitle || "예비 (질문이 나오면)") : (sl.section || (sl.type === "section" ? sl.title : section) || "본문");
    if (sec !== section) { pres.addSection({ title: sec }); section = sec; }
    let s;
    if (sl.type === "cover") {
      const wide = !sl.terminal;
      s = pres.addSlide({ masterName: wide ? "표지-넓게" : "표지", sectionTitle: section });
      s.addText(sl.title, { placeholder: "title" });
      if (sl.subtitle) s.addText(sl.subtitle, { placeholder: "body" });
      if (sl.meta) s.addText(sl.meta, { placeholder: "meta" });
      if (sl.terminal) codeWindow(s, 7.55, 2.45, 5.07, 2.6, codeLines(sl.terminal), { label: sl.terminalLabel || "터미널", size: 15 });
    } else if (sl.type === "section") {
      s = pres.addSlide({ masterName: "섹션", sectionTitle: section });
      s.addText(sl.num || "", { placeholder: "num" });
      s.addText(sl.title, { placeholder: "title" });
      if (sl.desc) s.addText(sl.desc, { placeholder: "body" });
    } else if (sl.type === "closing") {
      s = pres.addSlide({ masterName: "마무리", sectionTitle: section });
      s.addText(sl.title || "정리", { placeholder: "title" });
      (sl.rows || []).forEach(([k, v], i) => {
        const y = Y0 + i * 0.68;
        text(s, X, y, 2.4, 0.5, [[[k, { size: 20, color: "coral" }]]]);
        text(s, X + 2.5, y, W - 2.5, 0.5, [[[v, { size: 20, color: "onDark" }]]]);
      });
      if ((sl.rows || []).length > 7) WARN.push(`${n}번 마무리: 줄이 ${sl.rows.length}개입니다. 7개 이하를 권장합니다.`);
    } else {
      s = await addContent(sl, n, section, spare);
    }
    if (!sl.notes) WARN.push(`${n}번 '${sl.title}': 발표자 노트(notes)가 없습니다.`);
    s.addNotes(sl.notes || "");
    NOTES.push({ title: sl.type === "section" ? `[섹션] ${sl.title}` : sl.title, notes: sl.notes || "", screen: sl.screen || "", spare });
  }
}

// ------------------------------------------------------------------ 테마 색 · 한글 글꼴 쓰기
// pptxgenjs는 테마 색을 Office 기본값으로 두고 한글(ea) 글꼴 칸을 비워 둔다. 둘 다 채워야 한글 제목 · 본문이 테마 글꼴을 따른다.
async function patchTheme(file) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  for (const name of Object.keys(zip.files).filter((x) => /^ppt\/theme\/theme\d+\.xml$/.test(x))) {
    let xml = await zip.file(name).async("string");
    for (const [slot, hex] of Object.entries(THEME.colors)) xml = xml.replace(new RegExp(`(<a:${slot}>)[\\s\\S]*?(</a:${slot}>)`), `$1<a:srgbClr val="${hex}"/>$2`);
    const safe = THEME.name.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
    xml = xml.replace(/(<a:(?:theme|clrScheme|fontScheme)\b[^>]*?\bname=")[^"]*"/g, `$1${safe}"`);
    const fontBlock = (tag, face) => {
      xml = xml.replace(new RegExp(`<a:${tag}>([\\s\\S]*?)</a:${tag}>`), (m, inner) => {
        inner = inner.replace(/<a:ea typeface="[^"]*"\/>/, `<a:ea typeface="${face}"/>`).replace(/<a:font script="Hang" typeface="[^"]*"\/>/, `<a:font script="Hang" typeface="${face}"/>`);
        if (!/script="Hang"/.test(inner)) inner += `<a:font script="Hang" typeface="${face}"/>`;
        return `<a:${tag}>${inner}</a:${tag}>`;
      });
    };
    fontBlock("majorFont", FONTS.head);
    fontBlock("minorFont", FONTS.body);
    zip.file(name, xml);
  }
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

// ------------------------------------------------------------------ 대본
function script(file) {
  const cps = SPEC.charsPerSecond || 5.5;                       // 한국어 발표 속도(공백 포함 글자/초) 어림
  const secs = (t) => Math.max(5, Math.round(t.length / cps / 5) * 5);
  const mm = (t) => `${Math.floor(t / 60)}:${String(t % 60).padStart(2, "0")}`;
  const main = NOTES.filter((x) => !x.spare), spare = NOTES.filter((x) => x.spare);
  const total = main.reduce((a, x) => a + secs(x.notes), 0);
  const L = [`# ${SPEC.title || "발표"} — 대본`, ""];
  if (SPEC.meta) Object.entries(SPEC.meta).forEach(([k, v]) => L.push(`- ${k}: ${v}`));
  L.push(`- 발표 파일: \`${path.basename(OUT)}\` (발표자 노트에 아래 대사가 그대로 들어 있다)`, "",
         "## 시간 배분 (대사 길이로 어림)", "", "| # | 슬라이드 | 시간 | 누적 |", "|---|---|---|---|");
  let t = 0;
  main.forEach((x, i) => { t += secs(x.notes); L.push(`| ${i + 1} | ${x.title} | ${mm(secs(x.notes))} | ${mm(t)} |`); });
  L.push("", `> 합계 약 ${Math.floor(total / 60)}분 ${total % 60}초. 섹션 슬라이드는 한 문장만 하고 넘긴다.`, "", "---", "");
  main.forEach((x, i) => { L.push(`## ${i + 1}. ${x.title} (${mm(secs(x.notes))})`, ""); if (x.screen) L.push(`*화면: ${x.screen}*`, ""); L.push(`> ${x.notes}`, "", "---", ""); });
  if (spare.length) {
    L.push("## 예비 슬라이드 (맨 뒤, 질문이 나오면)", "");
    spare.forEach((x, i) => L.push(`### ${main.length + i + 1}. ${x.title}`, "", ...(x.screen ? [`*${x.screen}*`, ""] : []), `> ${x.notes}`, ""));
  }
  if (SPEC.qa && SPEC.qa.length) L.push("## 질문 대비", "", "| 질문 | 짧은 답 |", "|---|---|", ...SPEC.qa.map(([q, a]) => `| ${q} | ${a} |`), "");
  L.push("## 발표 전 체크", "", `- [ ] 발표 PC에 ${FONTS.head} · ${FONTS.body} · ${FONTS.mono} 가 있는지 확인 (없으면 설치하거나 파일 › 옵션 › 저장 › 파일의 글꼴 포함)`,
         "- [ ] 발표자 보기로 노트를 보며 한 번, 노트 없이 한 번 리허설해서 시간을 잰다", "");
  fs.writeFileSync(file, L.join("\n"));
  return total;
}

(async () => {
  await build();
  await pres.writeFile({ fileName: OUT });
  await patchTheme(OUT);
  const total = SCRIPT ? script(SCRIPT) : 0;
  const main = NOTES.filter((x) => !x.spare).length;
  console.log(`덱: ${OUT}`);
  if (SCRIPT) console.log(`대본: ${SCRIPT} (본 ${main}장 + 예비 ${NOTES.length - main}장, 약 ${Math.floor(total / 60)}분 ${total % 60}초)`);
  WARN.forEach((w) => console.warn("경고: " + w));
})().catch((e) => { console.error(e); process.exit(1); });
