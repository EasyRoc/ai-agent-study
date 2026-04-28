package com.aimodel.javademo.web;

import com.aimodel.javademo.api.dto.rag.RagAskRequestBody;
import com.aimodel.javademo.api.dto.rag.RagAskResponseBody;
import com.aimodel.javademo.service.RagServiceClient;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import jakarta.validation.Valid;

/**
 * 第 4 周：对外 <code>POST /api/v1/ask</code>，转发 Python 聚合 RAG（检索 + 生成 + 引用）。
 */
@RestController
@RequestMapping("/api/v1")
public class AskV1Controller {

    private final RagServiceClient ragServiceClient;

    public AskV1Controller(RagServiceClient ragServiceClient) {
        this.ragServiceClient = ragServiceClient;
    }

    @PostMapping("/ask")
    public RagAskResponseBody ask(
            @Valid @RequestBody RagAskRequestBody body,
            @RequestHeader(name = "X-No-Cache", required = false) String xNoCache) {
        boolean noCache = "1".equals(xNoCache) || "true".equalsIgnoreCase(xNoCache);
        return this.ragServiceClient.ask(body, noCache);
    }
}
