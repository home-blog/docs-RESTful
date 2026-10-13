"""발표용 그림(SVG) 생성기. 결과는 저장소의 발표/그림/ 에 쓴다."""
import html, os, sys

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.makedirs(OUT, exist_ok=True)

FONT = "'Noto Sans KR','Malgun Gothic','Apple SD Gothic Neo',sans-serif"
MONO = "'JetBrains Mono','D2Coding',Consolas,'Noto Sans KR',monospace"
C = dict(
    ink="#1C2230", muted="#5A6474", line="#B4BCC8", faint="#E3E7ED", soft="#F4F6F9", white="#FFFFFF",
    blue="#2459C2", blueBg="#EAF0FB", teal="#0D7468", tealBg="#E2F2EF",
    violet="#5B45B8", violetBg="#EEEAFA", green="#1B7F3B", greenBg="#E5F3E9",
    orange="#B55400", orangeBg="#FCEFE0", red="#BF2A20", redBg="#FBE8E6",
)
MARKERS = ["ink", "muted", "blue", "teal", "violet", "green", "orange", "red"]


def esc(s):
    return html.escape(s, quote=True)


def tw(s, size, mono=False):
    w = 0.0
    for ch in s:
        if ord(ch) >= 0x1100:
            w += size * 1.0
        else:
            w += size * (0.6 if mono else 0.56)
    return w


class Fig:
    def __init__(self, name, title, w, h, claim, oy=0):
        self.name, self.title, self.w, self.h, self.claim, self.oy = name, title, w, h, claim, oy
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def rect(self, x, y, w, h, stroke="line", fill="white", rx=14, sw=2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{C[fill]}" stroke="{C[stroke]}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=20, weight=400, fill="ink", anchor="middle", mono=False):
        fam = MONO if mono else FONT
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" font-weight="{weight}" fill="{C[fill]}" text-anchor="{anchor}" xml:space="preserve">{esc(s)}</text>')

    def rich(self, x, y, spans, size=20, anchor="start"):
        """spans: (text, color, weight, mono)"""
        out = []
        for sp in spans:
            t, col = sp[0], sp[1]
            wt = sp[2] if len(sp) > 2 else 400
            mono = sp[3] if len(sp) > 3 else False
            fam = MONO if mono else FONT
            out.append(f'<tspan font-family="{fam}" font-weight="{wt}" fill="{C[col]}">{esc(t)}</tspan>')
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" xml:space="preserve">{"".join(out)}</text>')

    def path(self, pts, color="muted", arrow=True, dash=None, sw=2.5):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        m = f' marker-end="url(#ah-{color})"' if arrow else ""
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="none" stroke="{C[color]}" stroke-width="{sw}" stroke-linejoin="round"{da}{m}/>')

    def pill(self, cx, cy, s, color, size=16, weight=600, pad=12, fill="white"):
        w = tw(s, size) + pad * 2
        self.rect(cx - w / 2, cy - size * 0.95, w, size * 1.9, color, fill, rx=size * 0.95, sw=1.5)
        self.text(cx, cy + size * 0.36, s, size, weight, color)

    def xmark(self, cx, cy, r=16):
        self.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{C["redBg"]}" stroke="{C["red"]}" stroke-width="2"/>')
        k = r * 0.45
        self.add(f'<path d="M{cx-k},{cy-k} L{cx+k},{cy+k} M{cx+k},{cy-k} L{cx-k},{cy+k}" stroke="{C["red"]}" stroke-width="3" stroke-linecap="round"/>')

    def svg(self):
        defs = "".join(
            f'<marker id="ah-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="12" markerHeight="12" '
            f'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{C[c]}"/></marker>'
            for c in MARKERS
        )
        body = "\n".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {self.oy} {self.w} {self.h-self.oy}" width="{self.w}" height="{self.h-self.oy}" '
            f'role="img" aria-label="{esc(self.claim)}">\n<title>{esc(self.title)}</title>\n<defs>{defs}</defs>\n'
            f'<rect x="0" y="{self.oy}" width="{self.w}" height="{self.h-self.oy}" rx="18" fill="{C["white"]}"/>\n{body}\n</svg>\n'
        )


FIGS = []


def fig(*a, **k):
    f = Fig(*a, **k)
    FIGS.append(f)
    return f


# ---------------------------------------------------------------- 00 왜 요청을 보내나
f = fig("00-왜-요청을-보내나", "왜 요청을 보내나", 1240, 600,
        "화면에 보이는 데이터는 서버의 DB에 있으므로, 사용자의 동작 하나하나가 서버로 보내는 HTTP 요청 하나가 된다.")
for x, t in [(40, "사용자가 화면에서 하는 일"), (420, "클라이언트가 보내는 요청"), (800, "서버가 하는 일 → 응답")]:
    f.text(x, 46, t, 16, 700, "muted", "start")
IR = [
    ("블로그 첫 화면을 연다", "GET", "/api/v1/posts", "DB에서 글 목록 조회", "200 + 글 목록"),
    ("42번 글을 누른다", "GET", "/api/v1/posts/42", "42번 글 조회", "200 + 글 내용"),
    ("글을 쓰고 저장한다", "POST", "/api/v1/posts", "DB에 새 글 저장", "201 + 새 글 주소"),
    ("내 글을 삭제한다", "DELETE", "/api/v1/posts/42", "DB에서 42번 글 삭제", "204"),
]
for i, (act, m, url, work, res) in enumerate(IR):
    y = 72 + i * 96
    cy = y + 36
    f.rect(40, y, 320, 72, "blue", "blueBg", rx=12)
    f.text(60, cy + 7, act, 19, 600, "ink", "start")
    f.path([(362, cy), (414, cy)], "blue")
    f.rect(420, y, 330, 72, "line", "white", rx=12)
    f.rich(440, cy + 7, [(m, "blue", 700, True), (" " + url, "ink", 500, True)], 18)
    f.path([(752, cy), (794, cy)], "teal")
    f.rect(800, y, 400, 72, "teal", "tealBg", rx=12)
    f.text(820, cy + 7, work, 17, 500, "ink", "start")
    f.text(1180, cy + 7, res, 16, 700, "green", "end", True)
f.rect(40, 470, 1160, 100, "faint", "soft", rx=14)
f.text(620, 510, "화면에 보이는 글 · 댓글 · 회원 정보는 사용자 기기가 아니라 서버의 DB에 있다", 19, 700, "ink")
f.text(620, 544, "그래서 화면은 데이터가 필요할 때마다 서버에 요청을 보내 데이터를 받아 오거나 바꾼다", 17, 400, "muted")

# ---------------------------------------------------------------- 00b 여러 클라이언트가 같은 API를 쓴다
f = fig("00b-여러-클라이언트가-같은-API를-쓴다", "여러 클라이언트가 같은 API를 쓴다", 1240, 590,
        "웹, 모바일 앱, 관리자 페이지, 다른 서비스가 모두 같은 API 서버를 호출하므로, 누구나 예측할 수 있는 공통 규칙이 필요하다.")
CL = [("웹 브라우저", "React · Vue"), ("모바일 앱", "iOS · Android"), ("관리자 페이지", "운영팀이 쓰는 화면"), ("다른 서비스", "외부 파트너 · 사내 시스템")]
for i, (n, sub) in enumerate(CL):
    y = 40 + i * 104
    f.rect(40, y, 270, 82, "blue", "blueBg", rx=12)
    f.text(175, y + 36, n, 19, 700, "blue")
    f.text(175, y + 62, sub, 14, 400, "muted")
    f.path([(312, y + 41), (420, y + 41), (420, 245), (496, 245)] if i < 2 else [(312, y + 41), (420, y + 41), (420, 245)], "blue", arrow=(i == 0), sw=2.5)
f.path([(420, 245), (496, 245)], "blue")
f.text(430, 228, "HTTP 요청", 14, 700, "blue", "start")
f.rect(500, 130, 320, 230, "teal", "tealBg")
f.text(660, 172, "API 서버", 22, 700, "teal")
f.text(660, 198, "하나의 API를 모두에게 제공", 14, 400, "muted")
for k, t in enumerate(["GET    /api/v1/posts", "POST   /api/v1/posts", "GET    /api/v1/posts/42", "DELETE /api/v1/posts/42"]):
    f.text(530, 238 + k * 28, t, 14, 500, "ink", "start", True)
f.path([(822, 245), (936, 245)], "violet")
f.rect(940, 175, 250, 140, "violet", "violetBg")
f.text(1065, 236, "DB", 22, 700, "violet")
f.text(1065, 266, "글 · 댓글 · 회원", 15, 400, "muted")
f.rect(40, 470, 1150, 96, "ink", "white", rx=14)
f.text(615, 508, "API를 만드는 사람과 쓰는 사람이 다르다", 19, 700, "ink")
f.rich(615, 542, [("그래서 문서를 일일이 묻지 않아도 예측할 수 있는 공통 규칙이 필요하다  →  ", "muted", 400), ("REST", "teal", 700)], 17, "middle")

# ---------------------------------------------------------------- 01 클라이언트와 서버
f = fig("01-클라이언트와-서버", "클라이언트와 서버", 1200, 530,
        "클라이언트는 요청을 보내고, 서버가 DB를 다룬 뒤 응답한다. 클라이언트는 DB를 직접 열지 않는다.", oy=95)
f.rect(40, 150, 220, 200, "blue", "blueBg")
f.text(150, 222, "클라이언트", 28, 700, "blue")
f.text(150, 258, "브라우저 · 앱", 19, 400, "muted")
f.text(150, 305, "요청을 보낸다", 19, 500)
f.rect(520, 150, 240, 200, "teal", "tealBg")
f.text(640, 222, "서버", 28, 700, "teal")
f.text(640, 258, "Spring Boot", 19, 400, "muted")
f.text(640, 305, "요청을 처리한다", 19, 500)
f.add(f'<rect x="508" y="168" width="14" height="164" rx="5" fill="{C["teal"]}"/>')
f.text(515, 132, "API", 18, 700, "teal")
f.rect(940, 150, 220, 200, "violet", "violetBg")
f.text(1050, 222, "데이터베이스", 26, 700, "violet")
f.text(1050, 258, "글 · 댓글 · 회원", 19, 400, "muted")
f.text(1050, 305, "데이터를 저장한다", 19, 500)
f.path([(262, 215), (504, 215)], "blue")
f.text(383, 198, "① 요청", 18, 600, "blue")
f.path([(506, 290), (264, 290)], "teal")
f.text(385, 322, "④ 응답", 18, 600, "teal")
f.path([(762, 215), (936, 215)], "violet")
f.text(850, 198, "② 조회 · 저장", 17, 600, "violet")
f.path([(938, 290), (764, 290)], "violet")
f.text(850, 322, "③ 결과", 17, 600, "violet")
f.path([(150, 352), (150, 440), (1050, 440), (1050, 352)], "red", arrow=False, dash="8 7", sw=2)
f.xmark(600, 440, 18)
f.text(600, 495, "클라이언트는 DB를 직접 열지 않고, 항상 API를 거친다", 20, 600, "red")

# ---------------------------------------------------------------- 02 요청과 응답의 구조
f = fig("02-요청과-응답의-구조", "요청과 응답의 구조", 1200, 470,
        "요청은 메서드와 주소, 헤더, 바디로 되어 있고, 응답은 상태 코드, 헤더, 바디로 되어 있다.")


def card(f, x, head, sub, color, bg, rows):
    f.rect(x, 40, 540, 400, "line", "white", rx=16)
    f.add(f'<path d="M{x},{40+16} a16,16 0 0 1 16,-16 h508 a16,16 0 0 1 16,16 v44 h-540 z" fill="{C[bg]}"/>')
    f.add(f'<line x1="{x}" y1="100" x2="{x+540}" y2="100" stroke="{C[color]}" stroke-width="2"/>')
    f.rich(x + 24, 80, [(head, color, 700), ("   " + sub, "muted", 400)], 22)
    y = 100
    for i, (lab, sublab, h, draw) in enumerate(rows):
        f.text(x + 24, y + 42, lab, 18, 700, color, "start")
        f.text(x + 24, y + 66, sublab, 15, 400, "muted", "start")
        draw(x + 190, y)
        y += h
        if i < len(rows) - 1:
            f.add(f'<line x1="{x+20}" y1="{y}" x2="{x+520}" y2="{y}" stroke="{C["faint"]}" stroke-width="1.5"/>')


def lines(f, ls, size=17):
    def d(x, y):
        for i, s in enumerate(ls):
            f.text(x, y + 42 + i * 28, s, size, 400, "ink", "start", True)
    return d


card(f, 40, "요청", "클라이언트 → 서버", "blue", "blueBg", [
    ("메서드 + 주소", "무엇을, 어디에", 90,
     lambda x, y: f.rich(x, y + 52, [("POST", "blue", 700, True), (" /api/v1/posts", "ink", 400, True)], 22)),
    ("헤더", "부가 정보", 110, lines(f, ["Content-Type: application/json", "Authorization: Bearer eyJhb…"])),
    ("바디", "내용물 (JSON)", 150, lines(f, ["{", '  "title": "제주도 3박 4일",', '  "content": "첫째 날은…"', "}"])),
])
card(f, 620, "응답", "서버 → 클라이언트", "teal", "tealBg", [
    ("상태 코드", "결과 번호", 90,
     lambda x, y: f.rich(x, y + 52, [("201", "green", 700, True), (" Created", "ink", 400, True)], 22)),
    ("헤더", "부가 정보", 110, lines(f, ["Content-Type: application/json", "Location: /api/v1/posts/43"])),
    ("바디", "내용물 (JSON)", 150, lines(f, ["{", '  "id": 43,', '  "title": "제주도 3박 4일"', "}"])),
])

# ---------------------------------------------------------------- 03 REST 세 줄 약속
f = fig("03-REST-세-줄-약속", "REST 세 줄 약속", 1200, 440,
        "DELETE /api/v1/posts/42 → 204 No Content 는 어떻게(메서드), 무엇(URL), 결과(상태 코드)로 나뉘어 읽힌다.", oy=75)
for (x, w, s, col, bg, sz, l1, l2) in [
    (80, 200, "DELETE", "blue", "blueBg", 34, "어떻게 (행동)", "HTTP 메서드"),
    (320, 440, "/api/v1/posts/42", "teal", "tealBg", 34, "무엇 (자원)", "URL"),
    (840, 300, "204 No Content", "green", "greenBg", 32, "결과", "상태 코드"),
]:
    cx = x + w / 2
    f.rect(x, 110, w, 96, col, bg)
    f.text(cx, 170, s, sz, 700, col, mono=True)
    f.add(f'<path d="M{x+8},222 V234 H{x+w-8} V222 M{cx},234 V246" fill="none" stroke="{C[col]}" stroke-width="2.5"/>')
    f.text(cx, 282, l1, 23, 700, col)
    f.text(cx, 314, l2, 19, 400, "muted")
f.path([(772, 158), (830, 158)], "muted", sw=3)
f.rect(250, 350, 700, 58, "line", "soft", rx=29)
f.text(600, 387, "읽는 법: “42번 글을 지웠고, 잘 끝났다”", 22, 500)

# ---------------------------------------------------------------- 04a 동사 URL과 자원 URL 비교
f = fig("04a-동사-URL과-자원-URL", "동사 URL과 자원 URL", 1240, 650,
        "URL에 동사를 넣는 대신, 행동은 HTTP 메서드로 표현하고 URL은 명사로 자원만 가리킨다.")
f.text(40, 46, "하는 일", 16, 700, "muted", "start")
f.text(230, 46, "동사가 들어간 URL", 16, 700, "red", "start")
f.text(740, 46, "메서드 + 명사 URL", 16, 700, "green", "start")
VR = [
    ("글 목록 조회", [("GET  /", "muted"), ("get", "red"), ("Posts", "ink")], "GET", "/posts", None),
    ("글 작성", [("POST /", "muted"), ("create", "red"), ("Post", "ink")], "POST", "/posts", None),
    ("42번 글 조회", [("GET  /", "muted"), ("get", "red"), ("Post?id=42", "ink")], "GET", "/posts/42", None),
    ("42번 글 수정", [("POST /", "muted"), ("update", "red"), ("Post?id=42", "ink")], "PATCH", "/posts/42", None),
    ("42번 글 삭제", [("GET  /", "muted"), ("delete", "red"), ("Post?id=42", "ink")], "DELETE", "/posts/42", "GET인데 데이터가 바뀜"),
    ("42번 글의 댓글 조회", [("GET  /", "muted"), ("get", "red"), ("CommentsByPostId?postId=42", "ink")], "GET", "/posts/42/comments", None),
]
for i, (task, bad, m, url, warn) in enumerate(VR):
    y = 66 + i * 72
    cy = y + 29
    f.text(40, cy + 6, task, 17, 600, "ink", "start")
    f.rect(230, y, 440, 58, "line", "soft", rx=10, sw=1.5)
    f.xmark(254, cy, 11)
    f.rich(276, cy + 6, [(t, c, 700 if c == "red" else 500, True) for t, c in bad], 17)
    if warn:
        f.text(660, cy + 24, warn, 12, 700, "red", "end")
    f.path([(676, cy), (734, cy)], "muted")
    f.rect(740, y, 460, 58, "green", "white", rx=10, sw=1.5)
    f.add(f'<circle cx="764" cy="{cy}" r="11" fill="{C["greenBg"]}" stroke="{C["green"]}" stroke-width="2"/>')
    f.add(f'<path d="M758,{cy} L762.5,{cy+4.5} L770,{cy-4}" fill="none" stroke="{C["green"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>')
    f.rich(788, cy + 6, [(f"{m:<7}", "blue", 700, True), (url, "teal", 700, True)], 18)
f.rect(40, 512, 1160, 108, "faint", "soft", rx=14)
f.rich(620, 552, [("동사(get · create · update · delete)는 ", "ink", 700), ("HTTP 메서드", "blue", 700),
                  ("가 표현하고, URL은 ", "ink", 700), ("자원(명사)", "teal", 700), ("만 가리킨다", "ink", 700)], 19, "middle")
f.rich(620, 590, [("같은 주소 ", "muted", 400), ("/posts/42", "teal", 700, True),
                  ("에 메서드만 바꿔 조회 · 수정 · 삭제를 한다", "muted", 400)], 17, "middle")

# ---------------------------------------------------------------- 04 자원 중심 URL
f = fig("04b-자원-중심-URL", "자원 중심 URL", 1200, 730,
        "URL은 명사를 계층으로 이어 붙여 자원을 가리키고, 누구인지는 경로에, 보여 주는 방식은 쿼리에 두며, 소문자와 하이픈, 버전 접두사를 쓴다.")
rows = [
    (0, "/api/v1", "/posts", "글 목록 (복수형 명사)"),
    (1, "/api/v1/posts", "/42", "42번 글 하나"),
    (2, "/api/v1/posts/42", "/comments", "42번 글의 댓글 목록"),
    (3, "/api/v1/posts/42/comments", "/7", "그중 7번 댓글"),
    (0, "/api/v1", "/members", "회원 목록"),
    (1, "/api/v1/members", "/me", "나 (로그인한 회원)"),
]
ys = [70, 128, 186, 244, 320, 378]
X0, STEP, SZ = 60, 40, 22
for i, ((ind, pre, seg, desc), y) in enumerate(zip(rows, ys)):
    x = X0 + ind * STEP
    if ind > 0:
        px = X0 + (ind - 1) * STEP + 10
        f.add(f'<path d="M{px},{ys[i-1]+10} V{y-7} H{x-8}" fill="none" stroke="{C["line"]}" stroke-width="2"/>')
    f.rich(x, y, [(pre, "muted", 400, True), (seg, "teal", 700, True)], SZ)
    end = x + tw(pre + seg, SZ, True)
    f.add(f'<line x1="{end+14}" y1="{y-7}" x2="{606}" y2="{y-7}" stroke="{C["faint"]}" stroke-width="2" stroke-dasharray="2 6"/>')
    f.text(620, y, desc, 20, 500, "ink", "start")
f.add(f'<path d="M880,112 H896 V258 H880" fill="none" stroke="{C["orange"]}" stroke-width="2.5"/>')
f.text(912, 172, "관계는 슬래시로", 19, 700, "orange", "start")
f.text(912, 200, "중첩은 2단계까지", 19, 700, "orange", "start")
f.text(912, 226, "(글 → 댓글)", 16, 400, "muted", "start")
f.text(912, 262, "더 깊어지면", 15, 400, "muted", "start")
f.rich(912, 286, [("/comments/7", "teal", 700, True), (" 로 끊는다", "muted", 400)], 15)
f.add(f'<line x1="40" y1="430" x2="1160" y2="430" stroke="{C["faint"]}" stroke-width="2"/>')
f.text(60, 476, "경로와 쿼리", 20, 700, "ink", "start")
f.rich(60, 532, [("/api/v1/posts", "ink", 400, True), ("/42", "teal", 700, True)], 22)
f.text(700, 532, "누구냐 → 경로", 21, 700, "teal", "start")
f.rich(60, 590, [("/api/v1/posts", "ink", 400, True), ("?sort=createdAt,desc&size=20", "blue", 700, True)], 22)
f.text(700, 590, "어떻게 보여 줄까 → 쿼리 (? 뒤)", 21, 700, "blue", "start")
f.rect(40, 628, 1120, 76, "faint", "soft", rx=12)
f.rich(60, 672, [("소문자 + 하이픈  ", "ink", 700), ("/blog-categories", "green", 700, True),
                 ("   아님: ", "muted", 400), ("/blogCategories", "red", 500, True)], 17)
f.rich(640, 672, [("/api/v1", "teal", 700, True), (" = 버전.  구조가 바뀌면 ", "ink", 500),
                  ("/api/v2", "teal", 700, True), ("를 따로 연다", "ink", 500)], 17)

# ---------------------------------------------------------------- 05 메서드별 결과
f = fig("05-메서드별-결과", "메서드별로 달라지는 결과", 1280, 690,
        "같은 42번 글에 메서드만 바꾸면 결과가 달라진다. PUT은 통째로 교체해 안 보낸 본문이 사라지고, PATCH는 보낸 제목만 고친다.")
for x, s, a in [(100, "메서드", "middle"), (180, "요청", "start"), (645, "전", "middle"), (915, "후", "middle"), (1050, "결과", "start")]:
    f.text(x, 50, s, 16, 700, "muted", a)


def post_card(f, x, y, title_v, body_v, title_c="ink", body_c="ink", tw_=400, bw=400):
    f.rect(x, y, 210, 88, "line", "white", rx=10)
    f.text(x + 14, y + 26, "42번 글", 15, 700, "muted", "start")
    f.rich(x + 14, y + 52, [("제목  ", "muted", 400), (title_v, title_c, tw_)], 16)
    f.rich(x + 14, y + 77, [("본문  ", "muted", 400), (body_v, body_c, bw)], 16)


def list_card(f, x, y, ids, new=None):
    f.rect(x, y, 210, 88, "line", "white", rx=10)
    f.text(x + 14, y + 26, "글 목록", 15, 700, "muted", "start")
    for i, n in enumerate(ids):
        nx = x + 14 + i * 62
        isnew = n == new
        f.rect(nx, y + 40, 52, 34, "green" if isnew else "line", "greenBg" if isnew else "soft", rx=8, sw=1.5)
        f.text(nx + 26, y + 63, n, 16, 700 if isnew else 500, "green" if isnew else "ink", mono=True)


M = [
    ("GET", "GET /posts/42", "(바디 없음)", "읽기만 한다", "데이터는 그대로", "green"),
    ("POST", "POST /posts", '{ "title": "부산 맛집" }', "새로 만든다", "201 + 새 글 주소", "green"),
    ("PUT", "PUT /posts/42", '{ "title": "제주 여행 후기" }', "통째로 교체한다", "안 보낸 칸은 사라질 수 있다", "orange"),
    ("PATCH", "PATCH /posts/42", '{ "title": "제주 여행 후기" }', "보낸 칸만 고친다", "나머지는 그대로", "blue"),
    ("DELETE", "DELETE /posts/42", "(바디 없음)", "지운다", "204 No Content", "red"),
]
for i, (m, req, body, n1, n2, nc) in enumerate(M):
    y0 = 76 + i * 120
    cy = y0 + 50
    f.rect(40, cy - 22, 120, 44, "ink", "ink", rx=22, sw=0)
    f.text(100, cy + 7, m, 19, 700, "white", mono=True)
    f.text(180, cy - 6, req, 18, 600, "ink", "start", True)
    f.text(180, cy + 22, body, 15, 400, "muted", "start", True)
    if m == "POST":
        list_card(f, 540, y0 + 6, ["41", "42"])
        list_card(f, 810, y0 + 6, ["41", "42", "43"], new="43")
    else:
        post_card(f, 540, y0 + 6, "제주 여행", "첫째 날은…")
        if m == "GET":
            post_card(f, 810, y0 + 6, "제주 여행", "첫째 날은…")
        elif m == "PUT":
            post_card(f, 810, y0 + 6, "제주 여행 후기", "(비어 있음)", "orange", "red", 700, 700)
        elif m == "PATCH":
            post_card(f, 810, y0 + 6, "제주 여행 후기", "첫째 날은…", "blue", "ink", 700)
        else:
            f.rect(810, y0 + 6, 210, 88, "line", "soft", rx=10, dash="6 6")
            f.text(915, y0 + 56, "42번 글 없음", 17, 600, "muted")
    f.path([(758, cy), (802, cy)], "muted")
    f.text(1050, cy - 4, n1, 18, 700, nc, "start")
    f.text(1050, cy + 22, n2, 15, 400, "muted", "start")
    if i < len(M) - 1:
        f.add(f'<line x1="40" y1="{y0+111}" x2="1240" y2="{y0+111}" stroke="{C["faint"]}" stroke-width="1.5"/>')

# ---------------------------------------------------------------- 06 멱등성
f = fig("06-멱등성", "멱등성", 1200, 560,
        "POST를 3번 보내면 글이 3개 생기지만, DELETE를 3번 보내도 42번 글이 없는 상태는 1번 보낸 것과 같다.")
for (px, head_m, head_t, sub, results, sc, s1, s2) in [
    (40, "POST /posts", " 를 3번 보내면", "보낼 때마다 새 자원이 하나씩 생긴다",
     [("201 · 43번 글 생성", "green", "greenBg"), ("201 · 44번 글 생성", "green", "greenBg"), ("201 · 45번 글 생성", "green", "greenBg")],
     "orange", "결과: 같은 글이 3개 생김", "멱등 아님 → 중복을 막아야 한다"),
    (620, "DELETE /posts/42", " 를 3번 보내면", "몇 번 보내도 서버 상태는 같다",
     [("204 · 42번 글 삭제", "green", "greenBg"), ("404 · 이미 없음", "muted", "soft"), ("404 · 이미 없음", "muted", "soft")],
     "green", "결과: 42번 글 없음", "1번 보낸 것과 상태가 같다 → 멱등"),
]:
    cx = px + 270
    f.rect(px, 30, 540, 460, "faint", "soft", rx=16)
    f.rich(cx, 76, [(head_m, "ink", 700, True), (head_t, "ink", 700)], 22, "middle")
    f.text(cx, 106, sub, 17, 400, "muted")
    for j, (r, col, bg) in enumerate(results):
        cy = 160 + j * 62
        f.text(px + 36, cy + 6, f"{j+1}번째", 16, 600, "muted", "start")
        f.path([(px + 100, cy), (px + 258, cy)], "muted")
        f.rect(px + 266, cy - 22, 240, 44, col, bg, rx=22, sw=1.5)
        f.text(px + 386, cy + 6, r, 17, 600, col)
    f.rect(px + 30, 362, 480, 104, sc, sc + "Bg", rx=14)
    f.text(cx, 404, s1, 22, 700, sc)
    f.text(cx, 440, s2, 18, 400, "ink")
f.rich(600, 532, [("멱등 O: ", "green", 700), ("GET · PUT · DELETE", "ink", 600, True),
                  ("     멱등 X: ", "orange", 700), ("POST", "ink", 600, True),
                  ("   →  글쓰기 버튼은 한 번 누르면 막아 둔다", "muted", 400)], 18, "middle")

# ---------------------------------------------------------------- 07 상태 코드
f = fig("07-상태-코드-네-갈래", "상태 코드 네 갈래", 1200, 640,
        "서버의 처리 결과는 2xx 성공, 3xx 리다이렉트, 4xx 클라이언트 오류, 5xx 서버 오류 네 갈래로 나뉘고, 실패를 200으로 주면 안 된다.")
f.rect(40, 215, 170, 110, "blue", "blueBg")
f.text(125, 265, "클라이언트", 22, 700, "blue")
f.text(125, 293, "요청", 16, 400, "muted")
f.rect(280, 215, 190, 110, "teal", "tealBg")
f.text(375, 262, "서버", 24, 700, "teal")
f.text(375, 292, "처리 결과", 16, 400, "muted")
f.path([(212, 270), (276, 270)], "blue")
f.text(125, 362, "바디를 읽기 전에", 15, 400, "muted")
f.text(125, 384, "상태 코드로 결과를 안다", 15, 400, "muted")
f.path([(472, 270), (535, 270)], "muted", arrow=False)
for (y, col, code, t1, codes, t3) in [
    (24, "green", "2xx", "성공", "200 OK · 201 Created · 204 No Content", "요청한 작업이 처리됨"),
    (150, "violet", "3xx", "리다이렉트", "301 · 302 · 304 Not Modified", "다른 주소로 이동 / 캐시를 그대로 사용 (API에선 드묾)"),
    (276, "orange", "4xx", "클라이언트 오류", "400 · 401 · 403 · 404 · 409", "요청을 고쳐서 다시 보내야 함"),
    (402, "red", "5xx", "서버 오류", "500 · 502 · 503 · 504", "서버 쪽 문제, 클라이언트는 잠시 후 재시도"),
]:
    cy = y + 54
    f.path([(535, 270), (535, cy), (596, cy)], col)
    f.rect(600, y, 560, 108, col, col + "Bg")
    f.text(668, cy + 13, code, 36, 700, col, mono=True)
    f.text(750, cy - 18, t1, 20, 700, col, "start")
    f.text(750, cy + 9, codes, 16, 500, "ink", "start", True)
    f.text(750, cy + 36, t3, 15, 400, "muted", "start")
f.rect(40, 548, 1120, 66, "red", "redBg", rx=12)
f.xmark(80, 581, 15)
f.rich(108, 588, [("하지 말 것: 실패인데 ", "ink", 600), ('200 OK + { "success": false }', "red", 700, True),
                  ("  →  모니터링·재시도·캐시가 성공으로 처리", "ink", 400)], 18)

# ---------------------------------------------------------------- 07b 자주 만나는 에러 코드
f = fig("07b-자주-만나는-에러-코드", "자주 만나는 에러 상태 코드", 1240, 700,
        "실제로 자주 보는 에러 코드는 400, 401, 403, 404, 409와 500, 502, 503, 504이며, 코드마다 먼저 확인할 곳이 다르다.")
COLS = [(40, "코드"), (170, "이름"), (430, "언제 나오나 (블로그 API 예)"), (850, "먼저 확인할 것")]
for x, t in COLS:
    f.text(x, 46, t, 16, 700, "muted", "start")
f.add(f'<line x1="30" y1="62" x2="1210" y2="62" stroke="{C["line"]}" stroke-width="2"/>')
ROWS = [
    ("400", "Bad Request", "필수 값 누락, 형식 오류 (빈 제목, 깨진 JSON)", "응답의 errors: 어느 필드가 틀렸나", "orange", True),
    ("401", "Unauthorized", "토큰이 없거나 만료됨", "Authorization 헤더, 토큰 만료 시간", "orange", True),
    ("403", "Forbidden", "로그인했지만 권한 없음 (남의 글 삭제)", "사용자 역할, 자원 소유자", "orange", False),
    ("404", "Not Found", "없는 자원 (/posts/99999), URL 오타", "URL 경로와 id, 삭제된 데이터인지", "orange", True),
    ("409", "Conflict", "중복 (같은 이메일로 가입), 동시 수정", "유니크 값, 버전 필드", "orange", False),
    ("500", "Internal Server Error", "처리하지 못한 예외 (NullPointerException 등)", "서버 로그의 스택 트레이스", "red", True),
    ("502", "Bad Gateway", "게이트웨이가 뒤쪽 서버에서 잘못된 응답을 받음", "뒤쪽 서비스가 떠 있나, 주소·포트", "red", False),
    ("503", "Service Unavailable", "과부하, 점검, 배포 중이라 처리 불가", "서버 상태, 배포·재시작 중인지", "red", False),
    ("504", "Gateway Timeout", "뒤쪽 서버가 제한 시간 안에 응답 안 함", "느린 쿼리, 타임아웃 설정", "red", False),
]
for i, (code, name, when, check, col, hot) in enumerate(ROWS):
    y = 70 + i * 62
    cy = y + 37
    if i % 2 == 0:
        f.add(f'<rect x="30" y="{y+4}" width="1180" height="56" rx="8" fill="{C["soft"]}"/>')
    f.add(f'<rect x="30" y="{y+4}" width="5" height="56" rx="2" fill="{C[col]}"/>')
    f.text(48, cy + 2, code, 24, 700, col, "start", True)
    if hot:
        f.rect(100, cy - 16, 52, 26, col, col + "Bg", rx=13, sw=1.2)
        f.text(126, cy + 2, "자주", 13, 700, col)
    f.text(170, cy, name, 16, 600, "ink", "start", True)
    f.text(430, cy, when, 16, 400, "ink", "start")
    f.text(850, cy, check, 16, 400, "muted", "start")
    if code == "409":
        f.add(f'<line x1="30" y1="{y+66}" x2="1210" y2="{y+66}" stroke="{C["line"]}" stroke-width="1.5" stroke-dasharray="4 6"/>')
f.text(40, 664, "그 밖에:  405 Method Not Allowed (메서드 틀림) · 415 Unsupported Media Type (Content-Type 틀림) · 429 Too Many Requests (요청 과다)", 15, 400, "muted", "start")

# ---------------------------------------------------------------- 08 401과 403
f = fig("08-401과-403", "401과 403", 1200, 420,
        "요청은 인증(실패하면 401)과 인가(실패하면 403)를 모두 통과해야 처리된다.", oy=50)
f.rect(30, 80, 180, 110, "blue", "blueBg")
f.text(120, 122, "클라이언트", 21, 700, "blue")
f.text(120, 152, "DELETE /posts/42", 15, 600, "ink", mono=True)
f.text(120, 176, "(글 삭제 요청)", 15, 400, "muted")
for (x, w, t1, t2, t3) in [(280, 240, "① 인증", "로그인했나?", "(Authentication)"),
                           (590, 250, "② 인가", "이 글을 지울 권한이 있나?", "(Authorization)")]:
    f.rect(x, 80, w, 110, "ink", "white", sw=2)
    f.text(x + w / 2, 120, t1, 20, 700)
    f.text(x + w / 2, 150, t2, 17, 500)
    f.text(x + w / 2, 175, t3, 14, 400, "muted")
f.rect(910, 80, 260, 110, "green", "greenBg")
f.text(1040, 126, "204 No Content", 22, 700, "green", mono=True)
f.text(1040, 162, "42번 글 삭제 완료", 17, 500)
f.path([(212, 135), (276, 135)], "muted")
f.path([(522, 135), (586, 135)], "green")
f.text(554, 122, "예", 16, 700, "green")
f.path([(842, 135), (906, 135)], "green")
f.text(874, 122, "예", 16, 700, "green")
for (cx, code, l1, l2) in [(400, "401 Unauthorized", "인증 실패", "토큰이 없거나 만료됨"),
                           (715, "403 Forbidden", "인가 실패", "글쓴이·관리자가 아님")]:
    f.path([(cx, 192), (cx, 266)], "orange")
    f.text(cx + 12, 236, "아니오", 15, 700, "orange", "start")
    f.rect(cx - 115, 270, 230, 120, "orange", "orangeBg")
    f.text(cx, 308, code, 19, 700, "orange", mono=True)
    f.text(cx, 342, l1, 19, 700)
    f.text(cx, 370, l2, 16, 400, "muted")
f.rect(910, 270, 260, 120, "faint", "soft")
f.text(1040, 304, "구분", 17, 700, "muted")
f.text(1040, 336, "401: 누구인지 모름", 16, 500)
f.text(1040, 364, "403: 누구인지 알지만 권한 없음", 16, 500)

# ---------------------------------------------------------------- 09 공통 에러 형식
f = fig("09-공통-에러-형식", "공통 에러 형식", 1200, 570,
        "API마다 다른 에러 모양을 표준 형식 하나로 통일하면, 화면은 code 하나만 보고 처리할 수 있다.")
f.add(f'<line x1="600" y1="30" x2="600" y2="540" stroke="{C["faint"]}" stroke-width="2" stroke-dasharray="6 8"/>')
f.text(300, 62, "통일 전", 23, 700)
f.text(300, 92, "API마다 에러 모양이 다르다", 16, 400, "muted")
for j, (name, st, stc, body) in enumerate([
    ("글 API", "404", "ink", '{ "error": "not found" }'),
    ("댓글 API", "400", "ink", '{ "result": false, "msg": "실패" }'),
    ("회원 API", "200", "red", '"FAIL"'),
]):
    y = 128 + j * 76
    f.rect(40, y, 130, 56, "line", "soft", rx=10)
    f.text(105, y + 34, name, 17, 700)
    f.path([(172, y + 28), (196, y + 28)], "muted", sw=2)
    f.rect(200, y, 370, 56, "line", "white", rx=10)
    f.rich(214, y + 34, [(st, stc, 700, True), ("  " + body, "ink", 400, True)], 15)
f.text(556, 314, "실패인데 200", 14, 700, "red", "end")
f.path([(300, 350), (300, 446)], "muted")
f.rect(130, 450, 340, 90, "orange", "orangeBg")
f.text(300, 487, "화면 개발자", 19, 700, "orange")
f.text(300, 517, "에러 모양 3가지를 따로 처리", 16, 400)
f.text(900, 62, "통일 후", 23, 700)
f.text(900, 92, "모든 API가 같은 모양으로 응답", 16, 400, "muted")
for j, name in enumerate(["글 API", "댓글 API", "회원 API"]):
    y = 128 + j * 76
    f.rect(630, y, 120, 56, "line", "soft", rx=10)
    f.text(690, y + 34, name, 17, 700)
    f.path([(752, y + 28), (776, y + 28)], "teal", arrow=False)
f.path([(776, 156), (776, 308)], "teal", arrow=False)
f.path([(776, 232), (798, 232)], "teal")
f.rect(800, 110, 370, 300, "teal", "white")
J = ["{", '  "type": "/errors/post-not-found",', '  "title": "글을 찾을 수 없습니다",', '  "status": 404,',
     '  "detail": "42번 글이 없습니다.",', '  "code": "POST_NOT_FOUND"', "}"]
for k, s in enumerate(J):
    hl = "code" in s
    f.text(818, 142 + k * 28, s, 15, 700 if hl else 400, "blue" if hl else "ink", "start", True)
f.add(f'<line x1="816" y1="348" x2="1154" y2="348" stroke="{C["faint"]}" stroke-width="1.5"/>')
f.text(818, 372, "type · title · status · detail: 표준 (RFC 9457)", 14, 400, "muted", "start")
f.text(818, 396, "code: 우리 팀 에러 코드", 14, 700, "blue", "start")
f.path([(985, 412), (985, 446)], "teal")
f.rect(815, 450, 340, 90, "green", "greenBg")
f.text(985, 487, "화면 개발자", 19, 700, "green")
f.text(985, 517, "code 하나만 보고 처리", 16, 400)

# ---------------------------------------------------------------- 10 전역 예외 처리와 입력 검증
f = fig("10-전역-예외-처리와-입력-검증", "전역 예외 처리와 입력 검증", 1240, 590,
        "요청은 입력 검증, 컨트롤러, 서비스, DB를 지나고, 어디서 난 에러든 전역 예외 처리기 한 곳에 모여 같은 양식으로 응답한다.")
f.rect(30, 110, 180, 100, "blue", "blueBg")
f.text(120, 167, "클라이언트", 21, 700, "blue")
for (x, w, t1, t2, t3, col, bg) in [
    (270, 200, "입력 검증", "@Valid", "요청 DTO 형식 검사", "orange", "orangeBg"),
    (520, 190, "컨트롤러", "요청 받고 넘기기", None, "line", "white"),
    (760, 190, "서비스", "업무 규칙 검사", None, "line", "white"),
    (1000, 200, "DB", "읽기 · 쓰기", None, "violet", "violetBg"),
]:
    f.rect(x, 110, w, 100, col, bg)
    tc = "ink" if col == "line" else col
    if t3:
        f.text(x + w / 2, 148, t1, 20, 700, tc)
        f.text(x + w / 2, 174, t2, 15, 600, "ink", mono=True)
        f.text(x + w / 2, 197, t3, 14, 400, "muted")
    else:
        f.text(x + w / 2, 155, t1, 20, 700, tc)
        f.text(x + w / 2, 182, t2, 15, 400, "muted")
f.path([(212, 160), (266, 160)], "blue")
f.path([(472, 160), (516, 160)], "muted")
f.path([(712, 160), (756, 160)], "muted")
f.path([(952, 160), (996, 160)], "muted")
f.text(615, 240, "try-catch 없음", 15, 600, "muted")
f.path([(615, 108), (615, 64), (120, 64), (120, 106)], "green")
f.text(368, 52, "성공하면 200 · 201 · 204", 16, 700, "green")
f.path([(370, 212), (370, 376)], "orange")
f.text(382, 292, "형식 오류", 15, 700, "orange", "start")
f.text(382, 314, "(빈 제목 등)", 14, 400, "muted", "start")
f.path([(855, 212), (855, 376)], "orange")
f.text(867, 292, "글 없음", 15, 700, "orange", "start")
f.text(867, 314, "중복 · 권한 없음", 15, 700, "orange", "start")
f.path([(1100, 212), (1100, 376)], "red")
f.text(1112, 302, "예상 못 한 오류", 15, 700, "red", "start")
f.rect(270, 380, 930, 180, "teal", "tealBg")
f.rich(735, 418, [("전역 예외 처리기 · ", "teal", 700), ("@RestControllerAdvice", "teal", 700, True)], 21, "middle")
f.text(735, 446, "어디서 던진 예외든 여기서 받아 같은 형식으로 응답한다", 16, 400, "ink")
for k, (t1, t2, col) in enumerate([("검증 실패", "400", "orange"), ("글 없음", "404", "orange"),
                                    ("중복 제목", "409", "orange"), ("그 밖의 오류", "500 + 로그", "red")]):
    x = 290 + k * 230
    f.rect(x, 468, 210, 70, col, "white", rx=12, sw=1.5)
    f.text(x + 105, 495, t1, 15, 500)
    f.text(x + 105, 524, t2, 19, 700, col, mono=True)
f.path([(268, 503), (120, 503), (120, 214)], "teal")
f.text(132, 345, "같은 양식의", 15, 700, "teal", "start")
f.text(132, 367, "에러 응답", 15, 700, "teal", "start")

# ---------------------------------------------------------------- 11 검색·정렬·페이징 주소
f = fig("11-검색-정렬-페이징-주소", "검색·정렬·페이징 주소 읽기", 1200, 300,
        "목록 조건은 물음표 뒤 쿼리에 검색, 정렬, 페이징 순으로 이름=값을 &로 이어 붙인다.", oy=45)
SZ = 24
groups = [
    ("/api/v1/posts?", "ink", 400, "어떤 자원", "경로 (? 앞)"),
    ("topic=TRAVEL&keyword=제주", "blue", 700, "검색 · 필터", "어떤 글만?"),
    ("&", "muted", 400, None, None),
    ("sort=createdAt,desc", "teal", 700, "정렬", "어떤 순서로?"),
    ("&", "muted", 400, None, None),
    ("page=0&size=20", "violet", 700, "페이징", "몇 개씩, 몇 번째 쪽?"),
]
total = sum(tw(g[0], SZ, True) for g in groups)
x = (1200 - total) / 2
f.rich(x, 100, [(g[0], g[1], g[2], True) for g in groups], SZ)
for (s, col, wt, l1, l2) in groups:
    w = tw(s, SZ, True)
    if l1:
        bc = "muted" if col == "ink" else col
        f.add(f'<path d="M{x+4:.1f},120 V130 H{x+w-4:.1f} V120 M{x+w/2:.1f},130 V140" fill="none" stroke="{C[bc]}" stroke-width="2.5"/>')
        f.text(x + w / 2, 174, l1, 20, 700, bc)
        f.text(x + w / 2, 202, l2, 16, 400, "muted")
    x += w
f.rect(150, 236, 900, 46, "faint", "soft", rx=23)
f.text(600, 266, "물음표(?) 뒤에 이름=값을 &로 잇는다 · 안 보내면 기본값 (최신순, 20개)", 17, 500)

# ---------------------------------------------------------------- 12 오프셋과 커서
f = fig("12-오프셋과-커서", "오프셋과 커서", 1200, 600,
        "오프셋은 앞의 글을 세며 건너뛰어 쪽 번호로 이동하고, 커서는 마지막으로 본 글 다음부터 바로 가져온다.")
for (px, head, url) in [(30, "오프셋 (쪽 번호)", "GET /posts?page=2&size=20"),
                        (615, "커서 (마지막으로 본 위치)", "GET /posts?cursor=981&size=20")]:
    f.rect(px, 30, 555, 490, "faint", "soft", rx=16)
    f.text(px + 277, 70, head, 22, 700)
    f.text(px + 277, 100, url, 17, 600, "muted", mono=True)
# 오프셋
for (y, h, t1, t2, col, bg, dash) in [
    (125, 70, "0쪽", "1~20번째 글", "line", "white", None),
    (205, 70, "1쪽", "21~40번째 글", "line", "white", None),
    (285, 70, "2쪽", "41~60번째 글", "blue", "blueBg", None),
    (365, 46, "3쪽 …", None, "line", "soft", "6 6"),
]:
    f.rect(60, y, 230, h, col, bg, rx=10, dash=dash)
    if t2:
        f.text(175, y + 30, t1, 17, 700, "blue" if col == "blue" else "ink")
        f.text(175, y + 54, t2, 15, 400, "muted")
    else:
        f.text(175, y + 29, t1, 16, 500, "muted")
f.add(f'<path d="M302,128 H314 V272 H302" fill="none" stroke="{C["orange"]}" stroke-width="2.5"/>')
f.text(328, 194, "건너뛴다 (40개)", 17, 700, "orange", "start")
f.text(328, 218, "앞의 글을 세면서 넘김", 15, 400, "muted", "start")
f.path([(380, 320), (296, 320)], "blue")
f.text(390, 326, "이만큼 가져온다", 17, 700, "blue", "start")
f.text(60, 456, "장점: 원하는 쪽으로 바로 이동 (게시판)", 16, 600, "green", "start")
f.text(60, 486, "단점: 뒤쪽일수록 느리고, 새 글이 오면 겹칠 수 있다", 16, 600, "orange", "start")
# 커서
f.rect(645, 125, 230, 150, "line", "white", rx=10)
f.text(760, 192, "이미 본 글", 17, 700)
f.text(760, 218, "1000번 ~ 981번", 15, 400, "muted")
f.add(f'<line x1="635" y1="280" x2="885" y2="280" stroke="{C["violet"]}" stroke-width="3" stroke-dasharray="8 5"/>')
f.text(895, 286, "커서 = 981", 16, 700, "violet", "start")
f.rect(645, 285, 230, 70, "blue", "blueBg", rx=10)
f.text(760, 315, "980번 ~ 961번", 17, 700, "blue")
f.text(760, 339, "이번에 가져올 20개", 15, 400, "muted")
f.rect(645, 365, 230, 46, "line", "soft", rx=10, dash="6 6")
f.text(760, 394, "…", 16, 500, "muted")
f.text(895, 192, "세지 않고", 17, 700, "ink", "start")
f.text(895, 216, "981번 바로 다음부터", 15, 400, "muted", "start")
f.path([(985, 330), (881, 330)], "blue")
f.text(995, 336, "이만큼", 17, 700, "blue", "start")
f.text(645, 456, "장점: 데이터가 많아도 빠르다 (무한 스크롤)", 16, 600, "green", "start")
f.text(645, 486, "단점: 5쪽으로 바로 가기는 어렵다", 16, 600, "orange", "start")
f.rich(600, 568, [("안전장치  ", "ink", 700), ("size 최댓값 (예: 100) · 기본 정렬 · 정렬할 수 있는 칸 제한", "muted", 500)], 18, "middle")

# ---------------------------------------------------------------- 13 API 문서
f = fig("13-API-문서가-만들어지는-길", "API 문서가 만들어지는 길", 1200, 460,
        "코드에서 springdoc이 OpenAPI 명세를 만들고 Swagger UI가 보여 주며, 정확도가 필요하면 테스트를 통과해야 생기는 REST Docs를 쓴다.")
f.text(30, 56, "시작이 쉬움", 15, 700, "teal", "start")
f.text(30, 216, "정확도 높음", 15, 700, "violet", "start")
f.rect(30, 70, 210, 110, "line", "white")
f.text(135, 112, "컨트롤러 코드", 19, 700)
f.text(135, 142, "@GetMapping", 14, 500, "muted", mono=True)
f.text(135, 164, "@Schema", 14, 500, "muted", mono=True)
f.path([(242, 125), (326, 125)], "teal")
f.text(285, 112, "springdoc", 14, 700, "teal", mono=True)
f.text(285, 150, "자동 생성", 14, 500, "teal")
f.rect(330, 70, 230, 110, "teal", "tealBg")
f.text(445, 112, "OpenAPI 명세", 19, 700, "teal")
f.text(445, 140, "openapi.json", 15, 500, "ink", mono=True)
f.text(445, 164, "문서의 규격", 15, 400, "muted")
f.path([(562, 125), (636, 125)], "teal")
f.text(600, 112, "화면으로", 14, 500, "teal")
f.rect(640, 70, 250, 110, "blue", "blueBg")
f.text(765, 112, "Swagger UI", 19, 700, "blue")
f.text(765, 140, "API 목록 · 예시", 15, 400)
f.text(765, 164, "Try it out 으로 호출", 15, 400, "muted")
f.path([(892, 125), (956, 125)], "blue")
f.rect(960, 70, 210, 270, "green", "greenBg")
f.text(1065, 176, "읽는 사람", 21, 700, "green")
f.text(1065, 210, "프론트 개발자", 16, 500)
f.text(1065, 236, "다른 팀 · 미래의 나", 16, 500)
f.rect(30, 230, 210, 110, "line", "white")
f.text(135, 276, "테스트 코드", 19, 700)
f.text(135, 304, "API를 실제로 호출", 15, 400, "muted")
f.path([(242, 285), (326, 285)], "violet")
f.text(285, 272, "통과해야", 14, 700, "violet")
f.text(285, 310, "문서 생성", 14, 500, "violet")
f.rect(330, 230, 230, 110, "violet", "violetBg")
f.text(445, 274, "Spring REST Docs", 18, 700, "violet")
f.text(445, 304, "코드와 어긋나지 않음", 15, 400)
f.path([(562, 285), (956, 285)], "violet")
f.text(760, 272, "HTML 문서", 15, 500, "violet")
f.rect(30, 378, 1140, 58, "faint", "soft", rx=12)
f.rich(600, 414, [("좋은 문서에 꼭  ", "ink", 700),
                  ("메서드 + URL · 인증 · 요청 예시 · 응답 예시 · 에러 코드 표", "muted", 500)], 18, "middle")

# ---------------------------------------------------------------- 14 한 장 요약
f = fig("14-한-장-요약", "한 장 요약: 요청 하나의 여정", 1280, 390,
        "요청 하나는 URL, 메서드, 입력 검증, 전역 예외 처리, 상태 코드와 공통 응답 순으로 지나가고, API 문서가 이 약속을 미리 알려 준다.")
f.rect(60, 30, 1160, 56, "green", "greenBg", rx=12)
f.rich(640, 65, [("API 문서  ", "green", 700), ("아래 규칙을 모두 미리 적어 둔다", "ink", 500)], 19, "middle")
steps = [
    ("/posts/42", "teal", 18, "무엇 = URL", "명사 · 복수형"),
    ("DELETE", "blue", 18, "어떻게 = 메서드", "조회·생성·수정·삭제"),
    ("@Valid", "orange", 18, "입력 검증", "서버가 반드시 다시"),
    ("@RestControllerAdvice", "teal", 14, "예외는 한곳에서", "같은 에러 양식"),
    ("204 No Content", "green", 17, "결과 = 상태 코드", "응답 모양은 하나로"),
]
for k, (code, col, sz, cap, sub) in enumerate(steps):
    x = 60 + k * 240
    f.rect(x, 116, 200, 150, col, "white", rx=14)
    f.add(f'<circle cx="{x+22}" cy="{138}" r="13" fill="{C[col]}"/>')
    f.text(x + 22, 143, str(k + 1), 14, 700, "white")
    f.text(x + 100, 186, code, sz, 700, col, mono=True)
    f.text(x + 100, 220, cap, 18, 700)
    f.text(x + 100, 248, sub, 14, 400, "muted")
    if k < len(steps) - 1:
        f.path([(x + 202, 191), (x + 236, 191)], "muted")
f.rect(60, 300, 1160, 60, "faint", "soft", rx=12)
f.rich(640, 337, [("목록은 나눠서  ", "violet", 700), ("?page=0&size=20&sort=createdAt,desc", "ink", 600, True),
                  ("  처럼 쿼리로", "muted", 500)], 18, "middle")

# ---------------------------------------------------------------- 15 단일 서버 요청 흐름
def req_strip(f, y=44):
    f.rich(40, y, [("요청  ", "muted", 700), ("POST /api/v1/posts/42/comments", "blue", 700, True),
                   ("   42번 글에 댓글 작성", "muted", 400)], 19)

f = fig("15-단일-서버의-요청-흐름", "단일 서버의 요청 흐름", 1240, 640,
        "단일 서버에서는 애플리케이션 하나가 인증, URL 매핑, 컨트롤러, 서비스를 모두 처리하고, 모듈 사이 호출은 메서드 호출이며 DB는 하나다.")
req_strip(f)
f.rect(30, 250, 160, 110, "blue", "blueBg")
f.text(110, 300, "클라이언트", 20, 700, "blue")
f.text(110, 326, "브라우저 · 앱", 14, 400, "muted")
f.rect(250, 80, 720, 480, "teal", "white", rx=18)
f.text(274, 112, "Spring Boot 애플리케이션 1개", 18, 700, "teal", "start")
f.text(560, 112, "(서버 1대, 배포 단위 1개)", 15, 400, "muted", "start")
f.rect(280, 132, 660, 46, "line", "soft", rx=10)
f.rich(300, 162, [("① 인증 필터  ", "ink", 700), ("토큰 확인, 실패하면 401", "muted", 400)], 16)
f.rect(280, 192, 660, 46, "line", "soft", rx=10)
f.rich(300, 222, [("② URL 매핑  ", "ink", 700), ("경로와 메서드로 컨트롤러 선택", "muted", 400)], 16)
for k, (c, path_, sv, hl) in enumerate([("PostController", "/posts/**", "PostService", False),
                                        ("CommentController", "/posts/{id}/comments", "CommentService", True),
                                        ("MemberController", "/members/**", "MemberService", False)]):
    x = 280 + k * 240
    col, bg = ("blue", "blueBg") if hl else ("line", "white")
    tc = "blue" if hl else "ink"
    f.rect(x, 270, 180, 70, col, bg, rx=10)
    f.text(x + 90, 298, c, 14, 700, tc, mono=True)
    f.text(x + 90, 322, path_, 13, 400, "muted", mono=True)
    f.rect(x, 390, 180, 60, col, bg, rx=10)
    f.text(x + 90, 426, sv, 15, 700, tc, mono=True)
    if hl:
        f.path([(x + 90, 240), (x + 90, 266)], "blue")
        f.path([(x + 90, 342), (x + 90, 386)], "blue")
f.path([(520, 420), (464, 420)], "teal")
f.text(492, 478, "③ postService.exists(42)", 14, 700, "teal", mono=True)
f.text(492, 500, "같은 프로세스 안의 메서드 호출 (네트워크 없음)", 14, 400, "muted")
f.path([(192, 280), (226, 280), (226, 155), (276, 155)], "blue")
f.path([(248, 330), (194, 330)], "green")
f.text(110, 392, "⑤ 201 Created", 16, 700, "green")
f.text(110, 414, "또는 4xx · 5xx", 14, 400, "muted")
f.rect(1030, 300, 180, 190, "violet", "violetBg")
f.text(1120, 336, "DB 1개", 19, 700, "violet")
for k, t in enumerate(["posts", "comments", "members"]):
    f.text(1120, 380 + k * 32, t, 16, 600 if t == "comments" else 400, "ink", mono=True)
f.path([(702, 440), (730, 440), (730, 536), (1120, 536), (1120, 494)], "violet")
f.text(850, 526, "④ INSERT", 14, 700, "violet", mono=True)
f.text(40, 610, "장점: 구조가 단순하고 내부 호출이 빠르다      단점: 일부 기능만 따로 배포하거나 확장하기 어렵다", 16, 500, "muted", "start")

# ---------------------------------------------------------------- 16 MSA 요청 흐름
f = fig("16-MSA의-요청-흐름", "MSA의 요청 흐름", 1240, 700,
        "MSA에서는 API 게이트웨이가 인증과 라우팅을 맡고, 기능별 서비스가 각자 DB를 가지며, 서비스끼리도 REST API로 통신한다.")
req_strip(f)
f.rect(30, 290, 160, 110, "blue", "blueBg")
f.text(110, 340, "클라이언트", 20, 700, "blue")
f.text(110, 366, "브라우저 · 앱", 14, 400, "muted")
f.rect(240, 150, 270, 400, "teal", "tealBg")
f.text(375, 190, "API Gateway", 21, 700, "teal")
f.text(375, 216, "외부 요청이 들어오는 단일 입구", 14, 400, "muted")
f.text(262, 262, "① 인증", 16, 700, "ink", "start")
f.text(262, 286, "토큰 확인, 실패하면 401", 14, 400, "muted", "start")
f.text(262, 334, "② 라우팅 (경로 → 서비스)", 16, 700, "ink", "start")
for k, (r, hl) in enumerate([("/posts/*/comments → comment", True), ("/posts/**         → post", False),
                             ("/members/**       → member", False)]):
    f.text(262, 364 + k * 26, r, 13, 700 if hl else 400, "blue" if hl else "ink", "start", True)
f.text(262, 466, "그 밖에: 요청 로그, 요청 수 제한(429),", 13, 400, "muted", "start")
f.text(262, 486, "뒤쪽 장애 시 502 · 503 · 504", 13, 400, "muted", "start")
f.path([(192, 320), (236, 320)], "blue")
SV = [(90, "post-service", "/posts/**", "post DB", False),
      (280, "comment-service", "/posts/{id}/comments", "comment DB", True),
      (470, "member-service", "/members/**", "member DB", False)]
for (y, n, pth, db, hl) in SV:
    col, bg = ("blue", "blueBg") if hl else ("line", "white")
    f.rect(600, y, 270, 120, col, bg)
    f.text(735, y + 50, n, 18, 700, "blue" if hl else "ink", mono=True)
    f.text(735, y + 78, pth, 14, 400, "muted", mono=True)
    f.rect(1010, y + 20, 190, 80, "violet", "violetBg", rx=12)
    f.text(1105, y + 66, db, 17, 700, "violet")
    f.path([(872, y + 60), (1006, y + 60)], "violet" if hl else "line", sw=2.5 if hl else 2)
f.text(938, 330, "⑤ INSERT", 14, 700, "violet", mono=True)
f.path([(512, 320), (596, 320)], "blue")
f.text(554, 306, "③", 15, 700, "blue")
f.path([(690, 278), (690, 214)], "teal")
f.path([(780, 214), (780, 278)], "teal", dash="6 5")
f.text(800, 238, "④ GET /api/v1/posts/42", 13, 700, "teal", "start", True)
f.text(800, 258, "HTTP 호출 → 200 또는 404", 13, 400, "muted", "start")
f.path([(596, 370), (514, 370)], "green")
f.path([(236, 370), (194, 370)], "green")
f.text(110, 432, "⑥ 201 Created", 16, 700, "green")
f.text(110, 454, "또는 4xx · 5xx", 14, 400, "muted")
f.text(40, 650, "장점: 서비스마다 따로 배포·확장      단점: 서비스 사이가 네트워크 호출이라 지연·장애를 처리해야 한다", 16, 500, "muted", "start")
f.text(40, 678, "클라이언트가 보내는 요청(URL·메서드)은 단일 서버와 똑같다", 16, 700, "ink", "start")

# ---------------------------------------------------------------- 17 MSA 에러 전달
f = fig("17-MSA에서-에러가-전달되는-흐름", "MSA에서 에러가 전달되는 흐름", 1240, 660,
        "post-service의 404가 comment-service와 게이트웨이를 거쳐 같은 상태 코드와 에러 형식으로 클라이언트에 전달되고, 응답이 없으면 503이나 504가 된다.")
LX = [(130, "클라이언트", "blue", "blueBg"), (450, "API Gateway", "teal", "tealBg"),
      (780, "comment-service", "blue", "white"), (1090, "post-service", "ink", "white")]
for x, n, col, bg in LX:
    f.rect(x - 110, 30, 220, 56, col, bg, rx=12)
    f.text(x, 65, n, 17, 700, "ink" if col == "ink" else col, mono=(n.endswith("service")))
    f.add(f'<line x1="{x}" y1="88" x2="{x}" y2="520" stroke="{C["line"]}" stroke-width="2" stroke-dasharray="5 6"/>')


def msg(f, x1, x2, y, label, col="ink", dash=None, mono=True):
    f.path([(x1, y), (x2 + (-6 if x2 > x1 else 6), y)], col, dash=dash)
    f.text((x1 + x2) / 2, y - 12, label, 14, 700, col, mono=mono)


msg(f, 130, 450, 140, "POST /api/v1/posts/42/comments", "blue")
f.rect(470, 165, 190, 34, "teal", "white", rx=17, sw=1.5)
f.text(565, 188, "토큰 확인 OK", 14, 600, "teal")
msg(f, 450, 780, 240, "POST /api/v1/posts/42/comments", "blue")
msg(f, 780, 1090, 300, "GET /api/v1/posts/42", "teal")
f.rect(1100, 318, 130, 34, "line", "white", rx=8, sw=1.5)
f.text(1165, 341, "42번 글 없음", 14, 600, "muted")
msg(f, 1090, 780, 380, "404  POST_NOT_FOUND", "orange", dash="7 5")
msg(f, 780, 450, 430, "404  POST_NOT_FOUND", "orange", dash="7 5")
msg(f, 450, 130, 480, "404  POST_NOT_FOUND", "orange", dash="7 5")
f.rect(30, 540, 580, 100, "orange", "orangeBg", rx=12)
f.text(50, 574, "에러 형식이 모든 서비스에서 같으면", 16, 700, "orange", "start")
f.text(50, 600, "상태 코드와 code가 그대로 전달된다", 16, 400, "ink", "start")
f.text(50, 624, "→ 클라이언트는 어느 서비스에서 났는지 몰라도 처리 가능", 14, 400, "muted", "start")
f.rect(630, 540, 580, 100, "red", "redBg", rx=12)
f.text(650, 574, "post-service가 응답하지 않으면", 16, 700, "red", "start")
f.rich(650, 600, [("꺼져 있음 → ", "ink", 400), ("503", "red", 700, True), ("   제한 시간 초과 → ", "ink", 400), ("504", "red", 700, True)], 16)
f.text(650, 624, "그대로 500을 주지 말고 원인에 맞는 코드로", 14, 400, "muted", "start")

# ---------------------------------------------------------------- write
for fg in FIGS:
    with open(os.path.join(OUT, fg.name + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(fg.svg())
print(len(FIGS), "figures written to", OUT)
