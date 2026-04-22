package com.aimodel.javademo.api.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * 单条对话消息，配合 {@link ChatRequest#messages} 使用。role 常用：user / system / assistant。
 */
public class ChatMessageItem {

    @NotBlank(message = "role 不能为空")
    private String role;

    @NotBlank(message = "content 不能为空")
    private String content;

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }
}
