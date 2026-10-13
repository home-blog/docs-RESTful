package com.example.blog;

import org.springframework.http.HttpStatus;

enum ErrorCode {
    POST_NOT_FOUND(HttpStatus.NOT_FOUND, "글을 찾을 수 없습니다"),
    DUPLICATE_TITLE(HttpStatus.CONFLICT, "같은 제목의 글이 이미 있습니다");

    final HttpStatus status;
    final String title;

    ErrorCode(HttpStatus status, String title) {
        this.status = status;
        this.title = title;
    }
}

class ApiException extends RuntimeException {
    final ErrorCode errorCode;

    ApiException(ErrorCode errorCode, String detail) {
        super(detail);
        this.errorCode = errorCode;
    }
}
