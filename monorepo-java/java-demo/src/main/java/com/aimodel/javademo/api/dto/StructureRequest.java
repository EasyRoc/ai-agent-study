package com.aimodel.javademo.api.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * {@code POST /api/v1/structure} 请求体：用户原话 + 可选会话（L0）。
 */
public class StructureRequest {

    /**
     * 待结构化的用户说法（单条本轮输入）。
     */
    @NotBlank
    private String raw;

    /**
     * 可选；不传则服务端生成新 sessionId 并在响应中返回，便于客户端多轮沿用。
     */
    private String sessionId;

    public String getRaw() {
        return raw;
    }

    public void setRaw(String raw) {
        this.raw = raw;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
}
