package com.aimodel.javademo.service;

import com.aimodel.javademo.api.dto.FcChatResponse;
import com.aimodel.javademo.tools.Week01DemoTools;

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
 * 使用 Spring AI {@link ToolCallingChatOptions#internalToolExecutionEnabled} 在<strong>单条</strong>
 * {@link ChatModel#call} 链路内由框架完成「模型 → 工具 → 再请求」的闭环；与手搓 messages 的 Python
 * {@code fc_min.py} 对照学习。
 */
@Service
public class FunctionCallingChatService {

    private static final Logger log = LoggerFactory.getLogger(FunctionCallingChatService.class);

    private final ChatModel chatModel;
    private final MethodToolCallbackProvider toolProvider;

    @Value("${spring.ai.dashscope.chat.options.model:qwen-turbo}")
    private String configuredModel;

    public FunctionCallingChatService(ChatModel chatModel, Week01DemoTools week01DemoTools) {
        this.chatModel = chatModel;
        this.toolProvider = MethodToolCallbackProvider.builder()
                .toolObjects(week01DemoTools)
                .build();
    }

    public FcChatResponse invoke(String userPrompt) {
        try {
            var options = ToolCallingChatOptions.builder()
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
            log.error("Function Calling 调用失败", e);
            throw new ResponseStatusException(
                    HttpStatus.BAD_GATEWAY,
                    "大模型或工具链调用失败；请确认模型支持 tools（通义可尝试在配置中使用 qwen-plus 等）"
            );
        }
    }
}
