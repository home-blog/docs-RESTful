package com.example.blog;

import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import org.springframework.stereotype.Service;

@Service
class PostService {
    private final Map<Long, PostResponse> posts = new ConcurrentHashMap<>();
    private final AtomicLong seq = new AtomicLong(42);

    PostService() {
        posts.put(41L, new PostResponse(41L, "부산 맛집", "돼지국밥부터...", LocalDateTime.of(2026, 10, 1, 9, 0)));
        posts.put(42L, new PostResponse(42L, "제주 여행", "첫째 날은...", LocalDateTime.of(2026, 10, 2, 9, 0)));
    }

    List<PostResponse> list(String keyword) {
        return posts.values().stream()
                .filter(p -> keyword == null || p.title().contains(keyword))
                .sorted(Comparator.comparing(PostResponse::createdAt).reversed())
                .toList();
    }

    PostResponse get(Long id) {
        PostResponse post = posts.get(id);
        if (post == null) throw new ApiException(ErrorCode.POST_NOT_FOUND, id + "번 글이 없습니다.");
        return post;
    }

    PostResponse create(CreatePostRequest req) {
        boolean dup = posts.values().stream().anyMatch(p -> p.title().equals(req.title()));
        if (dup) throw new ApiException(ErrorCode.DUPLICATE_TITLE, "'" + req.title() + "' 제목의 글이 이미 있습니다.");
        long id = seq.incrementAndGet();
        PostResponse post = new PostResponse(id, req.title(), req.content(), LocalDateTime.of(2026, 10, 16, 13, 30));
        posts.put(id, post);
        return post;
    }

    PostResponse update(Long id, UpdatePostRequest req) {
        PostResponse old = get(id);
        PostResponse post = new PostResponse(id,
                req.title() != null ? req.title() : old.title(),
                req.content() != null ? req.content() : old.content(),
                old.createdAt());
        posts.put(id, post);
        return post;
    }

    void delete(Long id) {
        get(id);
        posts.remove(id);
    }
}
