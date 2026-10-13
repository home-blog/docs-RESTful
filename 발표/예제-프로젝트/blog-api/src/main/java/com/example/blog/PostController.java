package com.example.blog;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import java.net.URI;
import java.util.List;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Tag(name = "글", description = "블로그 글 API")
@RestController
@RequestMapping("/api/v1/posts")
class PostController {
    private final PostService postService;

    PostController(PostService postService) {
        this.postService = postService;
    }

    @Operation(summary = "글 목록 조회", description = "최신순으로 정렬한 글 목록")
    @GetMapping
    public List<PostResponse> list(@Parameter(description = "제목 검색어") @RequestParam(required = false) String keyword) {
        return postService.list(keyword);
    }

    @Operation(summary = "글 하나 조회")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "조회 성공"),
            @ApiResponse(responseCode = "404", description = "글이 없음 (code: POST_NOT_FOUND)")
    })
    @GetMapping("/{id}")
    public PostResponse get(@Parameter(description = "글 번호", example = "42") @PathVariable Long id) {
        return postService.get(id);
    }

    @Operation(summary = "글 작성")
    @PostMapping
    public ResponseEntity<PostResponse> create(@Valid @RequestBody CreatePostRequest req) {
        PostResponse post = postService.create(req);
        return ResponseEntity.created(URI.create("/api/v1/posts/" + post.id())).body(post);
    }

    @Operation(summary = "글 수정", description = "보낸 필드만 수정")
    @PatchMapping("/{id}")
    public PostResponse update(@PathVariable Long id, @Valid @RequestBody UpdatePostRequest req) {
        return postService.update(id, req);
    }

    @Operation(summary = "글 삭제")
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        postService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
