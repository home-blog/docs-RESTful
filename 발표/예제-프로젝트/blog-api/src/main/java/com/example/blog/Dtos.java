package com.example.blog;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.time.LocalDateTime;

record CreatePostRequest(
        @NotBlank @Size(max = 100) String title,
        @NotBlank String content) {}

record UpdatePostRequest(
        @Size(max = 100) String title,
        String content) {}

record PostResponse(Long id, String title, String content, LocalDateTime createdAt) {}
