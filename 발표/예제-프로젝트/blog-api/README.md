# 예제 프로젝트: 블로그 API

발표에서 쓴 블로그 API(글 조회·작성·수정·삭제)를 실제로 동작하게 만든 Spring Boot 프로젝트입니다.
발표 그림 13번과 `발표/그림/실제-화면/`의 화면은 이 프로젝트를 실행해서 찍었습니다.

- Java 21, Spring Boot 3.3
- 문서: springdoc(Swagger UI) + Spring REST Docs
- 에러 응답: `@RestControllerAdvice` + RFC 9457 `ProblemDetail` + 팀 에러 코드(`code`)

## 실행

```bash
mvn package                                  # 테스트 실행 + REST Docs 문서 생성 + jar 빌드
java -jar target/blog-api-0.0.1.jar
```

| 주소 | 내용 |
|---|---|
| http://localhost:8080/swagger-ui.html | Swagger UI (springdoc이 코드에서 자동으로 만든 문서) |
| http://localhost:8080/v3/api-docs | OpenAPI 명세 JSON |
| `target/generated-docs/index.html` | Spring REST Docs 문서 (테스트가 통과해야 만들어짐) |
| http://localhost:8080/api/v1/posts/42 | 글 조회 (200) |
| http://localhost:8080/api/v1/posts/99999 | 없는 글 조회 (404 + 공통 에러 형식) |

## 파일

| 파일 | 내용 |
|---|---|
| `PostController.java` | URL·메서드·상태 코드, `@Operation`으로 문서 설명 |
| `PostService.java` | 업무 규칙 검사, 실패하면 `ApiException`을 던짐 |
| `GlobalExceptionHandler.java` | 전역 예외 처리기: 예외 → 상태 코드 + 공통 에러 형식 |
| `ErrorCode.java` | 에러 코드와 상태 코드 |
| `Dtos.java` | 요청·응답 DTO와 `@Valid` 검증 규칙 |
| `src/test/.../PostApiDocsTest.java` | REST Docs 테스트: 통과하면 문서 조각(snippet)이 만들어짐 |
| `src/docs/asciidoc/index.adoc` | 문서 조각을 모아 REST Docs 페이지를 만드는 틀 |
