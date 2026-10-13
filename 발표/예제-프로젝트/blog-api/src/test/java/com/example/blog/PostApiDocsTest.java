package com.example.blog;

import static org.springframework.restdocs.mockmvc.MockMvcRestDocumentation.document;
import static org.springframework.restdocs.mockmvc.RestDocumentationRequestBuilders.get;
import static org.springframework.restdocs.mockmvc.RestDocumentationRequestBuilders.post;
import static org.springframework.restdocs.operation.preprocess.Preprocessors.*;
import static org.springframework.restdocs.payload.PayloadDocumentation.*;
import static org.springframework.restdocs.request.RequestDocumentation.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.restdocs.AutoConfigureRestDocs;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
@AutoConfigureRestDocs
class PostApiDocsTest {

    @Autowired MockMvc mockMvc;

    @Test
    void 글_하나_조회() throws Exception {
        mockMvc.perform(get("/api/v1/posts/{id}", 42))
                .andExpect(status().isOk())
                .andDo(document("post-get",
                        preprocessResponse(prettyPrint()),
                        pathParameters(parameterWithName("id").description("글 번호")),
                        responseFields(
                                fieldWithPath("id").description("글 번호"),
                                fieldWithPath("title").description("제목"),
                                fieldWithPath("content").description("본문"),
                                fieldWithPath("createdAt").description("작성 시각 (ISO-8601)"))));
    }

    @Test
    void 없는_글_조회() throws Exception {
        mockMvc.perform(get("/api/v1/posts/{id}", 99999))
                .andExpect(status().isNotFound())
                .andDo(document("post-get-not-found",
                        preprocessResponse(prettyPrint()),
                        responseFields(
                                fieldWithPath("type").description("에러 종류"),
                                fieldWithPath("title").description("에러 제목"),
                                fieldWithPath("status").description("HTTP 상태 코드"),
                                fieldWithPath("detail").description("이번 요청에 대한 설명"),
                                fieldWithPath("instance").description("요청 경로"),
                                fieldWithPath("code").description("팀에서 정한 에러 코드"))));
    }

    @Test
    void 글_작성() throws Exception {
        mockMvc.perform(post("/api/v1/posts")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"title\":\"서울 카페\",\"content\":\"성수동에서...\"}"))
                .andExpect(status().isCreated())
                .andDo(document("post-create",
                        preprocessRequest(prettyPrint()),
                        preprocessResponse(prettyPrint()),
                        requestFields(
                                fieldWithPath("title").description("제목 (필수, 100자 이하)"),
                                fieldWithPath("content").description("본문 (필수)")),
                        responseFields(
                                fieldWithPath("id").description("새 글 번호"),
                                fieldWithPath("title").description("제목"),
                                fieldWithPath("content").description("본문"),
                                fieldWithPath("createdAt").description("작성 시각"))));
    }
}
