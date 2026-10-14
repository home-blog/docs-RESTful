# 글결 API 문서

차례

- [1. 공통 약속](#overview)
  - [1.1. 주소와 버전](#_주소와_버전)
  - [1.2. 로그인 (서버 세션)](#_로그인_서버_세션)
  - [1.3. CSRF](#_csrf)
  - [1.4. 오류](#_오류)
- [2. 로그인](#auth)
  - [2.1. CSRF 토큰 받기](#auth-csrf)
  - [2.2. 이메일로 로그인](#auth-login)
  - [2.3. 지금 로그인한 회원](#auth-me)
  - [2.4. 로그아웃](#auth-logout)
- [3. 블로그·분류](#blog)
  - [3.1. 블로그 정보](#blog-read)
  - [3.2. 분류 목록](#category-list)
  - [3.3. 분류 추가](#category-create)
- [4. 글](#post)
  - [4.1. 글 쓰기](#post-create)
  - [4.2. 글 읽기](#post-read)
  - [4.3. 글 수정](#post-update)
  - [4.4. 글 삭제](#post-delete)
- [5. 둘러보기·검색](#explore)
  - [5.1. 한 블로그의 글 목록](#blog-posts)
  - [5.2. 글 검색](#post-search)
  - [5.3. 첫 화면 분량](#post-summary)
- [6. 댓글·좋아요](#reaction)
  - [6.1. 댓글 쓰기](#comment-create)
  - [6.2. 댓글 목록](#comment-list)
  - [6.3. 댓글 삭제](#comment-delete)
  - [6.4. 좋아요](#post-like)
- [7. 블로그 관리](#manage)
  - [7.1. 대시보드](#manage-dashboard)
- [8. 오류 예시](#errors)
  - [8.1. 입력값 오류 (400)](#error-validation)
  - [8.2. 로그인 필요 (401)](#error-unauthenticated)
  - [8.3. 없는 글 (404)](#error-not-found)

여러 사람이 각자 블로그를 쓰고 한곳에서 둘러보는 멀티 블로그 서비스 **글결** 의 서버 API입니다 (릴리스 0.5.2).

이 문서의 요청과 응답은 **테스트가 실제로 보내고 받은 것** 입니다 (Spring REST Docs, `ApiDocumentationTest`). 응답에 문서에 없는 칸이 생기거나 적은 칸이 사라지면 테스트가 실패하므로, 문서가 코드와 어긋나지 않습니다. 전체 API 목록(61개)은 개발 서버의 Swagger 화면(`/swagger-ui.html`)에 있고, 이 문서는 주요 흐름을 예시와 함께 설명합니다.

## [1. 공통 약속](#overview)

### [1.1. 주소와 버전](#_주소와_버전)

모든 주소는 `/api/v1/…` 입니다. API 버전은 릴리스 번호와 따로 가서, 칸을 더하는 변경은 v1 그대로 두고 칸을 빼거나 뜻을 바꿀 때만 v2를 엽니다.

### [1.2. 로그인 (서버 세션)](#_로그인_서버_세션)

로그인하면 세션 쿠키 `SESSION` 이 생기고, 세션은 PostgreSQL에 저장합니다 (JWT를 쓰지 않습니다). 7일 동안 쓰지 않으면 끝납니다. 로그인이 필요한 API를 로그인 없이 부르면 `401` 입니다.

### [1.3. CSRF](#_csrf)

GET이 아닌 요청은 쿠키 `XSRF-TOKEN` 의 값을 머리글 `X-XSRF-TOKEN` 에 실어 보냅니다. 토큰은 [CSRF 토큰 받기](#auth-csrf) 로 받고, 로그인하면 바뀌므로 로그인한 뒤 다시 받습니다.

### [1.4. 오류](#_오류)

모든 오류는 같은 모양입니다. 볼 권한이 없는 글·댓글·이미지는 있는지조차 알 수 없도록 없는 것과 같은 `404` 로 답합니다.

| 상태 | 뜻 |
| --- | --- |
| `400` | 입력값이 규칙에 맞지 않음 (`fieldErrors` 에 칸마다 까닭) |
| `401` | 로그인이 필요함 |
| `403` | CSRF 토큰이 없거나 틀림, 또는 할 수 없는 일 |
| `404` | 없거나 볼 수 없음 |
| `409` | 이미 있음 (예: 같은 이름의 분류) |
| `429` | 너무 자주 보냄 (`retryAfterSeconds` 뒤에 다시) |

## [2. 로그인](#auth)

### [2.1. CSRF 토큰 받기](#auth-csrf)

화면이 처음 열릴 때와 로그인한 뒤에 부릅니다.

#### [2.1.1. 요청](#auth-csrf_http_request)

```http
GET /api/v1/auth/csrf HTTP/1.1
Host: geulgyeol.java21.net
```

#### [2.1.2. 응답](#auth-csrf_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: XSRF-TOKEN=ebe06e29-3651-48ba-8979-79dd1f2af849; Path=/; Secure; HttpOnly
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 147

{
  "headerName" : "X-XSRF-TOKEN",
  "token" : "IzrTqx3yW5UxigkuRtcOXY8cTjLqdV6ectrjfe1hKSpfMHdFRli2myuXaawcuT8bd_o6Ze19YwrTQmezReOHGdwHG0s5CEN8"
}
```

#### [2.1.3. 응답 칸](#auth-csrf_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `headerName` | `String` | 토큰을 실을 머리글 이름 (`X-XSRF-TOKEN`) |
| `token` | `String` | 머리글에 실을 값. 같은 값이 쿠키 \`XSRF-TOKEN\`에도 들어온다 |

### [2.2. 이메일로 로그인](#auth-login)

성공하면 세션 쿠키 `SESSION` 이 생깁니다. 비밀번호를 5번 틀리면 10분 동안 잠깁니다.

#### [2.2.1. 요청 머리글](#auth-login_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [2.2.2. 요청 본문 칸](#auth-login_request_fields)

| Path | Type | Description |
| --- | --- | --- |
| `email` | `String` | 가입한 이메일 |
| `password` | `String` | 비밀번호. 5번 틀리면 10분 동안 잠긴다 |

#### [2.2.3. 요청](#auth-login_http_request)

```http
POST /api/v1/auth/login HTTP/1.1
Content-Type: application/json
X-XSRF-TOKEN: JZV3vEYxRHabnlbwpI2J4i8vkVQPBHNZCRC83YbIOotZ0LDMQ6YWjyBTJkS2rWPGnKC90kkdvGw-YUB0MSDe5b-uWLNrtIOt
Content-Length: 69
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=f3a3fbb2-3568-40f2-81e3-80b89fb82d3a

{
  "email" : "docs24700175@example.com",
  "password" : "abcd123!"
}
```

#### [2.2.4. 응답](#auth-login_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 71

{
  "member" : {
    "id" : 10736,
    "nickname" : "docs2470017"
  }
}
```

#### [2.2.5. 응답 칸](#auth-login_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `member.id` | `Number` | 회원 번호 |
| `member.nickname` | `String` | 닉네임 (2\~10자, 한글·영문·숫자) |

### [2.3. 지금 로그인한 회원](#auth-me)

화면이 처음 열릴 때 로그인 상태를 묻습니다. 로그인하지 않았으면 `401` 입니다.

#### [2.3.1. 요청](#auth-me_http_request)

```http
GET /api/v1/auth/me HTTP/1.1
Host: geulgyeol.java21.net
```

#### [2.3.2. 응답](#auth-me_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: SESSION=Nw==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:43 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 71

{
  "member" : {
    "id" : 10745,
    "nickname" : "docsb653e32"
  }
}
```

#### [2.3.3. 응답 칸](#auth-me_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `member.id` | `Number` | 회원 번호 |
| `member.nickname` | `String` | 닉네임 (2\~10자, 한글·영문·숫자) |

### [2.4. 로그아웃](#auth-logout)

세션을 지우고 쿠키를 만료시킵니다.

#### [2.4.1. 요청 머리글](#auth-logout_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [2.4.2. 요청](#auth-logout_http_request)

```http
POST /api/v1/auth/logout HTTP/1.1
X-XSRF-TOKEN: ZJSQLQEAuj0T8pqTBCBpQZuoyAqnt-_H4fPtWU7TOdRxhE9QBqGlTDcy3gk-lP-mMg1dcqqe5Wieg9jq1JKJb3zrDrdCt3wy
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=b55a62d4-fe56-4316-b947-5ad6287c333b
```

#### [2.4.3. 응답](#auth-logout_http_response)

```http
HTTP/1.1 204 No Content
Set-Cookie: SESSION=MTM=; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:45 GMT; HttpOnly; SameSite=Lax
Set-Cookie: SESSION=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure
Set-Cookie: XSRF-TOKEN=; Path=/; Max-Age=0; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Secure; HttpOnly
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
```

## [3. 블로그·분류](#blog)

회원마다 블로그가 하나 있고, 블로그 안의 분류는 비공개로 둘 수 있습니다 (비공개 분류의 글은 주인만 봅니다).

### [3.1. 블로그 정보](#blog-read)

누구나 부릅니다. 방문자 수에 셉니다.

#### [3.1.1. 주소 안의 값](#blog-read_path_parameters)

Table 1. /api/v1/blogs/{blogId}

| Parameter | Description |
| --- | --- |
| `blogId` | 블로그 번호 |

#### [3.1.2. 요청](#blog-read_http_request)

```http
GET /api/v1/blogs/10006 HTTP/1.1
Host: geulgyeol.java21.net
```

#### [3.1.3. 응답](#blog-read_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: MYBLOG_VISITOR=a54761567a9600fdf8de6042c9a1e7be; Path=/; Max-Age=31536000; Expires=Thu, 14 Oct 2027 05:30:40 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 98

{
  "blogId" : 10006,
  "name" : "docsb125d82의 블로그",
  "intro" : "",
  "isOwner" : false
}
```

#### [3.1.4. 응답 칸](#blog-read_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `blogId` | `Number` | 블로그 번호 |
| `name` | `String` | 블로그 이름 (1\~30자) |
| `intro` | `String` | 블로그 소개 (0\~200자) |
| `isOwner` | `Boolean` | 보는 사람이 이 블로그의 주인인지 |

### [3.2. 분류 목록](#category-list)

#### [3.2.1. 주소 안의 값](#category-list_path_parameters)

Table 1. /api/v1/blogs/{blogId}/categories

| Parameter | Description |
| --- | --- |
| `blogId` | 블로그 번호 |

#### [3.2.2. 요청](#category-list_http_request)

```http
GET /api/v1/blogs/10004/categories HTTP/1.1
Host: geulgyeol.java21.net
```

#### [3.2.3. 응답](#category-list_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 177

{
  "categories" : [ {
    "categoryId" : 11863,
    "name" : "미분류",
    "postCount" : 0,
    "isDefault" : true,
    "visibility" : "public",
    "colorIndex" : 0
  } ]
}
```

#### [3.2.4. 응답 칸](#category-list_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `categories[]` | `Array` | 분류 목록 (주인이 정한 순서). 방문자에게는 비공개 분류가 빠진다 |
| `categories[].categoryId` | `Number` | 분류 번호 |
| `categories[].name` | `String` | 분류 이름 |
| `categories[].postCount` | `Number` | 이 분류의 글 수 (보는 사람이 볼 수 있는 글만) |
| `categories[].isDefault` | `Boolean` | "미분류"인지 (지울 수 없다) |
| `categories[].visibility` | `String` | `public` 또는 `private` |
| `categories[].colorIndex` | `Number` | 화면에서 쓸 분류 색 번호 (0\~5) |

### [3.3. 분류 추가](#category-create)

#### [3.3.1. 요청 머리글](#category-create_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [3.3.2. 요청 본문 칸](#category-create_request_fields)

| Path | Type | Description |
| --- | --- | --- |
| `name` | `String` | 분류 이름 (1\~20자, 내 블로그 안에서 겹치지 않게) |
| `visibility` | `String` | `public` 또는 `private`. 비공개 분류의 글은 주인만 본다 |

#### [3.3.3. 요청](#category-create_http_request)

```http
POST /api/v1/me/blog/categories HTTP/1.1
Content-Type: application/json
X-XSRF-TOKEN: lX5pMh-14C5u-wDUF8niV88SjJliFfS7E9LdhV6TDXrLSS1ArR0NVi-D1BtDzWHnIeTWYKkhoaEDJ5eWd-O85z33NEuqLxxx
Content-Length: 57
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=8cdd0645-6a36-47f3-8a2c-d1abcd91af11

{
  "name" : "여행 기록",
  "visibility" : "public"
}
```

#### [3.3.4. 응답](#category-create_http_response)

```http
HTTP/1.1 201 Created
Set-Cookie: SESSION=MQ==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:40 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 143

{
  "categoryId" : 11865,
  "name" : "여행 기록",
  "postCount" : 0,
  "isDefault" : false,
  "visibility" : "public",
  "colorIndex" : 1
}
```

#### [3.3.5. 응답 칸](#category-create_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `categoryId` | `Number` | 분류 번호 |
| `name` | `String` | 분류 이름 |
| `postCount` | `Number` | 이 분류의 글 수 (보는 사람이 볼 수 있는 글만) |
| `isDefault` | `Boolean` | "미분류"인지 (지울 수 없다) |
| `visibility` | `String` | `public` 또는 `private` |
| `colorIndex` | `Number` | 화면에서 쓸 분류 색 번호 (0\~5) |

## [4. 글](#post)

### [4.1. 글 쓰기](#post-create)

본문은 마크다운이고, HTML은 글자 그대로 보입니다. 새 글이면 `201`, 같은 `requestKey` 로 이미 만든 글이면 `200` 입니다.

#### [4.1.1. 요청 머리글](#post-create_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [4.1.2. 요청 본문 칸](#post-create_request_fields)

| Path | Type | Description |
| --- | --- | --- |
| `title` | `String` | 제목 (1\~100자) |
| `content` | `String` | 본문 마크다운 (1\~10,000자) |
| `categoryId` | `Number` | 내 블로그의 분류 번호 |
| `topicId` | `Number` | 주제 번호 (여행·음식·취미·운동·개발) |
| `visibility` | `String` | `public` 또는 `private` |
| `tags[]` | `Array` | 태그 (0\~5개). 보낸 목록이 새 전체 목록이다 |
| `requestKey` | `String` | 글쓰기 화면을 열 때 만든 1회용 번호 (36자까지). 같은 번호로 다시 보내면 새 글을 만들지 않고 200으로 같은 글 번호를 돌려준다 |

#### [4.1.3. curl](#post-create_curl_request)

```bash
$ curl 'https://geulgyeol.java21.net/api/v1/posts' -i -X POST \
    -H 'Content-Type: application/json' \
    -H 'X-XSRF-TOKEN: PHxn9yP0HuCKdU-Z4DOK5Os6Kg4eUWjnp6FmquAw0AtPLncYBEQGkheXeNCnTX6r1x6-gNJZB294ZFHKksBTmdNR6D8uFk8h' \
    --cookie 'XSRF-TOKEN=88ae4cf0-8127-4d9c-af59-5a533a84a889' \
    -d '{
  "title" : "제주 올레 7코스 걷기",
  "content" : "## 걷기 좋은 날\n\n바다를 보며 **3시간** 걸었다.",
  "categoryId" : 11880,
  "topicId" : 1,
  "visibility" : "public",
  "requestKey" : "9f1c2e7a-4b3d-4c8e-9a51-2d6f0b7e1c33",
  "tags" : [ "제주", "걷기" ]
}'
```

#### [4.1.4. 응답](#post-create_http_response)

```http
HTTP/1.1 201 Created
Set-Cookie: SESSION=MTA=; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:44 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 22

{
  "postId" : 21061
}
```

#### [4.1.5. 응답 칸](#post-create_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `postId` | `Number` | 글 번호 |

### [4.2. 글 읽기](#post-read)

누구나 부릅니다. 볼 수 없는 글(비공개)은 없는 글과 같은 `404` 입니다. 조회수에 셉니다.

#### [4.2.1. 주소 안의 값](#post-read_path_parameters)

Table 1. /api/v1/posts/{postId}

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호 |

#### [4.2.2. 요청](#post-read_http_request)

```http
GET /api/v1/posts/21062 HTTP/1.1
Host: geulgyeol.java21.net
```

#### [4.2.3. 응답](#post-read_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: MYBLOG_VISITOR=1195d8bfda2bfc15ba57f450eac0f396; Path=/; Max-Age=31536000; Expires=Thu, 14 Oct 2027 05:30:44 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 652

{
  "postId" : 21062,
  "blogId" : 10021,
  "blogName" : "docs345bb82의 블로그",
  "category" : {
    "categoryId" : 11881,
    "name" : "미분류",
    "visibility" : "public"
  },
  "topic" : {
    "topicId" : 1,
    "name" : "여행"
  },
  "title" : "제주 올레 7코스 걷기",
  "content" : "## 걷기 좋은 날\n\n바다를 보며 **3시간** 걸었다.",
  "visibility" : "public",
  "createdAt" : "2026-10-14T05:30:44.198833Z",
  "updatedAt" : null,
  "prevPostId" : null,
  "nextPostId" : null,
  "isOwner" : false,
  "commentCount" : 0,
  "likeCount" : 0,
  "likedByMe" : false,
  "tags" : [ ],
  "sheets" : 1,
  "readMinutes" : 1
}
```

#### [4.2.4. 응답 칸](#post-read_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `postId` | `Number` | 글 번호 |
| `blogId` | `Number` | 블로그 번호 |
| `blogName` | `String` | 블로그 이름 |
| `category.categoryId` | `Number` | 분류 번호 |
| `category.name` | `String` | 분류 이름 |
| `category.visibility` | `String` | 분류 공개 범위 |
| `topic.topicId` | `Number` | 주제 번호 |
| `topic.name` | `String` | 주제 (여행·음식·취미·운동·개발) |
| `title` | `String` | 제목 |
| `content` | `String` | 본문 (마크다운. HTML은 글자 그대로 보인다) |
| `visibility` | `String` | `public` 또는 `private` |
| `createdAt` | `String` | 쓴 시각 (UTC, ISO 8601) |
| `updatedAt` | `String` | 고친 시각. 고친 적 없으면 null |
| `prevPostId` | `Number` | 같은 블로그의 이전 글 번호 (보는 사람이 볼 수 있는 글 중) |
| `nextPostId` | `Number` | 다음 글 번호 |
| `isOwner` | `Boolean` | 보는 사람이 글쓴이인지 (수정·삭제 버튼) |
| `commentCount` | `Number` | 댓글 수 |
| `likeCount` | `Number` | 좋아요 수 |
| `likedByMe` | `Boolean` | 보는 사람이 좋아요를 눌렀는지 |
| `tags[]` | `Array` | 태그 (0\~5개) |
| `sheets` | `Number` | 200자 원고지로 몇 매인지 (올림) |
| `readMinutes` | `Number` | 읽는 데 걸리는 분 (1분에 500자, 올림) |

### [4.3. 글 수정](#post-update)

#### [4.3.1. 요청 머리글](#post-update_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [4.3.2. 주소 안의 값](#post-update_path_parameters)

Table 1. /api/v1/posts/{postId}

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호 (내 글만) |

#### [4.3.3. 요청 본문 칸](#post-update_request_fields)

| Path | Type | Description |
| --- | --- | --- |
| `title` | `String` | 제목 (1\~100자) |
| `content` | `String` | 본문 마크다운 (1\~10,000자) |
| `categoryId` | `Number` | 내 블로그의 분류 번호 |
| `topicId` | `Number` | 주제 번호 (여행·음식·취미·운동·개발) |
| `visibility` | `String` | `public` 또는 `private` |
| `tags[]` | `Array` | 태그 (0\~5개). 보낸 목록이 새 전체 목록이다 |

#### [4.3.4. 요청](#post-update_http_request)

```http
PUT /api/v1/posts/21060 HTTP/1.1
Content-Type: application/json
X-XSRF-TOKEN: lDI0XRyb4JmIPbK2RL0_QILttbH7Dl8bJnLlpogk7CBla2xfpQIFan-u0K6lD4OOc5ALcOSMmIifPjs2FhTdwOoW3hRdUl1p
Content-Length: 280
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=1017c507-2187-40fa-9d0d-0f8fb2248916

{
  "title" : "제주 올레 7코스 걷기 (사진 추가)",
  "content" : "## 걷기 좋은 날\n\n바다를 보며 **3시간** 걸었다.\n\n사진을 더했다.",
  "categoryId" : 11879,
  "topicId" : 1,
  "visibility" : "public",
  "tags" : [ "제주", "걷기", "바다" ]
}
```

#### [4.3.5. 응답](#post-update_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: SESSION=OQ==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:43 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 92

{
  "postId" : 21060,
  "changed" : true,
  "updatedAt" : "2026-10-14T05:30:43.770928934Z"
}
```

#### [4.3.6. 응답 칸](#post-update_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `postId` | `Number` | 글 번호 |
| `changed` | `Boolean` | 실제로 바뀐 것이 있는지. 같은 내용이면 false이고 고친 시각도 그대로 |
| `updatedAt` | `String` | 고친 시각 |

### [4.4. 글 삭제](#post-delete)

#### [4.4.1. 요청 머리글](#post-delete_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [4.4.2. 주소 안의 값](#post-delete_path_parameters)

Table 1. /api/v1/posts/{postId}

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호 (내 글만). 댓글·좋아요·이미지·태그도 함께 지운다 |

#### [4.4.3. 요청](#post-delete_http_request)

```http
DELETE /api/v1/posts/21059 HTTP/1.1
X-XSRF-TOKEN: Nbu57z0ic2dTESBg67QhN33qeZNOea3tDN-xqby0ZzDrx3ROUd6Pjl4XQQJ-KRFUipkVBEnaVPEtT5_AP72JzInSUwjSpU14
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=de6ac52e-814a-4340-bc62-3b8e5f489b96
```

#### [4.4.4. 응답](#post-delete_http_response)

```http
HTTP/1.1 204 No Content
Set-Cookie: SESSION=OA==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:43 GMT; HttpOnly; SameSite=Lax
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
```

## [5. 둘러보기·검색](#explore)

### [5.1. 한 블로그의 글 목록](#blog-posts)

방문자는 공개 글, 주인은 비공개 글까지 봅니다.

#### [5.1.1. 주소 안의 값](#blog-posts_path_parameters)

Table 1. /api/v1/blogs/{blogId}/posts

| Parameter | Description |
| --- | --- |
| `blogId` | 블로그 번호 |

#### [5.1.2. 물음표 뒤의 값](#blog-posts_query_parameters)

| Parameter | Description |
| --- | --- |
| `page` | 쪽 번호 (1부터, 숫자가 아니면 1쪽) |
| `categoryId` | 이 분류의 글만 |

#### [5.1.3. 요청](#blog-posts_http_request)

```http
GET /api/v1/blogs/10022/posts?page=1 HTTP/1.1
Host: geulgyeol.java21.net
```

#### [5.1.4. 응답](#blog-posts_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 856

{
  "blogId" : 10022,
  "isOwner" : false,
  "categoryId" : null,
  "totalCount" : 2,
  "page" : 1,
  "totalPages" : 1,
  "pageSize" : 10,
  "posts" : [ {
    "postId" : 21064,
    "title" : "성산일출봉 새벽 산책",
    "categoryId" : 11882,
    "categoryName" : "미분류",
    "createdAt" : "2026-10-14T05:30:44.397452Z",
    "preview" : "걷기 좋은 날 바다를 보며 3시간 걸었다.",
    "visibility" : "public",
    "sheets" : 1,
    "readMinutes" : 1,
    "thumbnail" : null
  }, {
    "postId" : 21063,
    "title" : "제주 올레 7코스 걷기",
    "categoryId" : 11882,
    "categoryName" : "미분류",
    "createdAt" : "2026-10-14T05:30:44.396354Z",
    "preview" : "걷기 좋은 날 바다를 보며 3시간 걸었다.",
    "visibility" : "public",
    "sheets" : 1,
    "readMinutes" : 1,
    "thumbnail" : null
  } ]
}
```

#### [5.1.5. 응답 칸](#blog-posts_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `blogId` | `Number` | 블로그 번호 |
| `isOwner` | `Boolean` | 보는 사람이 주인인지 (주인은 비공개 글까지 본다) |
| `categoryId` | `Number` | 고른 분류 번호. 없으면 null |
| `totalCount` | `Number` | 전체 글 수 |
| `page` | `Number` | 지금 쪽 번호 |
| `totalPages` | `Number` | 전체 쪽 수 |
| `pageSize` | `Number` | 한 쪽의 글 수 |
| `posts[]` | `Array` | 글 목록 (최신순) |
| `posts[].postId` | `Number` | 글 번호 |
| `posts[].title` | `String` | 제목 |
| `posts[].categoryId` | `Number` | 분류 번호 |
| `posts[].categoryName` | `String` | 분류 이름 |
| `posts[].createdAt` | `String` | 쓴 시각 |
| `posts[].preview` | `String` | 본문 앞부분 (마크다운 기호를 뺀 글자) |
| `posts[].thumbnail` | `String` | 본문의 첫 이미지 주소. 없으면 null |
| `posts[].visibility` | `String` | `public` 또는 `private` |
| `posts[].sheets` | `Number` | 원고지 매수 |
| `posts[].readMinutes` | `Number` | 읽는 시간(분) |

### [5.2. 글 검색](#post-search)

#### [5.2.1. 물음표 뒤의 값](#post-search_query_parameters)

| Parameter | Description |
| --- | --- |
| `q` | 검색어 (2자 이상). 공개 글의 제목·본문에서 찾는다 |
| `page` | 쪽 번호 (1부터) |

#### [5.2.2. 요청](#post-search_http_request)

```http
GET /api/v1/search/posts?q=%EA%B8%80%EA%B2%B0%EB%AC%B8%EC%84%9C&page=1 HTTP/1.1
Host: geulgyeol.java21.net
```

#### [5.2.3. 응답](#post-search_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 484

{
  "keyword" : "글결문서",
  "totalCount" : 1,
  "page" : 1,
  "totalPages" : 1,
  "pageSize" : 10,
  "results" : [ {
    "postId" : 21058,
    "blogId" : 10017,
    "blogName" : "docs35bef9d의 블로그",
    "title" : "글결문서 예시: 제주 올레 7코스",
    "categoryId" : 11877,
    "categoryName" : "미분류",
    "createdAt" : "2026-10-14T05:30:43.191572Z",
    "preview" : "걷기 좋은 날 바다를 보며 3시간 걸었다.",
    "thumbnail" : null
  } ]
}
```

#### [5.2.4. 응답 칸](#post-search_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `keyword` | `String` | 다듬은 검색어 |
| `totalCount` | `Number` | 전체 글 수 |
| `page` | `Number` | 지금 쪽 번호 |
| `totalPages` | `Number` | 전체 쪽 수 |
| `pageSize` | `Number` | 한 쪽의 글 수 |
| `results[]` | `Array` | 찾은 글 (최신순) |
| `results[].postId` | `Number` | 글 번호 |
| `results[].title` | `String` | 제목 |
| `results[].categoryId` | `Number` | 분류 번호 |
| `results[].categoryName` | `String` | 분류 이름 |
| `results[].createdAt` | `String` | 쓴 시각 |
| `results[].preview` | `String` | 본문 앞부분 (마크다운 기호를 뺀 글자) |
| `results[].thumbnail` | `String` | 본문의 첫 이미지 주소. 없으면 null |
| `results[].blogId` | `Number` | 블로그 번호 |
| `results[].blogName` | `String` | 블로그 이름 |

### [5.3. 첫 화면 분량](#post-summary)

첫 화면 머리의 "원고지 표지"에 쓰는 숫자입니다.

#### [5.3.1. 요청](#post-summary_http_request)

```http
GET /api/v1/posts/summary HTTP/1.1
Host: geulgyeol.java21.net
```

#### [5.3.2. 응답](#post-summary_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 64

{
  "bloggerCount" : 12,
  "postCount" : 108,
  "sheets" : 473
}
```

#### [5.3.3. 응답 칸](#post-summary_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `bloggerCount` | `Number` | 공개 글이 있는 블로그 수 |
| `postCount` | `Number` | 공개 글 수 |
| `sheets` | `Number` | 공개 글 전체의 원고지 매수 (글마다 200자에 1매로 올림해 더함, 5분 동안 캐시) |

## [6. 댓글·좋아요](#reaction)

### [6.1. 댓글 쓰기](#comment-create)

#### [6.1.1. 요청 머리글](#comment-create_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [6.1.2. 주소 안의 값](#comment-create_path_parameters)

Table 1. /api/v1/posts/{postId}/comments

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호 |

#### [6.1.3. 요청 본문 칸](#comment-create_request_fields)

| Path | Type | Description |
| --- | --- | --- |
| `body` | `String` | 댓글 (1\~500자). 같은 회원은 5초에 한 번. 수정은 없다 |

#### [6.1.4. 요청](#comment-create_http_request)

```http
POST /api/v1/posts/21057/comments HTTP/1.1
Content-Type: application/json
X-XSRF-TOKEN: Ef4zcw7HHVMKJgTBs4U61pJby-oIC5nXH7vlIpd-APpIqp8tdc9SFW-kK2AnEzHxg6gO7qFt5tM8aqj6LN_RG_JLMZ9xnfsd
Content-Length: 84
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=d1afac63-5500-4836-94a1-3d49e51e97d0

{
  "body" : "저도 지난달에 걸었는데 바다 색이 정말 좋았어요."
}
```

#### [6.1.5. 응답](#comment-create_http_response)

```http
HTTP/1.1 201 Created
Set-Cookie: SESSION=Ng==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:42 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 265

{
  "id" : 4307,
  "author" : {
    "id" : 10744,
    "nickname" : "read33de844",
    "withdrawn" : false
  },
  "body" : "저도 지난달에 걸었는데 바다 색이 정말 좋았어요.",
  "createdAt" : "2026-10-14T05:30:42.829090313Z",
  "canDelete" : true
}
```

#### [6.1.6. 응답 칸](#comment-create_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `id` | `Number` | 댓글 번호 |
| `author.id` | `Number` | 쓴 회원 번호 |
| `author.nickname` | `String` | 쓴 회원 닉네임 (탈퇴했으면 "탈퇴한 회원") |
| `author.withdrawn` | `Boolean` | 쓴 회원이 탈퇴했는지 |
| `body` | `String` | 댓글 |
| `createdAt` | `String` | 쓴 시각 |
| `canDelete` | `Boolean` | 보는 사람이 지울 수 있는지 (쓴 사람이나 블로그 주인) |

### [6.2. 댓글 목록](#comment-list)

#### [6.2.1. 주소 안의 값](#comment-list_path_parameters)

Table 1. /api/v1/posts/{postId}/comments

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호 |

#### [6.2.2. 요청](#comment-list_http_request)

```http
GET /api/v1/posts/21055/comments HTTP/1.1
Host: geulgyeol.java21.net
```

#### [6.2.3. 응답](#comment-list_http_response)

```http
HTTP/1.1 200 OK
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 324

{
  "count" : 1,
  "comments" : [ {
    "id" : 4305,
    "author" : {
      "id" : 10740,
      "nickname" : "readf9f03b9",
      "withdrawn" : false
    },
    "body" : "저도 지난달에 걸었는데 바다 색이 정말 좋았어요.",
    "createdAt" : "2026-10-14T05:30:42.112979150Z",
    "canDelete" : false
  } ]
}
```

#### [6.2.4. 응답 칸](#comment-list_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `count` | `Number` | 댓글 수 |
| `comments[]` | `Array` | 댓글 (쓴 순서) |
| `comments[].id` | `Number` | 댓글 번호 |
| `comments[].author.id` | `Number` | 쓴 회원 번호 |
| `comments[].author.nickname` | `String` | 쓴 회원 닉네임 (탈퇴했으면 "탈퇴한 회원") |
| `comments[].author.withdrawn` | `Boolean` | 쓴 회원이 탈퇴했는지 |
| `comments[].body` | `String` | 댓글 |
| `comments[].createdAt` | `String` | 쓴 시각 |
| `comments[].canDelete` | `Boolean` | 보는 사람이 지울 수 있는지 (쓴 사람이나 블로그 주인) |

### [6.3. 댓글 삭제](#comment-delete)

#### [6.3.1. 요청 머리글](#comment-delete_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [6.3.2. 주소 안의 값](#comment-delete_path_parameters)

Table 1. /api/v1/comments/{commentId}

| Parameter | Description |
| --- | --- |
| `commentId` | 댓글 번호. 쓴 사람이나 그 블로그 주인만 지운다 (아니면 404) |

#### [6.3.3. 요청](#comment-delete_http_request)

```http
DELETE /api/v1/comments/4306 HTTP/1.1
X-XSRF-TOKEN: axGaxzCvOBz9OixhznIOjyAFSpcuMab1Jy-9W_OT8sSjgJIPCSL49wKfXS3QDhsD9186uUFhZ_VMV5HYQUuJPcDxx_ySsKNt
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=b3b020e1-47b9-46ad-bbf7-fd4f3b58101b
```

#### [6.3.4. 응답](#comment-delete_http_response)

```http
HTTP/1.1 204 No Content
Set-Cookie: SESSION=NQ==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:42 GMT; HttpOnly; SameSite=Lax
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
```

### [6.4. 좋아요](#post-like)

취소는 같은 주소에 `DELETE` 입니다.

#### [6.4.1. 요청 머리글](#post-like_request_headers)

| Name | Description |
| --- | --- |
| `X-XSRF-TOKEN` | CSRF 토큰 (\`GET /api/v1/auth/csrf\`로 받은 값, 쿠키 \`XSRF-TOKEN\`과 함께 보낸다) |

#### [6.4.2. 주소 안의 값](#post-like_path_parameters)

Table 1. /api/v1/posts/{postId}/like

| Parameter | Description |
| --- | --- |
| `postId` | 글 번호. 자기 글에는 누를 수 없다 |

#### [6.4.3. 요청](#post-like_http_request)

```http
PUT /api/v1/posts/21054/like HTTP/1.1
X-XSRF-TOKEN: oXuOJ3wIiRWDH29WbxOQG32-QJT4IgBRpn0RTiMjMypqgAK3lR-7Fkg5uiyueQ1lWj6kIx6PbfXBFDR8khxwLBsWBU5ctmGP
Host: geulgyeol.java21.net
Cookie: XSRF-TOKEN=4d514139-fb35-48c1-a964-4aab856d66c8
```

#### [6.4.4. 응답](#post-like_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: SESSION=Mw==; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:41 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 43

{
  "likeCount" : 1,
  "likedByMe" : true
}
```

#### [6.4.5. 응답 칸](#post-like_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `likeCount` | `Number` | 좋아요 수 |
| `likedByMe` | `Boolean` | 내가 눌렀는지 (여러 번 눌러도 한 번으로 센다) |

## [7. 블로그 관리](#manage)

### [7.1. 대시보드](#manage-dashboard)

로그인한 회원의 블로그 숫자입니다. 블로그 번호는 주소로 받지 않고 세션의 회원으로 정합니다.

#### [7.1.1. 요청](#manage-dashboard_http_request)

```http
GET /api/v1/manage/dashboard HTTP/1.1
Host: geulgyeol.java21.net
```

#### [7.1.2. 응답](#manage-dashboard_http_response)

```http
HTTP/1.1 200 OK
Set-Cookie: SESSION=MTI=; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:44 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 2490

{
  "views" : {
    "today" : 0,
    "yesterday" : 0,
    "total" : 0
  },
  "visitors" : {
    "today" : 0,
    "yesterday" : 0,
    "total" : 0
  },
  "newCommentCount" : 0,
  "chart" : [ {
    "date" : "2026-09-15",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-16",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-17",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-18",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-19",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-20",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-21",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-22",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-23",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-24",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-25",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-26",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-27",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-28",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-29",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-09-30",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-01",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-02",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-03",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-04",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-05",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-06",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-07",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-08",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-09",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-10",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-11",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-12",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-13",
    "views" : 0,
    "visitors" : 0
  }, {
    "date" : "2026-10-14",
    "views" : 0,
    "visitors" : 0
  } ],
  "popularPosts" : [ ],
  "recentPosts" : [ {
    "postId" : 21065,
    "title" : "제주 올레 7코스 걷기",
    "createdAt" : "2026-10-14T05:30:44.871238Z",
    "visibility" : "public"
  } ]
}
```

#### [7.1.3. 응답 칸](#manage-dashboard_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `views.today` | `Number` | 오늘 조회수 |
| `views.yesterday` | `Number` | 어제 조회수 |
| `views.total` | `Number` | 누적 조회수 |
| `visitors.today` | `Number` | 오늘 방문자 |
| `visitors.yesterday` | `Number` | 어제 방문자 |
| `visitors.total` | `Number` | 누적 방문자 |
| `newCommentCount` | `Number` | 새 댓글 수 (댓글 관리를 마지막으로 연 뒤 남이 쓴 것) |
| `chart[]` | `Array` | 최근 날짜별 그래프 (오래된 날부터) |
| `chart[].date` | `String` | 날짜 (한국 시간 기준) |
| `chart[].views` | `Number` | 그날 조회수 |
| `chart[].visitors` | `Number` | 그날 방문자 |
| `popularPosts[]` | `Array` | 최근 7일 조회수가 많은 글 |
| `recentPosts[]` | `Array` | 최근에 쓴 글 |
| `recentPosts[].postId` | `Number` | 글 번호 |
| `recentPosts[].title` | `String` | 제목 |
| `recentPosts[].createdAt` | `String` | 쓴 시각 |
| `recentPosts[].visibility` | `String` | 공개 범위 |

## [8. 오류 예시](#errors)

### [8.1. 입력값 오류 (400)](#error-validation)

제목을 비우고 글을 쓴 경우입니다.

#### [8.1.1. 응답](#error-validation_http_response)

```http
HTTP/1.1 400 Bad Request
Set-Cookie: SESSION=MTE=; Path=/; Max-Age=604800; Expires=Wed, 21 Oct 2026 05:30:44 GMT; HttpOnly; SameSite=Lax
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 222

{
  "code" : "VALIDATION_FAILED",
  "message" : "입력값을 다시 확인해 주세요",
  "fieldErrors" : [ {
    "field" : "title",
    "code" : "TITLE_REQUIRED",
    "message" : "제목을 입력해 주세요"
  } ]
}
```

#### [8.1.2. 응답 칸](#error-validation_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `code` | `String` | 오류 종류 (화면은 이 값으로 나눈다) |
| `message` | `String` | 사람이 읽는 안내 문구 |
| `fieldErrors[]` | `Array` | 칸마다 틀린 곳 (입력값 오류일 때만) |
| `fieldErrors[].field` | `String` | 칸 이름 |
| `fieldErrors[].code` | `String` | 틀린 까닭 |
| `fieldErrors[].message` | `String` | 칸 옆에 보일 문구 |

### [8.2. 로그인 필요 (401)](#error-unauthenticated)

#### [8.2.1. 응답](#error-unauthenticated_http_response)

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json;charset=UTF-8
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 82

{
  "code" : "UNAUTHENTICATED",
  "message" : "※ 로그인이 필요합니다"
}
```

#### [8.2.2. 응답 칸](#error-unauthenticated_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `code` | `String` | 오류 종류 |
| `message` | `String` | 사람이 읽는 안내 문구 |

### [8.3. 없는 글 (404)](#error-not-found)

#### [8.3.1. 응답](#error-not-found_http_response)

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Length: 81

{
  "code" : "POST_NOT_FOUND",
  "message" : "존재하지 않는 글입니다"
}
```

#### [8.3.2. 응답 칸](#error-not-found_response_fields)

| Path | Type | Description |
| --- | --- | --- |
| `code` | `String` | 오류 종류 |
| `message` | `String` | 사람이 읽는 안내 문구 |

Last updated 2026-10-14 05:30:25 UTC