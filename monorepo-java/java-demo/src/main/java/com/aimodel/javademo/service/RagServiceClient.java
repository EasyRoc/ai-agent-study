package com.aimodel.javademo.service;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

import com.aimodel.javademo.api.dto.rag.RagAskRequestBody;
import com.aimodel.javademo.api.dto.rag.RagAskResponseBody;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.server.ResponseStatusException;

/**
 * 转发 Python <code>POST /rag/ask</code>；第 5 周：5 分钟问题缓存、<code>clientRequestId</code> 幂等、
 * <code>X-No-Cache</code> 时跳过问题缓存（仍尊重幂等表）。
 */
@Service
public class RagServiceClient {

    private static final int BLOCK_SECONDS = 75;

    private final WebClient ragServiceWebClient;
    private final Cache<String, RagAskResponseBody> questionCache;
    private final Cache<String, RagAskResponseBody> idempotencyCache;

    public RagServiceClient(@Qualifier("ragServiceWebClient") WebClient ragServiceWebClient) {
        this.ragServiceWebClient = ragServiceWebClient;
        this.questionCache = Caffeine.newBuilder()
                .maximumSize(2_000)
                .expireAfterWrite(Duration.ofMinutes(5))
                .build();
        this.idempotencyCache = Caffeine.newBuilder()
                .maximumSize(5_000)
                .expireAfterWrite(Duration.ofMinutes(30))
                .build();
    }

    public RagAskResponseBody ask(RagAskRequestBody body, boolean noCache) {
        String idem = body.getClientRequestId();
        if (idem != null && !idem.isBlank()) {
            RagAskResponseBody fromIdem = this.idempotencyCache.getIfPresent(idem);
            if (fromIdem != null) {
                return fromIdem;
            }
        }
        if (!noCache) {
            String qk = cacheKeyForQuestion(body);
            RagAskResponseBody hit = this.questionCache.getIfPresent(qk);
            if (hit != null) {
                return hit;
            }
        }

        Map<String, Object> payload = new HashMap<>();
        payload.put("question", body.getQuestion());
        if (body.getTopK() != null) {
            payload.put("topK", body.getTopK());
        }
        if (body.getSessionId() != null && !body.getSessionId().isBlank()) {
            payload.put("sessionId", body.getSessionId());
        }
        try {
            RagAskResponseBody res = this.ragServiceWebClient.post()
                    .uri("/rag/ask")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(payload)
                    .retrieve()
                    .bodyToMono(RagAskResponseBody.class)
                    .onErrorMap(WebClientRequestException.class, ex ->
                            new ResponseStatusException(HttpStatus.BAD_GATEWAY, "RAG_TIMEOUT: " + ex.getMessage(), ex)
                    )
                    .block(java.time.Duration.ofSeconds(BLOCK_SECONDS));
            if (res == null) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "RAG 空响应", null);
            }
            if (idem != null && !idem.isBlank()) {
                this.idempotencyCache.put(idem, res);
            }
            if (!noCache) {
                this.questionCache.put(cacheKeyForQuestion(body), res);
            }
            return res;
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            if (e.getMessage() != null && e.getMessage().contains("timeout")) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "RAG_TIMEOUT: " + e.getMessage(), e);
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "RAG 服务调用失败: " + e.getMessage(), e);
        }
    }

    private static String cacheKeyForQuestion(RagAskRequestBody body) {
        return body.getQuestion().trim() + "\u0000" + Objects.toString(body.getTopK(), "4")
                + "\u0000" + (body.getSessionId() == null ? "" : body.getSessionId().trim());
    }
}
