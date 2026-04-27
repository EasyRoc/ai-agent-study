package com.aimodel.javademo.config;

import com.aimodel.javademo.api.dto.IntentSlotsResult;

import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver;

import org.springframework.ai.chat.model.ChatModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 第 2 周 L0：使用 {@link com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver} 作为 <strong>checkpointer</strong>，
 * 在 {@link ReactAgent} 中按 <code>RunnableConfig#threadId</code> 隔离多轮（与 java2ai 短期记忆文档一致）。<br>
 * 结构化输出由 <code>outputType(IntentSlotsResult.class)</code> 走 Agent 内建 schema/解析路径。
 */
@Configuration
public class StructureAgentConfiguration {

    @Bean
    public ReactAgent structureIntentReactAgent(
            ChatModel chatModel,
            StructureL0TrimmingHook l0TrimmingHook
    ) {
        return ReactAgent.builder()
                .name("week02-structure-intent")
                .model(chatModel)
                .systemPrompt("你是意图与槽位抽取器。稍后会通过 setSystemPrompt 注入完整 system 段。")
                .outputType(IntentSlotsResult.class)
                .saver(new MemorySaver())
                .hooks(l0TrimmingHook)
                .build();
    }
}
