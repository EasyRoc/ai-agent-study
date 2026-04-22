package com.aimodel.javademo.service;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

import com.aimodel.javademo.api.dto.ChatMessageItem;
import com.aimodel.javademo.api.dto.ChatRequest;
import com.aimodel.javademo.api.dto.ChatResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.SystemMessage;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Flux;

/**
 * 第 1 周第 3 天起：通过 Spring AI 的 {@link ChatClient} 做同步；第 1 周第 4 天起增加
 * {@link #streamContent(ChatRequest)} 流式，与 {@link #chat(ChatRequest)} 共用同一 {@link ChatModel} / 通义
 * 配置（application.yml 中 <code>spring.ai.dashscope</code>），无第二套 <code>baseUrl</code> / <code>api-key</code>。
 */
@Service
public class ChatLlmService {

    private static final Logger log = LoggerFactory.getLogger(ChatLlmService.class);

    private final ChatClient chatClient;

    @Value("${spring.ai.dashscope.chat.options.model:qwen-turbo}")
    private String configuredModel;

    public ChatLlmService(ChatModel chatModel) {
        this.chatClient = ChatClient.create(chatModel);
    }

    public ChatResponse chat(ChatRequest request) {
        List<Message> messages;
        try {
            messages = toSpringMessages(request);
        } catch (IllegalArgumentException e) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, e.getMessage());
        }
        try {
            String text = this.chatClient.prompt()
                    .messages(messages)
                    .call()
                    .content();
            if (text == null) {
                text = "";
            }
            return new ChatResponse(text, this.configuredModel);
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            log.error("ChatClient 同步调用 DashScope/通义 失败", e);
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "大模型服务调用失败，请稍后再试");
        }
    }

    /**
     * 第 1 周第 4 天：流式正文片段。调用方以 SSE 等方式写出；与同步路径共用同一条 DashScope/模型 配置链。
     */
    public Flux<String> streamContent(ChatRequest request) {
        List<Message> messages;
        try {
            messages = toSpringMessages(request);
        } catch (IllegalArgumentException e) {
            return Flux.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, e.getMessage()));
        }
        return this.chatClient.prompt()
                .messages(messages)
                .stream()
                .content();
    }

    public String getConfiguredModel() {
        return configuredModel;
    }

    private List<Message> toSpringMessages(ChatRequest request) {
        if (request.getMessages() != null && !request.getMessages().isEmpty()) {
            List<Message> out = new ArrayList<>();
            for (ChatMessageItem item : request.getMessages()) {
                out.add(toMessage(item));
            }
            return out;
        }
        if (request.getPrompt() == null) {
            throw new IllegalArgumentException("prompt 与 messages 不可同时为空");
        }
        return List.of(new UserMessage(request.getPrompt().trim()));
    }

    private Message toMessage(ChatMessageItem item) {
        String r = item.getRole() == null ? "" : item.getRole().trim().toLowerCase(Locale.ROOT);
        return switch (r) {
            case "system" -> new SystemMessage(item.getContent());
            case "user" -> new UserMessage(item.getContent());
            case "assistant" -> new AssistantMessage(item.getContent());
            default -> throw new IllegalArgumentException("不支持的 role: " + item.getRole() + "，请使用 system / user / assistant");
        };
    }
}
