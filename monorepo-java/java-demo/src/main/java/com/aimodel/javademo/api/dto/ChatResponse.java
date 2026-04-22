package com.aimodel.javademo.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * 同步补全/对话返回体。课表与周计划中称为 <strong>ChatResponse</strong>；与 Spring AI 的
 * {@code org.springframework.ai.chat.model.ChatResponse} 重名，故本类放在 {@code api.dto} 包，HTTP JSON 用此结构。
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ChatResponse {

    private String content;
    private String model;

    public ChatResponse() {
    }

    public ChatResponse(String content, String model) {
        this.content = content;
        this.model = model;
    }

    public String getContent() {
        return content;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }
}
