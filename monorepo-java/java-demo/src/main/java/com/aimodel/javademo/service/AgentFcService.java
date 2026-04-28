package com.aimodel.javademo.service;

import com.aimodel.javademo.api.dto.FcChatResponse;
import com.aimodel.javademo.tools.Week06AgentFcTools;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.ai.chat.model.ChatResponse;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.ai.model.tool.ToolCallingChatOptions;
import org.springframework.ai.tool.method.MethodToolCallbackProvider;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * 第 6 周：<code>knowledge_search</code> / <code>get_weather_mock</code> 等工具，由 DashScope FC 在多步内闭环；与 /api/v1/fc/chat（Week01 计算器）
 * **分开展示**两套 Tool 集。
 */
@Service
public class AgentFcService {

    private static final Logger log = LoggerFactory.getLogger(AgentFcService.class);

    private final ChatModel chatModel;
    private final MethodToolCallbackProvider toolProvider;

    @Value("${spring.ai.dashscope.chat.options.model:qwen-turbo}")
    private String configuredModel;

    public AgentFcService(ChatModel chatModel, Week06AgentFcTools week06AgentFcTools) {
        this.chatModel = chatModel;
        this.toolProvider = MethodToolCallbackProvider.builder()
                .toolObjects(week06AgentFcTools)
                .build();
    }

    public FcChatResponse invoke(String userPrompt) {
        try {
            ToolCallingChatOptions options = ToolCallingChatOptions.builder()
                    .toolCallbacks(this.toolProvider.getToolCallbacks())
                    .internalToolExecutionEnabled(true)
                    .build();
            Prompt prompt = new Prompt(new UserMessage(userPrompt), options);
            ChatResponse response = this.chatModel.call(prompt);
            String text = response.getResult().getOutput().getText();
            if (text == null) {
                text = "";
            }
            return new FcChatResponse(text, this.configuredModel);
        } catch (Exception e) {
            log.error("Agent FC 调用失败（建议 LLM_MODEL=qwen-plus）", e);
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "大模型或多步工具调用失败；请确认模型支持 FC（通义建议使用 qwen-plus 等）。"
            );
        }
    }
}
