글결.API

여러 사람이 각자 블로그를 쓰고 한곳에서 둘러보는 멀티 블로그 서비스 **글결**의 서버 API입니다. 서버 코드(Spring Boot)에서 자동으로 만든 OpenAPI 문서를 묶음별로 정리했습니다. 각 API를 누르면 요청 값과 응답 칸이 열립니다.

## 모든 API의 약속

### 주소와 버전

모든 주소는 `/api/v1/…`. API 버전은 릴리스 번호와 따로 가서, 칸을 더하는 변경은 v1 그대로 두고 칸을 빼거나 뜻을 바꿀 때만 v2를 엽니다.

### 로그인 = 서버 세션

로그인하면 세션 쿠키 `SESSION`이 생기고 세션은 PostgreSQL에 저장합니다(JWT 안 씀). 7일 동안 쓰지 않으면 끝납니다. 로그아웃은 `POST /api/v1/auth/logout`.

### CSRF 토큰

GET이 아닌 요청은 쿠키 `XSRF-TOKEN`의 값을 머리글 `X-XSRF-TOKEN`에 실어 보냅니다. 토큰은 `GET /api/v1/auth/csrf`로 받습니다.

### 소셜 로그인

화면이 `/oauth2/authorization/{회사}`로 이동하면 GitHub·Google·카카오·네이버 화면을 거쳐 `/login/oauth2/code/{회사}`로 돌아옵니다.

### 오류 모양 (모든 API 같음)

볼 권한이 없는 글·댓글·이미지는 있는지조차 알 수 없도록 없는 것과 같은 `404`로 답합니다.

```
{
  "code": "VALIDATION_FAILED",
  "message": "입력값을 다시 확인해 주세요",
  "fieldErrors": [ { "field": "title", "code": "TITLE_REQUIRED", "message": "제목을 입력해 주세요" } ]
}
```

## API 목록

찾기

로그인 세션 쿠키가 있어야 부를 수 있음 CSRF 머리글에 CSRF 토큰을 실음

찾는 API가 없습니다. 다른 말로 찾아 보세요.

코드 저장소의 `OpenApiDocsTest`가 모든 API에 설명이 있는지, "로그인" 표시가 실제 보안 설정과 같은지 매번 확인합니다.