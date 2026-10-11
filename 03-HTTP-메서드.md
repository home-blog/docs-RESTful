# 3. HTTP 메서드

## 3-1. 다섯 개만 기억하세요

URL이 "무엇"이라면, 메서드는 **"무엇을 하고 싶은지"** 입니다.

| 메서드 | 한 단어로 | 블로그 예시 | 바디 보내나? |
|---|---|---|---|
| **GET** | 조회 | `GET /posts/42` 42번 글 보기 | ❌ 안 보냄 |
| **POST** | 생성 | `POST /posts` 새 글 쓰기 | ✅ 새 글 내용 |
| **PUT** | 통째로 교체 | `PUT /posts/42` 42번 글을 이 내용으로 **전부** 바꾸기 | ✅ 전체 내용 |
| **PATCH** | 일부 수정 | `PATCH /posts/42` 42번 글의 **제목만** 바꾸기 | ✅ 바꿀 부분만 |
| **DELETE** | 삭제 | `DELETE /posts/42` 42번 글 지우기 | ❌ 보통 안 보냄 |

> 데이터베이스를 배웠다면 **CRUD** 와 짝지어 보세요.
> Create = POST, Read = GET, Update = PUT/PATCH, Delete = DELETE

## 3-2. PUT과 PATCH의 차이

가장 많이 헷갈리는 부분이에요. 42번 글이 지금 이렇다고 해 봐요.

```json
{ "title": "제주 여행", "content": "첫날은 비가 왔다", "topic": "TRAVEL" }
```

**제목만** 바꾸고 싶어요.

### PATCH: 보낸 것만 바꾼다

```http
PATCH /posts/42
{ "title": "제주도 3박 4일" }
```
결과 → `{ "title": "제주도 3박 4일", "content": "첫날은 비가 왔다", "topic": "TRAVEL" }` ✅

### PUT: 보낸 것으로 통째로 갈아 끼운다

```http
PUT /posts/42
{ "title": "제주도 3박 4일" }
```
결과 → `{ "title": "제주도 3박 4일", "content": null, "topic": null }` 😱 본문이 사라졌어요.
(PUT의 뜻대로 "보낸 것이 새 전체 내용"이라고 처리하는 서버라면 이렇게 됩니다.)

PUT으로 제목만 바꾸려면 **나머지도 전부 같이** 보내야 합니다.

> 비유: **PUT은 "이 서류로 원본을 교체해 주세요"**, **PATCH는 "이 부분만 수정 테이프로 고쳐 주세요"**.
> 실무에서 "수정" 기능은 대부분 **PATCH** 가 자연스럽습니다.

## 3-3. 꼭 알아야 할 두 가지 성질: 안전(Safe)과 멱등(Idempotent)

### 안전(Safe): 서버의 데이터를 바꾸지 않는가?

- **GET은 안전해야 합니다.** 조회만 하고 아무것도 바꾸면 안 돼요.
- 그래서 브라우저, 검색 로봇, 캐시가 GET은 마음 놓고 여러 번 부릅니다.
- `GET /posts/42/delete` 같은 API가 위험한 이유가 이거예요.

### 멱등(Idempotent): 여러 번 해도 결과가 같은가?

어려운 한자어지만 뜻은 간단해요. **"한 번 하든 열 번 하든 최종 결과가 같다."**

> 비유: **엘리베이터 호출 버튼**은 멱등이에요. 열 번 눌러도 엘리베이터는 한 번 와요.
> **자판기 구매 버튼**은 멱등이 아니에요. 열 번 누르면 음료가 열 개 나와요(돈도 열 번 나가요).

| 메서드 | 안전? | 멱등? | 이유 |
|---|---|---|---|
| GET | ✅ | ✅ | 조회만 하니까 |
| PUT | ❌ | ✅ | "이 내용으로 교체"를 열 번 해도 결과는 같은 내용 |
| DELETE | ❌ | ✅ | 이미 지운 걸 또 지워도 "없는 상태"는 같음 |
| PATCH | ❌ | △ (보통 ✅로 만든다) | "제목을 X로" 는 멱등, "조회수 +1" 은 멱등 아님 |
| POST | ❌ | ❌ | 열 번 보내면 글이 열 개 생김 |

### 왜 멱등이 중요한가요?

인터넷은 가끔 끊겨요. 요청을 보냈는데 응답이 안 오면 클라이언트는 **다시 보내야 할지** 고민합니다.

- 멱등한 요청(PUT, DELETE)이면 **그냥 다시 보내도 안전**해요.
- POST는 다시 보내면 **글이 두 개** 생길 수 있어요. 그래서 "결제", "글 쓰기" 버튼은 한 번 누르면 비활성화하거나, 서버에서 중복을 막는 장치를 둡니다.

> 💡 실무 팁: POST 중복을 막는 흔한 방법은 요청마다 고유한 값(예: `Idempotency-Key` 헤더)을 같이 보내고, 서버가 "이 키로 이미 처리했으면 같은 결과를 다시 돌려주는" 방식입니다. 결제 API(Stripe 등)가 이렇게 합니다.

## 3-4. 메서드별 응답 짝꿍 (4장 미리보기)

| 요청 | 성공하면 | 함께 주면 좋은 것 |
|---|---|---|
| `GET /posts` | `200 OK` | 목록 + 페이지 정보 |
| `GET /posts/42` | `200 OK` | 글 |
| `POST /posts` | `201 Created` | `Location: /posts/43` 헤더 + 만든 글 |
| `PUT /posts/42` | `200 OK` (또는 `204`) | 바뀐 글 |
| `PATCH /posts/42` | `200 OK` | 바뀐 글 |
| `DELETE /posts/42` | `204 No Content` | 바디 없음 |

## 3-5. 그 밖의 메서드 (이름만 알아 두기)

| 메서드 | 하는 일 |
|---|---|
| HEAD | GET과 같은데 **바디 없이 헤더만** 받는다 (파일이 있는지, 크기만 확인할 때) |
| OPTIONS | "이 주소에서 어떤 메서드를 쓸 수 있어요?" 묻는다. 브라우저가 다른 도메인 API를 부르기 전에 자동으로 보내는 **CORS 사전 요청**에 쓰인다 |

## 3-6. Spring에서는 이렇게 생겼어요

```java
@RestController
@RequestMapping("/api/v1/posts")
public class PostController {

    @GetMapping                      // GET    /api/v1/posts
    public PageResponse<PostSummary> list(...) { ... }

    @GetMapping("/{postId}")         // GET    /api/v1/posts/42
    public PostResponse get(@PathVariable Long postId) { ... }

    @PostMapping                     // POST   /api/v1/posts
    public ResponseEntity<PostResponse> create(@Valid @RequestBody CreatePostRequest request) { ... }

    @PatchMapping("/{postId}")       // PATCH  /api/v1/posts/42
    public PostResponse update(@PathVariable Long postId, @Valid @RequestBody UpdatePostRequest request) { ... }

    @DeleteMapping("/{postId}")      // DELETE /api/v1/posts/42
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable Long postId) { ... }
}
```

어노테이션 이름만 봐도 메서드와 주소가 한눈에 보이죠. 이게 RESTful 설계가 코드까지 깔끔하게 만드는 이유예요.

## 3-7. 정리

- **GET 조회 / POST 생성 / PUT 통째 교체 / PATCH 일부 수정 / DELETE 삭제**
- 수정은 대부분 **PATCH**. PUT은 보내지 않은 칸이 비워질 수 있다.
- **GET은 절대 데이터를 바꾸지 않는다** (안전).
- **PUT, DELETE는 여러 번 해도 같다** (멱등). **POST는 아니다** → 중복 주의.

다음: [4. HTTP 상태 코드](04-HTTP-상태-코드.md)
