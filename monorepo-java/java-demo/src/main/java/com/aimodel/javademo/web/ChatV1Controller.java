package com.aimodel.javademo.web;

import java.io.IOException;
import java.util.Map;
import java.util.concurrent.atomic.AtomicReference;

import com.aimodel.javademo.api.dto.ChatRequest;
import com.aimodel.javademo.api.dto.ChatResponse;
import com.aimodel.javademo.service.ChatLlmService;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import reactor.core.Disposable;
import reactor.core.publisher.Flux;

/**
 * 第 1 周第 3 天：同步 <code>POST /chat</code>；第 1 周第 4 天：SSE 流式 <code>POST/GET /chat/stream</code>。路径见 {@value #BASE}。
 */
@RestController
@RequestMapping(ChatV1Controller.BASE)
public class ChatV1Controller {

    public static final String BASE = "/api/v1";

    private static final long SSE_TIMEOUT_MS = 300_000L;
    private static final Logger log = LoggerFactory.getLogger(ChatV1Controller.class);

    private final ChatLlmService chatLlmService;
    private final ObjectMapper objectMapper;

    public ChatV1Controller(ChatLlmService chatLlmService, ObjectMapper objectMapper) {
        this.chatLlmService = chatLlmService;
        this.objectMapper = objectMapper;
    }

    @PostMapping(value = "/chat", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public ChatResponse chat(@RequestBody @Valid ChatRequest request) {
        return this.chatLlmService.chat(request);
    }

    /**
     * 第 1 周第 4 天：以 SSE（<code>text/event-stream</code>）推送模型增量；<code>curl -N</code> 可边收边看。
     * 事件名：<code>meta</code>（首条，含 model 名）、<code>delta</code>（正文分片）。异常时 <code>event: error</code> + JSON，再结束。
     */
    @PostMapping(
            value = "/chat/stream",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.TEXT_EVENT_STREAM_VALUE
    )
    public SseEmitter streamByPost(@RequestBody @Valid ChatRequest request) {
        return toSseEmitter(this.chatLlmService.streamContent(request));
    }

    /**
     * 与 {@link #streamByPost} 同逻辑，但仅单轮 <code>prompt</code>，便于浏览器 <code>EventSource</code>（仅支持 GET）试验。
     */
    @GetMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamByGet(@RequestParam("prompt") String prompt) {
        if (prompt == null || prompt.isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "prompt 不能为空");
        }
        ChatRequest r = new ChatRequest();
        r.setPrompt(prompt.trim());
        r.setMessages(null);
        return toSseEmitter(this.chatLlmService.streamContent(r));
    }

    private SseEmitter toSseEmitter(Flux<String> contentFlux) {
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        try {
            String meta = this.objectMapper.writeValueAsString(
                    Map.of("model", this.chatLlmService.getConfiguredModel()));
            emitter.send(SseEmitter.event().name("meta").data(meta, MediaType.APPLICATION_JSON));
        } catch (JsonProcessingException e) {
            emitter.completeWithError(e);
            return emitter;
        } catch (IOException e) {
            emitter.completeWithError(e);
            return emitter;
        }

        AtomicReference<Disposable> subRef = new AtomicReference<>();
        Runnable cancel = () -> {
            Disposable d = subRef.get();
            if (d != null && !d.isDisposed()) {
                d.dispose();
            }
        };
        emitter.onTimeout(() -> {
            log.warn("SSE 超时 ({} ms)", SSE_TIMEOUT_MS);
            cancel.run();
            emitter.complete();
        });
        emitter.onCompletion(cancel);
        emitter.onError(e -> cancel.run());

        try {
            Disposable d = contentFlux.subscribe(
                    piece -> {
                        if (piece == null) {
                            return;
                        }
                        try {
                            emitter.send(SseEmitter.event().name("delta").data(piece));
                        } catch (IOException ex) {
                            log.debug("客户端断开或写失败，停止上游流: {}", ex.toString());
                            cancel.run();
                        } catch (IllegalStateException ex) {
                            log.debug("SseEmitter 已结束: {}", ex.toString());
                            cancel.run();
                        }
                    },
                    err -> {
                        if (err instanceof ResponseStatusException rse) {
                            try {
                                String body = this.objectMapper.writeValueAsString(Map.of(
                                        "code", "BAD_REQUEST",
                                        "message", rse.getReason() != null ? rse.getReason() : "参数错误"
                                ));
                                emitter.send(SseEmitter.event().name("error").data(body, MediaType.APPLICATION_JSON));
                            } catch (Exception writeEx) {
                                log.error("回写 SSE error 事件失败", writeEx);
                            }
                            emitter.complete();
                            return;
                        }
                        log.error("流式生成失败", err);
                        try {
                            String body = this.objectMapper.writeValueAsString(Map.of(
                                    "code", "LLM_UPSTREAM",
                                    "message", "大模型流式调用失败，请稍后再试"
                            ));
                            emitter.send(SseEmitter.event().name("error").data(body, MediaType.APPLICATION_JSON));
                        } catch (Exception writeEx) {
                            log.error("回写 SSE error 事件失败", writeEx);
                        }
                        emitter.complete();
                    },
                    () -> {
                        try {
                            emitter.send(SseEmitter.event().name("done").data("[DONE]"));
                        } catch (Exception ignored) {
                            // 正常结束
                        }
                        emitter.complete();
                    }
            );
            subRef.set(d);
        } catch (Exception e) {
            log.error("订阅流式响应失败", e);
            try {
                String body = this.objectMapper.writeValueAsString(Map.of(
                        "code", "INTERNAL_ERROR",
                        "message", "无法建立流"
                ));
                emitter.send(SseEmitter.event().name("error").data(body, MediaType.APPLICATION_JSON));
            } catch (Exception ex) {
                // ignore
            }
            emitter.complete();
        }
        return emitter;
    }
}
