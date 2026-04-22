package com.aimodel.javademo.api.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * FC 单轮入参：自然语言问题，由模型决定是否调用本仓库注册的 @Tool。
 */
public class FcChatRequest {

    @NotBlank(message = "prompt 不能为空")
    private String prompt;

    public String getPrompt() {
        return prompt;
    }

    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }
}
