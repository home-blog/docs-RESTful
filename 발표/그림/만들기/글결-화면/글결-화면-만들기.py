"""글결 프로젝트의 API 문서(md 내보내기)를 Asciidoctor 원본(.adoc)으로 되돌린다.

- 원본/글결-REST-Docs.md → build/src/docs/asciidoc/index.adoc (REST Docs 전체 문서)
- 슬라이드에 넣을 부분만 골라 build/src/docs/asciidoc/발췌-*.adoc 로 만든다.
그다음 pom.xml 로 HTML을 만들고, 글결-화면-찍기.js 로 PNG를 찍는다.
"""
import os, re, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "build", "src", "docs", "asciidoc")
MD = open(os.path.join(HERE, "원본", "글결-REST-Docs.md"), encoding="utf-8").read().splitlines()

HEAD = re.compile(r"^(#{1,6}) (?:\[(.+?)\]\(#(.+?)\)|(.+))$")


def inline(s):
    s = s.replace("\\~", "~").replace("\\`", "`")
    s = re.sub(r"\[([^\]]+)\]\(#([^)]+)\)", r"<<\2,\1>>", s)
    s = re.sub(r"`([^`]+)`", lambda m: "``+" + m.group(1) + "+``", s)
    return s


def parse():
    """md를 (레벨, 앵커, 제목, 본문 줄들) 덩어리로 나눈다."""
    blocks, cur = [], None
    for line in MD:
        m = HEAD.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2) or m.group(4)
            cur = dict(level=level, anchor=m.group(3), title=title, body=[])
            blocks.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    return blocks


BLOCKS = parse()
BY = {b["anchor"]: b for b in BLOCKS if b["anchor"]}


def trim_http(lines, mode):
    """mode: full | nohdr(머리글 빼기) | line(첫 줄만)"""
    if mode == "full":
        return lines
    out, i = [lines[0]], 1
    if lines[0].startswith("$ curl"):
        out = [lines[0].rstrip(" \\")]
        if mode == "line":
            return out
        for l in lines[1:]:
            if l.strip().startswith(("-H 'X-XSRF", "--cookie", "-H 'Content-Type")):
                continue
            out.append(l)
        out[0] = lines[0]
        return out
    while i < len(lines) and lines[i].strip():
        i += 1
    if mode == "line":
        return out
    return out + lines[i:]


def cut_after_first_item(lines, key):
    """JSON 배열 key의 첫 항목만 남기고 나머지는 … 로 줄인다."""
    out, inside, depth = [], False, 0
    for l in lines:
        if not inside:
            out.append(l)
            if f'"{key}" : [' in l:
                inside = True
                depth = 0
            continue
        out.append(l)
        depth += l.count("{") - l.count("}")
        if depth <= 0 and l.strip().startswith("}"):
            out[-1] = l[: len(l) - len(l.lstrip())] + "}, … ]"
            out.append("}")
            return out
    return out


def body_to_adoc(lines, opts):
    out, i, pending_title = [], 0, None
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            lang = l[3:].strip() or "text"
            j = i + 1
            code = []
            while not lines[j].startswith("```"):
                code.append(lines[j])
                j += 1
            code = trim_http(code, opts.get("http", "full"))
            if opts.get("first_item"):
                code = cut_after_first_item(code, opts["first_item"])
            out += [f'[source,{lang},options="nowrap"]', "----", *code, "----", ""]
            i = j + 1
            continue
        if l.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split(" | ")]
                rows.append(cells)
                i += 1
            head, data = rows[0], [r for r in rows[2:]]
            if opts.get("rows"):
                data = [r for r in data if r[0].strip("`") in opts["rows"]]
            n = len(head)
            cols = {2: "1,3", 3: "2,1,4"}.get(n, ",".join(["1"] * n))
            if pending_title:
                out.append("." + pending_title)
                pending_title = None
            out += [f'[cols="{cols}",options="header"]', "|==="]
            out.append("|" + "|".join(inline(c) for c in head))
            for r in data:
                out.append("")
                out += ["|" + inline(c) for c in r]
            out += ["|===", ""]
            continue
        if l.startswith("Table 1. "):
            pending_title = "``+" + l[len("Table 1. "):] + "+``"
            i += 1
            continue
        if l.strip() == "차례" or re.match(r"^\s*- \[", l) or l.startswith("Last updated"):
            i += 1
            continue
        out.append(inline(l))
        i += 1
    return out


def section(b, level, opts, heading=True):
    out = []
    if heading:
        out += [f"[[{b['anchor']}]]", "=" * level + " " + b["title"], ""]
    if not opts.get("no_body"):
        out += body_to_adoc(b["body"], opts)
    return out


def full_doc():
    out = ["= 글결 API 문서", ":doctype: book", ":toc: left", ":toc-title: 차례", ":toclevels: 2",
           ":sectlinks:", ":source-highlighter: rouge", ":last-update-label: Last updated", ""]
    for b in BLOCKS:
        if b["level"] == 1:
            out += body_to_adoc(b["body"], {})
        else:
            out += section(b, b["level"], {})
    return out


# 슬라이드별 발췌: (앵커, 선택). "!" 로 시작하면 제목 없이 본문만.
EXCERPTS = {
    "01-오류-상태-코드": [("_오류", {})],
    "02-오류-응답": [
        ("error-validation", {}), ("!error-validation_http_response", {"http": "nohdr"}),
        ("!error-validation_response_fields", {}),
        ("error-not-found", {"no_body": True}), ("!error-not-found_http_response", {"http": "nohdr"}),
    ],
}


def excerpt(items):
    out = [":nofooter:", ":source-highlighter: rouge", ""]
    for name, opts in items:
        heading = not name.startswith("!")
        b = BY[name.lstrip("!")]
        if opts.get("rows"):
            opts = dict(opts, rows=[r for r in opts["rows"]])
        out += section(b, 2 if b["level"] <= 3 else 3, opts, heading)
    return out


def api_page():
    """원본/글결-API.md (springdoc OpenAPI 문서 페이지)를 같은 글로 HTML 한 장으로 만든다.
    md에 API 목록 칸은 들어 있지 않아(화면에서 그려짐) 약속 부분까지만 만든다."""
    import html as H
    lines = open(os.path.join(HERE, "원본", "글결-API.md"), encoding="utf-8").read().splitlines()
    code = lambda s: re.sub(r"`([^`]+)`", r"<code>\1</code>", H.escape(s))
    bold = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    out, i, cards = [], 0, False
    title = lines[0].strip()
    while i < len(lines):
        l = lines[i]
        if l.startswith("## "):
            if cards:
                out.append("</div>")
                cards = False
            if l[3:].strip() == "API 목록":
                out.append('<h2>API 목록</h2><div class="search"><span class="box">찾기</span>'
                           '<span class="tag">🔒 로그인 세션 쿠키가 있어야 부를 수 있음</span>'
                           '<span class="tag">🛡 CSRF 머리글에 CSRF 토큰을 실음</span></div>')
                i += 1
                while i < len(lines) and not lines[i].startswith("코드 저장소"):
                    i += 1
                continue
            out.append(f"<h2>{H.escape(l[3:])}</h2>")
            if "약속" in l:
                out.append('<div class="cards">')
                cards = True
        elif l.startswith("### "):
            if cards and out[-1] != '<div class="cards">':
                out.append("</section>")
            out.append(f'<section class="card"><h3>{H.escape(l[4:])}</h3>')
        elif l.startswith("```"):
            j = i + 1
            while not lines[j].startswith("```"):
                j += 1
            out.append("<pre>" + H.escape("\n".join(lines[i + 1:j])) + "</pre>")
            i = j
        elif l.strip() and i > 0:
            out.append(f"<p>{bold(code(l))}</p>")
        i += 1
        if cards and i < len(lines) and lines[i].startswith("## "):
            out.append("</section>")
    css = """body{margin:0;background:#f6f7f9;color:#1f2430;font-family:'Noto Sans KR',sans-serif}
main{max-width:1180px;margin:0 auto;padding:36px 40px 28px}
h1{font-size:34px;margin:0 0 10px;letter-spacing:-.5px}h1 span{color:#0d7468}
main>p{color:#4a5262;font-size:16px;line-height:1.7;margin:0 0 6px}
h2{font-size:21px;margin:30px 0 14px}
.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
.card{min-width:0;background:#fff;border:1px solid #dfe3e9;border-radius:12px;padding:16px 20px}
.card h3{font-size:16px;margin:0 0 8px;color:#0d7468}.card p{font-size:14.5px;line-height:1.7;margin:0 0 6px;color:#333a46}
code{font-family:'JetBrains Mono',monospace;font-size:13px;background:#eef1f4;border-radius:4px;padding:1px 5px}
pre{font-family:'JetBrains Mono',monospace;font-size:12.5px;white-space:pre-wrap!important;background:#1f2430;color:#e6eaf0;border-radius:8px;padding:12px 14px;margin:8px 0 0;white-space:pre}
.search{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.box{flex:1;min-width:240px;background:#fff;border:1px solid #cdd3dc;border-radius:8px;padding:9px 14px;color:#8a92a0;font-size:14px}
.tag{font-size:13px;background:#fff;border:1px solid #dfe3e9;border-radius:999px;padding:6px 12px;color:#4a5262}
.note{font-size:14px;color:#4a5262;margin-top:16px}"""
    name, _, rest = title.partition(".")
    body = "\n".join(out).replace("<p>코드 저장소", '<p class="note">코드 저장소')
    page = (f'<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>{H.escape(title)}</title>'
            f'<style>{css}</style></head><body><main><h1>{H.escape(name)}.<span>{H.escape(rest)}</span></h1>\n{body}</main></body></html>')
    os.makedirs(os.path.join(HERE, "build", "html"), exist_ok=True)
    open(os.path.join(HERE, "build", "html", "글결-API.html"), "w", encoding="utf-8").write(page)


if __name__ == "__main__":
    shutil.rmtree(SRC, ignore_errors=True)
    os.makedirs(SRC)
    open(os.path.join(SRC, "index.adoc"), "w", encoding="utf-8").write("\n".join(full_doc()) + "\n")
    for name, items in EXCERPTS.items():
        open(os.path.join(SRC, f"발췌-{name}.adoc"), "w", encoding="utf-8").write("\n".join(excerpt(items)) + "\n")
    api_page()
    print("adoc", len(EXCERPTS) + 1)
