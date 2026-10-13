# 8. API 문서 작성

## 8-1. 왜 문서가 필요한가요?

> 🍽️ **메뉴판 없는 식당**을 떠올려 보세요. 맛있는 음식이 있어도 손님은 뭘 주문할 수 있는지 몰라요.

API 문서는 API의 메뉴판이에요. 이 사람들이 읽어요.

- **화면(프론트엔드) 개발자**: 무슨 주소로, 무엇을 보내면, 무엇이 오는지
- **같은 팀 백엔드 개발자**: 내가 만들지 않은 API를 고칠 때
- **QA·기획자**: 어떤 경우에 어떤 에러가 나는지
- **3개월 뒤의 나**: "이거 왜 이렇게 만들었지?"

> 💡 문서가 없으면 질문이 쏟아지고, 문서가 틀리면 **없는 것보다 더 나빠요.**

## 8-2. API 하나에 무엇을 적어야 하나요?

| 항목 | 예시 (글 쓰기 API) |
|---|---|
| 한 줄 설명 | 새 글을 씁니다. 로그인한 회원만 쓸 수 있습니다. |
| 메서드 + URL | `POST /api/v1/posts` |
| 인증 | 필요 (로그인) |
| 요청 파라미터 | 없음 |
| 요청 바디 | `title` (필수, 1~100자), `content` (필수, 1~10,000자), `topic` (필수, `TRAVEL`/`FOOD`/…) |
| 성공 응답 | `201 Created`, `Location` 헤더, 만든 글 JSON 예시 |
| 실패 응답 | `400 INVALID_INPUT`, `401 UNAUTHENTICATED` + 예시 |
| 예시 요청 | `curl` 한 줄 또는 JSON 예시 |

> **요청·응답 예시 JSON**이 가장 많이 읽혀요. 설명이 길어도 예시가 없으면 결국 물어봅니다.

## 8-3. 표준: OpenAPI (옛 이름 Swagger)

손으로 문서를 쓰는 대신, **정해진 형식의 파일**로 API를 설명하는 국제 표준이 있어요. 이게 **OpenAPI 명세(OpenAPI Specification)** 입니다.

| 이름 | 정체 |
|---|---|
| **OpenAPI** | API를 설명하는 **문서 형식(규격)**. YAML이나 JSON 파일 |
| **Swagger UI** | OpenAPI 파일을 읽어 **웹 화면으로 보여 주는 도구**. 화면에서 바로 API를 호출해 볼 수도 있음 |
| Swagger | OpenAPI의 **옛 이름**이자 관련 도구 묶음의 이름. 그래서 섞어서 부름 |

OpenAPI 파일은 이렇게 생겼어요 (일부).

```yaml
openapi: 3.1.0
info:
  title: 블로그 API
  version: v1
paths:
  /api/v1/posts/{postId}:
    get:
      summary: 글 하나 보기
      parameters:
        - name: postId
          in: path
          required: true
          schema: { type: integer }
      responses:
        "200":
          description: 성공
        "404":
          description: 글이 없음 (code = POST_NOT_FOUND)
```

이 파일 하나로 할 수 있는 것:
- **Swagger UI** 같은 도구로 보기 좋은 문서 페이지를 만든다
- 프론트엔드용 **요청 코드를 자동 생성**한다
- Postman 같은 도구로 **바로 가져와** 테스트한다

## 8-4. Spring에서 문서 만드는 세 가지 방법

### 방법 1. springdoc-openapi: 코드에서 자동으로 (가장 쉬움)

라이브러리를 하나 추가하면 컨트롤러를 읽어서 OpenAPI 문서와 Swagger UI 화면을 **자동으로** 만들어 줘요.

```xml
<!-- pom.xml: 버전은 쓰고 있는 Spring Boot 버전에 맞는 것을 springdoc 공식 문서에서 확인 -->
<dependency>
    <groupId>org.springdoc</groupId>
    <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
    <version>(Spring Boot에 맞는 버전)</version>
</dependency>
```

서버를 켜고 `http://localhost:8080/swagger-ui/index.html` 을 열면 문서 화면이 보여요.
운영 서버에서는 `springdoc.swagger-ui.enabled: false`로 끄고, Spring Security를 쓰면 `/swagger-ui/**`, `/v3/api-docs/**`를 열어 줘야 해요.

설명을 더 붙이고 싶으면 어노테이션을 달아요.

```java
@Operation(summary = "글 쓰기", description = "로그인한 회원만 쓸 수 있습니다.")
@ApiResponse(responseCode = "201", description = "작성 성공")
@ApiResponse(responseCode = "400", description = "입력값 오류 (INVALID_INPUT)")
@PostMapping
public ResponseEntity<PostResponse> create(@Valid @RequestBody CreatePostRequest request) { ... }
```

```java
public record CreatePostRequest(
    @Schema(description = "글 제목", example = "제주도 3박 4일", maxLength = 100)
    @NotBlank @Size(max = 100) String title,
    ...
) {}
```

> 💡 `@NotBlank`, `@Size` 같은 검증 어노테이션도 문서에 **"필수", "최대 100자"** 로 자동 반영돼요. 6장의 검증과 문서가 자연스럽게 이어집니다.

### 방법 2. Spring REST Docs: 테스트가 통과해야 문서가 생김 (가장 정확)

API **테스트 코드**를 쓰면, 테스트가 실제로 주고받은 요청·응답을 문서 조각으로 만들어 줘요.

- 👍 테스트가 통과해야 문서가 생기니 **문서와 실제 동작이 어긋날 수 없어요.**
- 👍 운영 코드에 문서용 어노테이션이 붙지 않아 깔끔해요.
- 👎 테스트를 꼼꼼히 써야 해서 처음엔 손이 많이 가요.

적용 순서는 네 단계예요. 전체 코드는 [`발표/예제-프로젝트/blog-api`](발표/예제-프로젝트/blog-api)에 있어요.

1. 의존성 추가: `spring-restdocs-mockmvc`(테스트) + Asciidoctor 플러그인
2. 테스트 작성: `@AutoConfigureRestDocs` + `.andDo(document("post-get", responseFields(...)))`
3. 테스트 실행 → `generated-snippets/post-get/`에 요청·응답 문서 조각이 생김
4. `src/docs/asciidoc/index.adoc`에서 조각을 `include`하고 빌드 → HTML 문서

### 방법 3. 손으로 쓰기 (Notion, 위키, 엑셀)

- 👍 아무 도구 없이 바로 시작
- 👎 코드는 바뀌는데 문서는 안 바뀌어서 **금방 틀려져요.** 작은 팀 초반에만 추천

### 비교

| | springdoc (자동) | REST Docs (테스트 기반) | 손으로 |
|---|---|---|---|
| 시작 난이도 | 쉬움 | 어려움 | 가장 쉬움 |
| 정확도 | 코드 기준이라 높음 (설명 문구는 사람이 관리) | **가장 높음** | 낮음 (낡기 쉬움) |
| 화면에서 바로 호출해 보기 | ✅ Swagger UI | 설정하면 가능 | ❌ |
| 추천 상황 | **처음 시작, 학습, 빠른 협업** | 문서 정확도가 중요한 서비스 | 아주 초기 |

> 실무에서는 두 가지를 섞기도 해요. REST Docs로 정확한 문서를 만들고, 그 결과를 OpenAPI 파일로 바꿔 Swagger UI로 보여 주는 식이에요.

## 8-5. 좋은 API 문서의 조건

1. **예시가 있다**: 요청·응답 JSON을 그대로 복사해서 써 볼 수 있다.
2. **에러도 적혀 있다**: 성공만 적힌 문서는 반쪽짜리. 에러 코드 표(5장)를 꼭 같이.
3. **최신이다**: 코드에서 자동으로 만들거나, 코드를 바꿀 때 문서도 같이 바꾸는 규칙이 있다.
4. **공통 규칙이 앞에 있다**: 인증 방법, 날짜 형식, 페이징 규칙(0부터?), 에러 형식은 API마다 반복하지 말고 맨 앞에 한 번.
5. **운영 서버에서는 보호한다**: Swagger UI를 아무나 볼 수 있게 열어 두면 공격자에게도 지도가 돼요. 운영에서는 끄거나 로그인 뒤에 둡니다.

## 8-6. 정리

- 문서는 API의 **메뉴판**. 없으면 아무도 못 쓰고, 틀리면 더 나쁘다.
- 표준은 **OpenAPI**, 보여 주는 도구는 **Swagger UI**.
- 쉽게 시작은 **springdoc**, 정확도는 **Spring REST Docs**.
- **예시 JSON, 에러 코드, 공통 규칙**이 들어간 문서가 좋은 문서.

다음: [9. 한 장 요약·체크리스트](09-한-장-요약-체크리스트.md)
