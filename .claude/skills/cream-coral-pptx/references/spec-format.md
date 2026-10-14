# 덱 스펙(JSON) 형식

`scripts/build_deck.js`가 읽는 JSON입니다. 전체 예시는 `assets/example-spec.json`(8장 + 예비 1장)에 있습니다.
상대 경로(이미지, curl 응답 파일)는 **스펙 파일이 있는 폴더 기준**입니다.

## 목차

1. 덱 전체 필드
2. 슬라이드 종류 (cover · section · content · closing)
3. 블록 종류 (text · table · code · http · inline · cards · callout · chart · image · badge · row)
4. 글자 조각과 색 이름
5. 높이와 넘침

---

## 1. 덱 전체 필드

| 필드 | 뜻 | 기본값 |
|---|---|---|
| `title` | 덱 제목 (파일 속성, 대본 제목) | — |
| `author` | 작성자 | — |
| `output` | 결과 .pptx 경로 | `deck.pptx` |
| `script` | 대본 .md 경로. `false`면 만들지 않음 | `<output>-대본.md` |
| `fonts` | `{head, body, mono}` | Noto Serif KR · Pretendard · JetBrains Mono |
| `themeName` | 테마 이름 | `Cream Coral` |
| `meta` | 대본 머리에 넣을 `{"키": "값"}` (일시, 대상, 길이 등) | — |
| `qa` | 예상 질문 `[["질문", "짧은 답"], …]` → 대본의 질문 대비 표 | — |
| `charsPerSecond` | 대사 속도(공백 포함 글자/초). 시간 배분 어림에 씀 | 5.5 |
| `slides` | 본 슬라이드 배열 | — |
| `spare` | 예비 슬라이드 배열. 맨 뒤 "예비" 섹션에 들어감 | — |
| `spareTitle` | 예비 섹션 이름 | `예비 (질문이 나오면)` |

모든 슬라이드 공통: `notes`(발표자 노트 = 대사, 빠지면 경고), `screen`(대본에 적을 화면 설명), `section`(섹션 이름을 직접 지정).
섹션은 `type: "section"` 슬라이드가 나올 때마다 그 제목으로 바뀝니다.

## 2. 슬라이드 종류

### cover (표지)

```json
{ "type": "cover", "title": "제목", "subtitle": "부제", "meta": "날짜 · 발표자",
  "terminal": ["$ curl -i /api/posts/1", ["HTTP/1.1 200", "success"]], "terminalLabel": "실제 응답", "notes": "…" }
```
`terminal`이 있으면 오른쪽에 다크 코드 창, 없으면 제목이 넓게 펼쳐집니다.

### section (섹션 구분, 다크)

```json
{ "type": "section", "num": "01", "title": "상태 코드", "desc": "한 줄 설명", "notes": "…" }
```

### content (본문, 기본값 — `type` 생략)

```json
{ "eyebrow": "STATUS CODE", "title": "한 문장 메시지", "badge": "curl -i", "blocks": [ … ], "notes": "…" }
```
- `eyebrow`: 제목 위 작은 영문 대문자 라벨. 예비 슬라이드에서 비우면 `APPENDIX`.
- `badge`: 오른쪽 위 회색 알약. 출처나 상태("예시", "실제 응답")를 적을 때.
- 블록은 제목 아래(1.73in)부터 위→아래로 0.25in 간격으로 쌓입니다. 블록마다 `gapAfter`로 간격 조정.

### closing (마무리, 다크)

```json
{ "type": "closing", "title": "정리", "rows": [["상태 코드", "실패는 4xx · 5xx로"], …], "notes": "…" }
```
왼쪽 키는 코랄, 오른쪽 값은 흰 글자. 7줄 이하.

## 3. 블록 종류

| kind | 필드 | 메모 |
|---|---|---|
| `text` | `lines`, `size`(20), `color`, `bold`, `gap`(6pt), `align` | 줄 = 문자열 또는 조각 배열 (4장) |
| `table` | `rows`(첫 줄 = 머리글), `colW`(비율), `mono`(고정폭 열 번호 배열), `status`(4xx·5xx를 빨갛게 칠할 열 번호, `true`=0번), `colorCol`, `colorRow`, `size`(16), `rowH` | 테두리는 가로 머리줄만. `×`는 자동으로 에러색 |
| `code` | `lines`, `label`, `size`(13), `h` | 줄 = 문자열 또는 `["문자열", "색 이름"]`. 다크 창 + 점 세 개 |
| `http` | `file`, `cmd`, `keep`(남길 머리글, 기본 Content-Type · Location), `label`, `size` | `curl -i` 결과 파일을 그대로 읽음. 상태 줄 2xx 초록 · 4xx/5xx 빨강, JSON 정렬, `"code"` 줄 앰버 |
| `inline` | `text`, `size`(16), `color`(coralText), `mono`(true) | 크림 카드 한 줄. URL · 한 줄 코드 · 한 줄 요약 |
| `cards` | `items[{kicker, title, code, body[], fill:"dark", kickerColor, titleSize, codeSize, bodySize}]`, `h`(2.1) | 같은 너비로 옆에 나란히. 비교에 씀 |
| `callout` | `text`, `size`(22) | 코랄 바탕 + 잉크 굵은 글자. **슬라이드당 하나, 덱 전체에서도 아껴 씀** |
| `chart` | `chartType`(bar · col · line · pie · doughnut), `labels`, `series[{name, values}]`, `title`, `format`, `highlight`(막대 하나만 코랄), `stacked`, `showPercent`, `colors`, `valueTitle`, `legendPos`, `h`(4.2) | **네이티브 차트** — PowerPoint에서 데이터 편집으로 숫자를 고칠 수 있음 |
| `image` | `path`, `cuts`(세로로 자를 비율, 예 `[0.5]` → 두 칸), `h` | 긴 스크린숏을 잘라 옆으로 나란히. 얇은 테두리 |
| `badge` | `text` | 본문 안 작은 알약 |
| `row` | `cols`(블록 배열), `widths`(비율), `h` | 옆으로 나란히. 높이는 가장 큰 칸에 맞춰짐 |

### 차트 메모

- 단일 계열 막대는 기본 잉크색이고 `highlight` 번호의 막대만 코랄입니다. 말하고 싶은 막대 하나만 칠하세요.
- 여러 계열 색 순서: 코랄 → 잉크 → 진한 코랄 → 회색 → 앰버 → 틸.
- 가로 막대(`bar`)는 `labels` 순서대로 위에서 아래로 그려집니다.
- 누적 막대 · 도넛 · 파이 안 숫자는 흰 굵은 14pt. 조각은 4개 이하가 읽기 좋습니다.
- **측정하지 않은 숫자를 넣을 때는 `title`이나 `badge`에 "예시"를 적습니다.**

## 4. 글자 조각과 색 이름

`text`의 `lines`와 `cards`의 `body` 줄은 문자열 또는 조각 배열입니다.

```json
"lines": [
  "그냥 한 줄",
  [["200으로 실패를 보내면 ", {}], ["오류율이 0%로 집계", {"color": "coralText", "bold": true}], ["됩니다.", {}]]
]
```
조각 옵션: `color`, `size`, `bold`, `italic`, `mono`.

색 이름 (HEX 6자리도 됨):

| 이름 | 값 | 쓰는 곳 |
|---|---|---|
| `ink` | 테마 글자1 #141413 | 제목 · 본문 강조 |
| `body` | #3D3D3A | 본문 |
| `muted` | 테마 강조3 #6C6A64 | 보조 |
| `mutedSoft` | #8E8B82 | 18pt 이상 주석만 |
| `coral` | 테마 강조1 #CC785C | 24pt 이상 굵은 글자, 다크 위 |
| `coralText` | 테마 강조2 #A9583E | 크림 위 본문 크기 코랄 강조 |
| `error` | 테마 강조6 #C64545 | 크림 위 에러 |
| `errorOnDark` | #E5806F | 다크 위 에러 (4xx · 5xx) |
| `success` | #5DB872 | 다크 위 2xx만 |
| `amber`, `teal` | 테마 강조4 · 5 | 다크 코드 안에서만 |
| `onDark`, `onDarkSoft` | #FAF9F5 · #A09D96 | 다크 위 글자 |
| `canvas`, `card`, `dark`, `hair`, `creamStrong`, `elevated` | 바탕색 | 도형 |

테마 색 슬롯으로 넣은 색은 PowerPoint의 디자인 › 변형 › 색에서 바꾸면 덱 전체가 따라 바뀝니다.

## 5. 높이와 넘침

- 쓸 수 있는 높이: 1.73in ~ 7.0in (약 5.27in).
- 엔진이 블록 높이를 어림해서, 남은 높이보다 크면 **줄여서 그리고 경고**를 냅니다. 경고가 나오면 블록을 줄이거나 슬라이드를 나눕니다.
- 어림 높이: text = 줄 수 × 글자 크기, table = 행 수 × 0.42in(16pt), code = 줄 수 × 0.23in(13pt) + 0.8, cards 2.1, callout 0.95, chart 4.2, image 4.8. `h`로 직접 정할 수 있습니다.
- 어림은 PowerPoint의 줄바꿈을 모릅니다. 긴 문장이 두 줄로 넘어가면 실제로 더 길어지므로 **반드시 렌더해서 눈으로 확인**합니다.
