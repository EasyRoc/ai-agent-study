package com.aimodel.javademo.service;

import java.util.Map;

import com.aimodel.javademo.api.dto.vector.VectorSearchResponseBody;

import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientRequestException;
import org.springframework.web.server.ResponseStatusException;
/**
 * 封装 <code>POST {baseUrl}/search</code>，供网关演示；超时映射为 502 + 课表码 {@code VECTOR_TIMEOUT} 语义。
 */
@Service
public class VectorServiceClient {

    private static final int BLOCK_SECONDS = 8;

    private final WebClient vectorServiceWebClient;

    public VectorServiceClient(@Qualifier("vectorServiceWebClient") WebClient vectorServiceWebClient) {
        this.vectorServiceWebClient = vectorServiceWebClient;
    }

    public VectorSearchResponseBody search(String q, int k) {
        try {
            return this.vectorServiceWebClient.post()
                    .uri("/search")
                    .contentType(MediaType.APPLICATION_JSON)
                    .bodyValue(Map.of("q", q, "k", k))
                    .retrieve()
                    .bodyToMono(VectorSearchResponseBody.class)
                    .onErrorMap(WebClientRequestException.class, ex ->
                            new ResponseStatusException(HttpStatus.BAD_GATEWAY, "VECTOR_TIMEOUT: " + ex.getMessage(), ex)
                    )
                    .block(java.time.Duration.ofSeconds(BLOCK_SECONDS));
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            if (e.getMessage() != null && e.getMessage().contains("timeout")) {
                throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "VECTOR_TIMEOUT: " + e.getMessage(), e);
            }
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "向量服务调用失败: " + e.getMessage(), e);
        }
    }
}
