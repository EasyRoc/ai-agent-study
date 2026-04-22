package com.aimodel.javademo.api.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

/** FC 终答 + 与同步接口一致带上当前配置的 model 名。 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class FcChatResponse {

    private String content;
    private String model;

    public FcChatResponse() {
    }

    public FcChatResponse(String content, String model) {
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
