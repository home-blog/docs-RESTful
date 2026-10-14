# 2. 자원 중심 URL

## 2-1. 자원(Resource)이 뭔가요?

**자원은 API가 다루는 "대상"** 입니다. 문법으로 치면 **명사**예요.

블로그라면 이런 것들이 자원이에요.

- 글 (posts)
- 댓글 (comments)
- 회원 (users)
- 태그 (tags)

URL은 이 자원이 **어디 있는지** 가리키는 주소예요. 집 주소처럼요.

```text
/posts            → 글 전체 (글들이 모여 있는 곳)
/posts/42         → 42번 글 하나
/posts/42/comments → 42번 글에 달린 댓글들
```

## 2-2. 가장 중요한 규칙: URL에는 명사, 동사는 메서드로

> **"무엇을"은 URL에, "어떻게"는 HTTP 메서드에.**

| ❌ 나쁜 예 (URL에 동사) | ✅ 좋은 예 (명사 + 메서드) |
|---|---|
| `GET /getPosts` | `GET /posts` |
| `POST /createPost` | `POST /posts` |
| `POST /updatePost?id=42` | `PATCH /posts/42` |
| `GET /deletePost?id=42` | `DELETE /posts/42` |
| `GET /getCommentsOfPost?postId=42` | `GET /posts/42/comments` |

왜 동사를 빼야 할까요?

- 동사는 사람마다 다르게 써요. `get`, `fetch`, `find`, `list`, `select`... 끝이 없습니다.
- HTTP 메서드는 딱 다섯 개 정도로 정해져 있어서 **누구나 같은 뜻으로 읽어요.**
- 특히 `GET /deletePost?id=42` 처럼 **GET으로 지우는 API는 위험**합니다. 검색 로봇이나 미리보기 기능이 링크를 "열어 보기만" 해도 글이 지워질 수 있어요.

## 2-3. URL 작성 규칙 7가지

### ① 컬렉션은 복수형 명사

```text
✅ /posts   /users   /comments
❌ /post    /user    /comment
```

`/posts` 는 "글 보관함", `/posts/42` 는 "보관함 안의 42번". 복수형으로 쓰면 이 관계가 자연스럽게 읽혀요.

### ② 소문자, 단어 사이는 하이픈(-)

```text
✅ /blog-categories
❌ /blogCategories   /blog_categories   /BlogCategories
```

URL은 대소문자를 구분할 수 있어서 헷갈려요. 밑줄(_)은 링크에 밑줄이 그어지면 안 보입니다.

### ③ 계층 관계는 슬래시(/)로

```text
/posts/42/comments        42번 글의 댓글들
/posts/42/comments/7      42번 글의 7번 댓글
/users/7/posts            7번 회원이 쓴 글들
```

### ④ 중첩은 자원 두 개까지 (2단계)

```text
✅ /posts/{postId}/comments/{commentId}                       글 → 댓글 (2단계)
❌ /members/{memberId}/posts/{postId}/comments/{commentId}   회원 → 글 → 댓글 (3단계)
```

자원이 세 개 이상 이어지면 앞의 id를 모두 알아야 부를 수 있고, 서버도 단계마다 짝이 맞는지 확인해야 해요. **너무 깊으면 주소가 길고 바꾸기 어려워집니다.**

> 댓글 하나를 `/comments/7`처럼 댓글 id만으로 부르는 방식도 많이 써요. 둘 다 맞고, 팀이 하나로 정하면 돼요 ([예상 질문 Q17-1](10-예상-질문과-답.md#q17-1-comments7처럼-쓰는-곳도-있던데요)). 2단계는 무조건이 아니라 기본값이라서, GitHub 이슈처럼 위 id가 꼭 필요하면 더 깊어지기도 해요 ([Q17-2](10-예상-질문과-답.md#q17-2-그럼-2단계를-넘으면-안-되나요)).

### ⑤ 끝에 슬래시(/), 파일 확장자 붙이지 않기

```text
✅ /posts/42
❌ /posts/42/      ❌ /posts/42.json
```

어떤 형식으로 받을지는 URL이 아니라 **헤더**(`Accept: application/json`)로 말해요.

### ⑥ 필터·검색·정렬·페이지는 쿼리 스트링(?)으로

```text
✅ /posts?topic=travel&sort=createdAt,desc&page=0&size=20
❌ /posts/travel/sorted-by-date/page/1
```

### ⑦ 버전은 맨 앞에

```text
/api/v1/posts
/api/v2/posts     ← 응답 모양을 크게 바꿔야 할 때 새 버전을 만든다
```

이미 앱을 설치한 사용자는 옛날 API를 계속 부를 수 있어요. 그래서 크게 바꿀 때는 **새 주소(v2)를 만들고 옛 주소(v1)는 한동안 살려 둡니다.**

## 2-4. 경로 변수 vs 쿼리 스트링, 언제 뭘 쓰나요?

| | 경로 변수 `/posts/{id}` | 쿼리 스트링 `/posts?topic=travel` |
|---|---|---|
| 뜻 | **특정 하나**를 가리킨다 | 목록을 **어떻게 보고 싶은지** 조건을 단다 |
| 빠지면? | 다른 자원이 된다 (`/posts` ≠ `/posts/42`) | 조건 없이 전체를 본다 |
| 예 | 42번 글, 7번 회원 | 주제, 검색어, 정렬, 페이지 |

> 기억하기: **"누구냐"는 경로, "어떻게 보여 줄까"는 쿼리.**

## 2-5. 동사처럼 느껴지는 행동은 어떻게 하나요?

"좋아요 누르기", "글 발행하기", "주문 취소하기"는 딱 봐도 동사예요. 방법은 세 가지예요.

### 방법 1. 행동을 "자원"으로 바꿔 생각하기 (가장 추천)

**좋아요** → "좋아요"라는 자원을 만들고 지운다고 생각해요.

```text
PUT    /posts/42/likes/me     내 좋아요를 (있게) 만든다
DELETE /posts/42/likes/me     내 좋아요를 지운다
GET    /posts/42/likes        이 글의 좋아요 목록/수
```

> `PUT`을 쓴 이유: "좋아요"는 한 사람당 하나라서, 두 번 눌러도 결과가 같아야 해요(멱등). 3장에서 자세히 봅니다.

### 방법 2. 상태 필드를 바꾸기

**글 발행하기** → 글의 `status` 를 바꾼다고 생각해요.

```http
PATCH /posts/42
{ "status": "PUBLISHED" }
```

### 방법 3. 정말 자원으로 표현하기 어려우면, 행동 이름을 하위 경로로 (예외)

**주문 취소**처럼 돈 환불, 알림 발송 등 여러 일이 한꺼번에 일어나는 경우예요.

```text
POST /orders/1001/cancel
```

순수주의자는 싫어하지만 실무에서 꽤 씁니다. 대신 **꼭 필요할 때만, POST로만** 씁니다.

## 2-6. 블로그 API 전체 URL 설계 예시

| 메서드 | URL | 뜻 |
|---|---|---|
| GET | `/api/v1/posts` | 글 목록 (검색·정렬·페이지는 쿼리로) |
| POST | `/api/v1/posts` | 글 쓰기 |
| GET | `/api/v1/posts/{postId}` | 글 하나 보기 |
| PATCH | `/api/v1/posts/{postId}` | 글 일부 수정 |
| DELETE | `/api/v1/posts/{postId}` | 글 삭제 |
| GET | `/api/v1/posts/{postId}/comments` | 그 글의 댓글 목록 |
| POST | `/api/v1/posts/{postId}/comments` | 그 글에 댓글 쓰기 |
| DELETE | `/api/v1/comments/{commentId}` | 댓글 삭제 (댓글 번호만으로 충분) |
| PUT | `/api/v1/posts/{postId}/likes/me` | 좋아요 |
| DELETE | `/api/v1/posts/{postId}/likes/me` | 좋아요 취소 |
| GET | `/api/v1/users/me` | 내 정보 |
| GET | `/api/v1/users/{userId}/posts` | 그 회원이 쓴 글 |

## 2-7. 정리

- URL은 **명사(자원)**, 행동은 **HTTP 메서드**.
- **복수형, 소문자, 하이픈**, 중첩은 **자원 두 개(2단계)**까지.
- **"누구냐"는 경로**, **"어떻게 보여 줄까"는 쿼리 스트링**.
- 동사 같은 행동은 **자원으로 바꿔 생각**하고, 안 되면 예외로 `POST /…/행동`.

다음: [3. HTTP 메서드](03-HTTP-메서드.md)
