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


def _code(block):
    """덩어리 본문에서 첫 코드 블록의 줄들"""
    if not block:
        return []
    body, out, inside = block["body"], [], False
    for l in body:
        if l.startswith("```"):
            if inside:
                return out
            inside = True
            continue
        if inside:
            out.append(l)
    return out


def _table(block):
    rows = [l for l in (block or {"body": []})["body"] if l.startswith("|")]
    clean = lambda c: c.strip().strip("`").replace("\\~", "~").replace("\\`", "`")
    return [[clean(c) for c in r.strip().strip("|").split(" | ")] for r in rows[2:]]


def _json_after_blank(lines):
    import json
    if "" not in lines:
        return None
    text = "\n".join(lines[lines.index("") + 1:]).strip()
    try:
        return json.loads(text) if text else None
    except ValueError:
        return None


TYPES = {"String": "string", "Number": "integer", "Boolean": "boolean", "Array": "array", "Object": "object"}


def _schema(rows):
    root = {"type": "object", "properties": {}}
    for path, typ, desc in rows:
        node = root
        parts = path.split(".")
        for k, part in enumerate(parts):
            arr = part.endswith("[]")
            name = part[:-2] if arr else part
            last = k == len(parts) - 1
            props = node.setdefault("properties", {})
            if last and not (arr and typ == "Array" and False):
                if arr:
                    cur = props.setdefault(name, {"type": "array", "items": {"type": "string"}})
                    cur["description"] = desc
                    if typ != "Array":
                        cur["items"] = {"type": TYPES.get(typ, "string")}
                else:
                    cur = props.setdefault(name, {})
                    cur.update({"type": TYPES.get(typ, "string"), "description": desc})
            else:
                if arr:
                    cur = props.setdefault(name, {"type": "array", "items": {"type": "object", "properties": {}}})
                    cur["items"] = cur.get("items") if cur.get("items", {}).get("type") == "object" else {"type": "object", "properties": {}}
                    node = cur["items"]
                else:
                    cur = props.setdefault(name, {"type": "object", "properties": {}})
                    cur.setdefault("properties", {})
                    cur["type"] = "object"
                    node = cur
    return root


def openapi():
    """REST Docs에 적힌 API로 OpenAPI 명세를 만든다 (Swagger UI 화면용). 61개 중 문서에 실린 것만."""
    import json
    spec = {"openapi": "3.0.1",
            "info": {"title": "글결 API", "version": "0.5.2",
                     "description": "여러 사람이 각자 블로그를 쓰고 한곳에서 둘러보는 멀티 블로그 서비스 **글결**의 서버 API입니다."},
            "servers": [{"url": "https://geulgyeol.java21.net", "description": "개발 서버"}],
            "tags": [], "paths": {}}
    group = None
    extra = {"post-create": ("400", "error-validation"), "post-read": ("404", "error-not-found")}
    for b in BLOCKS:
        if b["level"] == 2:
            title = re.sub(r"^\d+\.\s*", "", b["title"])
            group = None if b["anchor"] in ("overview", "errors") else title
            if group:
                desc = " ".join(l for l in b["body"] if l.strip())
                spec["tags"].append({"name": group, **({"description": desc} if desc else {})})
            continue
        if b["level"] != 3 or not group:
            continue
        a = b["anchor"]
        req = _code(BY.get(a + "_http_request")) or _code(BY.get(a + "_curl_request"))
        if req[0].startswith("$ curl"):
            m = re.search(r"'https?://[^/]+([^']+)'.*-X (\w+)", req[0])
            path, method = m.group(1), m.group(2)
            body = re.search(r"-d '(.*)'", "\n".join(req), re.S)
            body = json.loads(body.group(1)) if body else None
        else:
            method, path = req[0].split()[:2]
            body = _json_after_blank(req)
        tpl = next((l[len("Table 1. "):] for l in (BY.get(a + "_path_parameters") or {"body": []})["body"] if l.startswith("Table 1. ")), path.split("?")[0])
        op = {"tags": [group], "summary": re.sub(r"^[\d.]+\s*", "", b["title"]), "operationId": a}
        desc = " ".join(l for l in b["body"] if l.strip())
        if desc:
            op["description"] = desc
        params = []
        for name, d in _table(BY.get(a + "_path_parameters")):
            params.append({"name": name, "in": "path", "required": True, "description": d, "schema": {"type": "integer"}})
        for name, d in _table(BY.get(a + "_query_parameters")):
            params.append({"name": name, "in": "query", "required": name == "q", "description": d,
                           "schema": {"type": "integer" if name in ("page", "categoryId") else "string"}})
        for name, d in _table(BY.get(a + "_request_headers")):
            params.append({"name": name, "in": "header", "required": True, "description": d, "schema": {"type": "string"}})
        if params:
            op["parameters"] = params
        rf = _table(BY.get(a + "_request_fields"))
        if rf:
            op["requestBody"] = {"required": True, "content": {"application/json": {"schema": _schema(rf), **({"example": body} if body else {})}}}
        res = _code(BY.get(a + "_http_response"))
        if not res and BY.get(a + "_curl_request"):
            res = []
        code, reason = (res[0].split()[1], " ".join(res[0].split()[2:])) if res else ("200", "OK")
        r = {"description": reason}
        rs = _table(BY.get(a + "_response_fields"))
        ex = _json_after_blank(res) if res else None
        if rs or ex is not None:
            r["content"] = {"application/json": {**({"schema": _schema(rs)} if rs else {}), **({"example": ex} if ex is not None else {})}}
        op["responses"] = {code: r}
        if a in extra:
            c, e = extra[a]
            er = _code(BY.get(e + "_http_response"))
            op["responses"][c] = {"description": re.sub(r"^[\d.]+\s*", "", BY[e]["title"]),
                                  "content": {"application/json": {"schema": _schema(_table(BY.get(e + "_response_fields"))), "example": _json_after_blank(er)}}}
        spec["paths"].setdefault(tpl, {})[method.lower()] = op
    return spec


def swagger_page():
    import json
    out = os.path.join(HERE, "build", "html", "swagger")
    os.makedirs(out, exist_ok=True)
    dist = os.path.join(HERE, "node_modules", "swagger-ui-dist")
    for f in ("swagger-ui.css", "swagger-ui-bundle.js"):
        shutil.copy(os.path.join(dist, f), out)
    spec = openapi()
    open(os.path.join(out, "openapi.json"), "w", encoding="utf-8").write(json.dumps(spec, ensure_ascii=False, indent=1))
    open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<title>Swagger UI</title><link rel="stylesheet" href="swagger-ui.css">
<style>body{{margin:0}} .swagger-ui, .swagger-ui .info .title, .swagger-ui .opblock-tag {{font-family:'Noto Sans KR',sans-serif}}</style></head>
<body><div id="swagger-ui"></div><script src="swagger-ui-bundle.js"></script>
<script>window.ui = SwaggerUIBundle({{spec: {json.dumps(spec, ensure_ascii=False)}, dom_id: '#swagger-ui', docExpansion: 'list',
  defaultModelsExpandDepth: -1, tryItOutEnabled: false, deepLinking: true}});</script></body></html>""")
    return len([1 for p in spec["paths"].values() for _ in p])


if __name__ == "__main__":
    shutil.rmtree(SRC, ignore_errors=True)
    os.makedirs(SRC)
    open(os.path.join(SRC, "index.adoc"), "w", encoding="utf-8").write("\n".join(full_doc()) + "\n")
    for name, items in EXCERPTS.items():
        open(os.path.join(SRC, f"발췌-{name}.adoc"), "w", encoding="utf-8").write("\n".join(excerpt(items)) + "\n")
    print("swagger api", swagger_page())
    print("adoc", len(EXCERPTS) + 1)
