package com.aimodel.javademo.api.dto;

import java.util.Map;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 第 2 周场景 A：从自然语言抽取意图与槽位；与 {@code structure-*.txt} 中约定的 JSON 字段一致，供 Spring AI
 * {@link org.springframework.ai.chat.client.ChatClient} 的 <strong>Structured Output</strong>（{@code .entity(...)}）反序列化。
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@JsonIgnoreProperties(ignoreUnknown = true)
public record IntentSlotsResult(
        @JsonProperty("intent")
        String intent,
        @JsonProperty("slots")
        Map<String, String> slots
) {
    public IntentSlotsResult {
        intent = intent == null ? "" : intent.trim();
        slots = slots == null ? Map.of() : Map.copyOf(slots);
    }
}
