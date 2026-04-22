package com.aimodel.javademo.web;

import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 第 0 周第 2 天：GET /api/v1/health/llm
 * 使用 Spring AI 核心接口 {@link ChatModel} 发「你好」探活（与 Python health_chat 语义一致）；
 * DashScope 的 {@link ChatModel} Bean 由 {@code spring-ai-alibaba-starter-dashscope} 自动注册。
 */
@RestController
@RequestMapping("/api/v1/health")
public class HealthLlmController {

    @Autowired
    private ChatModel chatModel;


    @GetMapping("/llm")
    public ResponseEntity<Map<String, Object>> healthLlm() {
        Map<String, Object> body = new LinkedHashMap<>();
        try {
            // Prompt 内一条用户消息，等价于「单轮补全/对话」一次
            ChatResponse response = this.chatModel.call(new Prompt(new UserMessage("你好")));
            // Spring AI 1.1+ 输出文本的取法（若你本地编译报错，按 IDE 补全 getOutput 的方法名即可）
            String reply = response.getResult().getOutput().getText();
            if (reply == null) {
                reply = "";
            }
            String preview = reply.length() > 200 ? reply.substring(0, 200) : reply;
            body.put("ok", true);
            body.put("preview", preview);
            body.put("length", reply.length());
            return ResponseEntity.ok(body);
        } catch (Exception e) {
            body.put("ok", false);
            body.put("error", e.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(body);
        }
    }
}
