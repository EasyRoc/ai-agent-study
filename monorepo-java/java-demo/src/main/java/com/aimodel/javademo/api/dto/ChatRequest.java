package com.aimodel.javademo.api.dto;

import java.util.List;

import jakarta.validation.Valid;
import jakarta.validation.constraints.AssertTrue;

/**
 * 第 1 周第 3 天 DTO：与 OpenAI/兼容端「多轮或单条」二选一，避免请求体过复杂。
 * <ul>
 *   <li>仅 <code>prompt</code>：等价于单轮 <code>user</code> 消息</li>
 *   <li>仅 <code>messages</code>：多轮（可含 system / user / assistant）</li>
 * </ul>
 * 不要同时传两者，也不要都为空（由 {@link #isExclusive()} 校验）。
 */
public class ChatRequest {

    @Valid
    private List<ChatMessageItem> messages;

    private String prompt;

    public List<ChatMessageItem> getMessages() {
        return messages;
    }

    public void setMessages(List<ChatMessageItem> messages) {
        this.messages = messages;
    }

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }

    @AssertTrue(message = "请仅提供非空 messages 或非空 prompt 之一，且不要同时传两者")
    public boolean isExclusive() {
        boolean hasMessages = messages != null && !messages.isEmpty();
        boolean hasPrompt = prompt != null && !prompt.isBlank();
        return hasMessages != hasPrompt;
    }
}
